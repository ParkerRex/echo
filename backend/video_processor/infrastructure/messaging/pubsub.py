"""
Google Cloud Pub/Sub implementation of the messaging interface.
"""

import json
import logging
import os
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.cloud.pubsub_v1.subscriber.message import Message

from video_processor.application.interfaces.messaging import MessageHandlerInterface
from video_processor.domain.exceptions import MessagingError


class PubSubAdapter(MessageHandlerInterface):
    """
    Google Cloud Pub/Sub implementation of the messaging interface.

    This adapter provides asynchronous messaging capabilities using
    Google Cloud Pub/Sub.
    """

    def __init__(self, project_id: str, client_id: Optional[str] = None):
        """
        Initialize the Pub/Sub adapter.

        Args:
            project_id: Google Cloud project ID
            client_id: Optional client ID for subscription naming
        """
        self.project_id = project_id
        self.client_id = client_id or f"client-{os.getpid()}"

        # Initialize clients
        self.publisher = PublisherClient()
        self.subscriber = SubscriberClient()

        # Track active subscriptions
        self._subscriptions = {}
        self._subscription_threads = {}
        self._running = True

        # Logger
        self.logger = logging.getLogger(__name__)

    def _get_topic_path(self, topic: str) -> str:
        """Get the full topic path."""
        return self.publisher.topic_path(self.project_id, topic)

    def _get_subscription_path(self, topic: str) -> str:
        """Get a unique subscription path for this client."""
        subscription_id = f"{topic}-{self.client_id}"
        return self.subscriber.subscription_path(self.project_id, subscription_id)

    def publish(self, topic: str, message: Dict[str, Any]) -> str:
        """
        Publish a message to a topic.

        Args:
            topic: The topic to publish to
            message: The message payload as a dictionary

        Returns:
            The published message ID

        Raises:
            MessagingError: If publishing fails
        """
        try:
            # Ensure topic exists
            topic_path = self._get_topic_path(topic)
            self._ensure_topic_exists(topic)

            # Convert message to bytes
            data = json.dumps(message).encode("utf-8")

            # Publish message
            future = self.publisher.publish(topic_path, data)
            message_id = future.result()  # Wait for publishing to complete

            self.logger.debug(f"Published message {message_id} to {topic}")
            return message_id
        except Exception as e:
            error_msg = f"Failed to publish message to {topic}: {str(e)}"
            self.logger.error(error_msg)
            raise MessagingError(error_msg) from e

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to a topic with a callback function.

        Args:
            topic: The topic to subscribe to
            callback: A function to call when a message is received

        Raises:
            MessagingError: If subscription fails
        """
        try:
            # Ensure topic exists
            self._ensure_topic_exists(topic)

            # Get paths
            topic_path = self._get_topic_path(topic)
            subscription_path = self._get_subscription_path(topic)

            # Create subscription if it doesn't exist
            try:
                self.subscriber.create_subscription(
                    request={"name": subscription_path, "topic": topic_path}
                )
                self.logger.info(f"Created subscription {subscription_path}")
            except AlreadyExists:
                self.logger.debug(f"Subscription {subscription_path} already exists")

            # Define callback wrapper
            def callback_wrapper(message: Message) -> None:
                try:
                    # Parse message data
                    data = json.loads(message.data.decode("utf-8"))

                    # Call user callback
                    callback(data)

                    # Acknowledge message
                    message.ack()
                except Exception as e:
                    self.logger.error(f"Error processing message: {str(e)}")
                    message.nack()

            # Subscribe and start listening
            self._subscriptions[topic] = self.subscriber.subscribe(
                subscription_path, callback_wrapper
            )

            # Start subscriber in a separate thread
            thread = threading.Thread(
                target=self._run_subscriber, args=(topic,), daemon=True
            )
            thread.start()
            self._subscription_threads[topic] = thread

            self.logger.info(f"Subscribed to topic {topic}")
        except Exception as e:
            error_msg = f"Failed to subscribe to {topic}: {str(e)}"
            self.logger.error(error_msg)
            raise MessagingError(error_msg) from e

    def _run_subscriber(self, topic: str) -> None:
        """Run the subscriber in a loop with error handling."""
        subscription = self._subscriptions.get(topic)
        if not subscription:
            return

        while self._running and topic in self._subscriptions:
            try:
                # Blocking call that processes messages
                subscription.result()
            except Exception as e:
                if self._running:  # Only log if we're still supposed to be running
                    self.logger.error(f"Subscription error for {topic}: {str(e)}")
                    time.sleep(1)  # Avoid busy-waiting on repeated errors

    def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from a topic.

        Args:
            topic: The topic to unsubscribe from

        Returns:
            True if unsubscribed successfully, False otherwise

        Raises:
            MessagingError: If unsubscription fails
        """
        try:
            # Check if we have an active subscription
            if topic not in self._subscriptions:
                return False

            # Stop the subscription
            self._subscriptions[topic].cancel()
            del self._subscriptions[topic]

            # Clean up the subscription resource
            subscription_path = self._get_subscription_path(topic)
            self.subscriber.delete_subscription(
                request={"subscription": subscription_path}
            )

            self.logger.info(f"Unsubscribed from topic {topic}")
            return True
        except Exception as e:
            error_msg = f"Failed to unsubscribe from {topic}: {str(e)}"
            self.logger.error(error_msg)
            raise MessagingError(error_msg) from e

    def pull_messages(self, topic: str, max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Pull messages from a topic without a subscription.

        Args:
            topic: The topic to pull messages from
            max_messages: The maximum number of messages to pull

        Returns:
            A list of message payloads

        Raises:
            MessagingError: If message pulling fails
        """
        try:
            # Ensure topic exists
            self._ensure_topic_exists(topic)

            # Create a temporary subscription for pulling
            temp_subscription_id = f"temp-pull-{self.client_id}-{int(time.time())}"
            temp_subscription_path = self.subscriber.subscription_path(
                self.project_id, temp_subscription_id
            )

            topic_path = self._get_topic_path(topic)

            # Create temporary subscription
            try:
                self.subscriber.create_subscription(
                    request={"name": temp_subscription_path, "topic": topic_path}
                )
            except AlreadyExists:
                # If it somehow already exists, continue using it
                pass

            # Pull messages
            try:
                response = self.subscriber.pull(
                    request={
                        "subscription": temp_subscription_path,
                        "max_messages": max_messages,
                    }
                )

                # Process messages
                messages = []
                ack_ids = []

                for received_message in response.received_messages:
                    # Parse message
                    data = json.loads(received_message.message.data.decode("utf-8"))
                    messages.append(data)
                    ack_ids.append(received_message.ack_id)

                # Acknowledge all messages
                if ack_ids:
                    self.subscriber.acknowledge(
                        request={
                            "subscription": temp_subscription_path,
                            "ack_ids": ack_ids,
                        }
                    )

                return messages
            finally:
                # Clean up temporary subscription
                try:
                    self.subscriber.delete_subscription(
                        request={"subscription": temp_subscription_path}
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to delete temporary subscription: {str(e)}"
                    )
        except Exception as e:
            error_msg = f"Failed to pull messages from {topic}: {str(e)}"
            self.logger.error(error_msg)
            raise MessagingError(error_msg) from e

    def ack_message(self, topic: str, message_id: str) -> bool:
        """
        Acknowledge a message as processed.

        Note: This is a no-op for the Pub/Sub adapter as messages are
        automatically acknowledged in the callback.

        Args:
            topic: The topic the message was from
            message_id: The ID of the message to acknowledge

        Returns:
            True (always succeeds as a no-op)
        """
        # This is a no-op since we auto-ack in the callback
        self.logger.debug(
            f"ack_message is a no-op for Pub/Sub adapter (topic: {topic}, message: {message_id})"
        )
        return True

    def create_topic(self, topic: str) -> bool:
        """
        Create a new topic if it doesn't exist.

        Args:
            topic: The topic to create

        Returns:
            True if created or already exists, False otherwise

        Raises:
            MessagingError: If topic creation fails
        """
        return self._ensure_topic_exists(topic)

    def _ensure_topic_exists(self, topic: str) -> bool:
        """Ensure that a topic exists, creating it if necessary."""
        try:
            topic_path = self._get_topic_path(topic)

            try:
                self.publisher.get_topic(request={"topic": topic_path})
                return True  # Topic already exists
            except NotFound:
                # Topic doesn't exist, create it
                self.publisher.create_topic(request={"name": topic_path})
                self.logger.info(f"Created topic {topic_path}")
                return True
        except Exception as e:
            error_msg = f"Failed to ensure topic {topic} exists: {str(e)}"
            self.logger.error(error_msg)
            raise MessagingError(error_msg) from e

    def delete_topic(self, topic: str) -> bool:
        """
        Delete a topic.

        Args:
            topic: The topic to delete

        Returns:
            True if deleted successfully, False otherwise

        Raises:
            MessagingError: If topic deletion fails
        """
        try:
            topic_path = self._get_topic_path(topic)

            try:
                self.publisher.delete_topic(request={"topic": topic_path})
                self.logger.info(f"Deleted topic {topic_path}")
                return True
            except NotFound:
                # Topic doesn't exist
                return False
        except Exception as e:
            error_msg = f"Failed to delete topic {topic}: {str(e)}"
            self.logger.error(error_msg)
            raise MessagingError(error_msg) from e

    def close(self) -> None:
        """
        Close all connections and clean up resources.
        """
        self._running = False

        # Cancel all subscriptions
        for topic in list(self._subscriptions.keys()):
            try:
                self.unsubscribe(topic)
            except Exception as e:
                self.logger.warning(f"Error while unsubscribing from {topic}: {str(e)}")

        # Close clients
        self.subscriber.close()

        self.logger.info("Pub/Sub adapter closed")
