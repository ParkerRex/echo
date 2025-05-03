"""
Messaging infrastructure for event-driven communication.
"""

from video_processor.infrastructure.messaging.handlers import (
    handle_processing_complete,
    handle_publishing_complete,
    handle_video_uploaded,
    register_handlers,
)
from video_processor.infrastructure.messaging.pubsub import PubSubAdapter
