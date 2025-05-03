"""
Interfaces for message handling and event-driven communication.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class MessageHandlerInterface(ABC):
    """
    Interface for handling asynchronous messaging between components.

    This interface defines methods for publishing messages to topics and
    subscribing to topics to receive messages.
    """

    @abstractmethod
    def publish(self, topic: str, message: Dict[str, Any]) -> str:
        """
        Publish a message to a topic.

        Args:
            topic: The topic to publish to
            message: The message payload as a dictionary

        Returns:
            A message ID or reference for the published message

        Raises:
            MessagingError: If publishing fails
        """
        pass

    @abstractmethod
    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to a topic with a callback function.

        Args:
            topic: The topic to subscribe to
            callback: A function to call when a message is received

        Raises:
            MessagingError: If subscription fails
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def pull_messages(self, topic: str, max_messages: int = 10) -> list[Dict[str, Any]]:
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
        pass

    @abstractmethod
    def ack_message(self, topic: str, message_id: str) -> bool:
        """
        Acknowledge a message as processed.

        Args:
            topic: The topic the message was from
            message_id: The ID of the message to acknowledge

        Returns:
            True if acknowledged successfully, False otherwise

        Raises:
            MessagingError: If acknowledgment fails
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
