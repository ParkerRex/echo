"""
Dependency injection container.

This module provides a dependency injection container that manages the
creation and lifecycle of service objects in the application. It helps to
decouple object creation from object usage, enabling better testability
and flexibility.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Type, TypeVar

from google.cloud import storage
from vertexai.preview.generative_models import GenerativeModel

from video_processor.adapters.ai.gemini import GeminiAIAdapter
from video_processor.adapters.publishing.youtube import YouTubeAdapter
from video_processor.adapters.storage.gcs import GCSStorageAdapter
from video_processor.adapters.storage.local import LocalStorageAdapter
from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.publishing import PublishingInterface
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.application.services.metadata import MetadataService
from video_processor.application.services.subtitle import SubtitleService
from video_processor.application.services.transcription import TranscriptionService
from video_processor.application.services.video_processor import VideoProcessorService
from video_processor.infrastructure.repositories.job_repository import JobRepository
from video_processor.infrastructure.repositories.video_repository import VideoRepository

# Type variable for generics
T = TypeVar("T")


class Container:
    """
    Dependency injection container.

    This container manages the creation, configuration, and lifetime of
    service objects, providing a central registry for application components.
    """

    def __init__(self):
        """Initialize an empty container."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, callable] = {}
        self._singletons: Dict[Type, bool] = {}

    def register(
        self, service_type: Type[T], factory: callable, singleton: bool = True
    ) -> None:
        """
        Register a service with the container.

        Args:
            service_type: The type/interface for the service
            factory: A factory function that creates an instance of the service
            singleton: Whether the service should be a singleton
        """
        self._factories[service_type] = factory
        self._singletons[service_type] = singleton

        # Clear existing instance if re-registering
        if service_type in self._services:
            del self._services[service_type]

    def get(self, service_type: Type[T]) -> T:
        """
        Get a service instance from the container.

        Args:
            service_type: The type/interface of the service to retrieve

        Returns:
            An instance of the requested service

        Raises:
            KeyError: If the service type is not registered
        """
        # Return existing instance for singletons
        if service_type in self._services and self._singletons.get(service_type, True):
            return self._services[service_type]

        # Create new instance using factory
        if service_type not in self._factories:
            raise KeyError(f"Service {service_type.__name__} not registered")

        factory = self._factories[service_type]
        instance = factory()

        # Cache singleton instances
        if self._singletons.get(service_type, True):
            self._services[service_type] = instance

        return instance

    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """
        Register an existing instance with the container.

        Args:
            service_type: The type/interface for the service
            instance: An existing instance to use
        """
        self._services[service_type] = instance
        self._singletons[service_type] = True


def create_container(testing: bool = False, local_storage: bool = False) -> Container:
    """
    Create and configure a dependency injection container.

    Args:
        testing: Whether the container is for testing
        local_storage: Whether to use local storage instead of GCS

    Returns:
        A configured Container instance
    """
    container = Container()
    thread_pool = ThreadPoolExecutor(max_workers=10)

    # Register infrastructure services
    if testing:
        # Use mock implementations for testing
        from unittest.mock import MagicMock

        container.register_instance(storage.Client, MagicMock())
    else:
        # Use real implementations for production
        container.register(storage.Client, lambda: storage.Client())

    # Register storage adapter
    if local_storage or testing:
        local_dir = os.environ.get("LOCAL_OUTPUT_DIR", "./output")
        container.register(
            StorageInterface,
            lambda: LocalStorageAdapter(base_dir=local_dir, executor=thread_pool),
        )
    else:
        container.register(
            StorageInterface,
            lambda: GCSStorageAdapter(
                client=container.get(storage.Client), executor=thread_pool
            ),
        )

    # Register AI service adapter
    if testing:
        from unittest.mock import MagicMock

        mock_ai = MagicMock(spec=AIServiceInterface)
        mock_ai.generate_content.return_value = "Mock AI response"
        container.register_instance(AIServiceInterface, mock_ai)
    else:
        # Configure Vertex AI
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "default-project")
        region = os.environ.get("REGION", "us-east1")
        model_name = os.environ.get("MODEL", "gemini-2.0-flash-001")

        import vertexai

        vertexai.init(project=project_id, location=region)

        container.register(GenerativeModel, lambda: GenerativeModel(model_name))

        container.register(
            AIServiceInterface,
            lambda: GeminiAIAdapter(model=container.get(GenerativeModel)),
        )

    # Register YouTube adapter
    container.register(
        PublishingInterface,
        lambda: YouTubeAdapter(
            storage=container.get(StorageInterface),
            credentials_path=os.environ.get(
                "YOUTUBE_CREDENTIALS", "credentials/youtube_credentials.json"
            ),
        ),
    )

    # Register repositories
    container.register(
        JobRepository, lambda: JobRepository(storage=container.get(StorageInterface))
    )

    container.register(
        VideoRepository,
        lambda: VideoRepository(storage=container.get(StorageInterface)),
    )

    # Register application services
    container.register(
        TranscriptionService,
        lambda: TranscriptionService(ai_service=container.get(AIServiceInterface)),
    )

    container.register(
        SubtitleService,
        lambda: SubtitleService(ai_service=container.get(AIServiceInterface)),
    )

    container.register(
        MetadataService,
        lambda: MetadataService(ai_service=container.get(AIServiceInterface)),
    )

    # Register the main processor service
    container.register(
        VideoProcessorService,
        lambda: VideoProcessorService(
            storage=container.get(StorageInterface),
            transcription_service=container.get(TranscriptionService),
            subtitle_service=container.get(SubtitleService),
            metadata_service=container.get(MetadataService),
            publishing_service=container.get(PublishingInterface),
            job_repository=container.get(JobRepository),
            video_repository=container.get(VideoRepository),
        ),
    )

    return container
