"""
Dependency injection container for the application.

This module sets up the dependency injection container that provides
all services needed by the application. It uses Python's built-in
functions and a registry pattern rather than a full DI framework to
keep things simple but maintainable.
"""

from typing import Any, Dict, Optional, Type

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.publishing import PublishingInterface
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.infrastructure.config.settings import settings


class Container:
    """
    Dependency injection container.

    This container manages all service instances and their dependencies,
    providing a clean way to access services throughout the application.
    """

    def __init__(self):
        """Initialize the container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._service_registry: Dict[str, Dict[str, Type]] = {
            "storage": {},
            "ai": {},
            "publishing": {},
        }

    def register_factory(self, service_name: str, factory: callable) -> None:
        """
        Register a factory function for a service.

        Args:
            service_name: Name of the service
            factory: Factory function that creates the service
        """
        self._factories[service_name] = factory

    def register_service_implementation(
        self, interface_name: str, implementation_name: str, implementation_type: Type
    ) -> None:
        """
        Register a service implementation for an interface.

        Args:
            interface_name: Name of the interface (e.g., "storage")
            implementation_name: Name of the implementation (e.g., "gcs")
            implementation_type: Type of the implementation class
        """
        if interface_name not in self._service_registry:
            self._service_registry[interface_name] = {}

        self._service_registry[interface_name][
            implementation_name
        ] = implementation_type

    def get(self, service_name: str, implementation: Optional[str] = None) -> Any:
        """
        Get a service instance.

        Args:
            service_name: Name of the service
            implementation: Optional name of the specific implementation to use
                            If not provided, the default implementation will be used

        Returns:
            The service instance

        Raises:
            ValueError: If the service is not registered
        """
        # If specific implementation is requested and it's in a registry
        if implementation and service_name in self._service_registry:
            registry = self._service_registry[service_name]
            if implementation not in registry:
                raise ValueError(
                    f"Implementation '{implementation}' not found for service '{service_name}'"
                )

            implementation_type = registry[implementation]
            service_key = f"{service_name}_{implementation}"

            if service_key not in self._services:
                self._services[service_key] = self._create_service(implementation_type)

            return self._services[service_key]

        # Normal service lookup
        if service_name not in self._services:
            if service_name not in self._factories:
                raise ValueError(f"Service '{service_name}' not registered")

            self._services[service_name] = self._factories[service_name]()

        return self._services[service_name]

    def _create_service(self, service_type: Type) -> Any:
        """
        Create a service instance.

        This method handles dependency injection for service constructors.

        Args:
            service_type: Type of the service to create

        Returns:
            The service instance
        """
        # This is a simple implementation that assumes the constructor
        # doesn't need any dependencies. In a real application, you would
        # inspect the constructor signature and provide the necessary dependencies.
        return service_type()


# Create storage adapter factory
def storage_adapter_factory() -> StorageInterface:
    """
    Factory function for storage adapter.

    Returns:
        An instance of a StorageInterface implementation based on settings
    """
    if settings.storage.use_local_storage:
        # Import here to avoid circular imports
        from video_processor.adapters.storage.local import LocalStorageAdapter

        return LocalStorageAdapter(root_path=settings.storage.local_storage_path)
    else:
        # Import here to avoid circular imports
        from video_processor.adapters.storage.gcs import GCSStorageAdapter

        return GCSStorageAdapter(
            bucket_name=settings.storage.gcs_bucket,
            input_prefix=settings.storage.gcs_input_prefix,
            output_prefix=settings.storage.gcs_output_prefix,
        )


# Create AI service factory
def ai_service_factory() -> AIServiceInterface:
    """
    Factory function for AI service.

    Returns:
        An instance of an AIServiceInterface implementation based on settings
    """
    if settings.ai.use_vertex_ai:
        # Import here to avoid circular imports
        from video_processor.adapters.ai.vertex_ai import VertexAIAdapter

        return VertexAIAdapter(
            project=settings.ai.vertex_ai_project,
            location=settings.ai.vertex_ai_location,
            model=settings.ai.vertex_ai_model,
        )
    else:
        # Import here to avoid circular imports
        from video_processor.adapters.ai.gemini import GeminiAIAdapter

        return GeminiAIAdapter(
            api_key=settings.ai.gemini_api_key, model=settings.ai.gemini_model
        )


# Create YouTube adapter factory
def youtube_adapter_factory() -> PublishingInterface:
    """
    Factory function for YouTube adapter.

    Returns:
        An instance of a PublishingInterface implementation for YouTube
    """
    # Import here to avoid circular imports
    from video_processor.adapters.publishing.youtube import YouTubeAdapter

    return YouTubeAdapter(
        client_secrets_file=settings.youtube.client_secrets_file,
        token_file=settings.youtube.token_file,
        scopes=settings.youtube.scopes,
    )


# Create and configure the container
container = Container()

# Register factories
container.register_factory("storage", storage_adapter_factory)
container.register_factory("ai", ai_service_factory)
container.register_factory("youtube", youtube_adapter_factory)

# When we implement the actual services, we'll also register implementations:
# container.register_service_implementation("storage", "gcs", GCSStorageAdapter)
# container.register_service_implementation("storage", "local", LocalStorageAdapter)
# container.register_service_implementation("ai", "gemini", GeminiAIAdapter)
# container.register_service_implementation("ai", "vertex", VertexAIAdapter)
# container.register_service_implementation("publishing", "youtube", YouTubeAdapter)
