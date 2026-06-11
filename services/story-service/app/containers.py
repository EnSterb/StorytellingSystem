from dependency_injector import containers, providers
from app.clients.rag_client import RagClient
from app.clients.llm_client import LLMClient


class Container(containers.DeclarativeContainer):
    rag_client = providers.Singleton(RagClient)
    llm_client = providers.Singleton(LLMClient)
