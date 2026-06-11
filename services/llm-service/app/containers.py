from dependency_injector import containers, providers
from app.backends.openai_backend import OpenAIBackend
from app.services.generation import GenerationService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.api.v1.routes_generate"]
    )

    llm_backend = providers.Singleton(OpenAIBackend)

    generation_service = providers.Factory(
        GenerationService,
        backend=llm_backend,
    )
