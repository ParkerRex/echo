"""
Enumeration types used throughout the video processing system.

This module defines enumeration classes used to represent fixed sets of values
in a type-safe manner, such as processing status states. Using enums instead of
string literals improves type safety and code readability.

Usage:
    from apps.core.models.enums import ProcessingStatus

    # Create a new job with pending status
    job = VideoJobModel(status=ProcessingStatus.PENDING)

    # Check job status
    if job.status == ProcessingStatus.COMPLETED:
        print("Processing is complete!")
"""

from enum import Enum, auto


class ProcessingStatus(str, Enum):
    """
    Enumeration of possible video processing job statuses.

    This enum inherits from str to allow for easy serialization to/from databases
    and JSON, while still providing type safety and enumeration benefits.

    Attributes:
        PENDING: Job has been created but processing has not started.
        PROCESSING: Job is currently being processed.
        COMPLETED: Job has completed successfully.
        FAILED: Job processing failed with an error.
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
