from fastapi import HTTPException, status

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.world_repository import WorldRepository
from app.clients.rag_client import RagClient  # ← добавить


class DocumentService:

    def __init__(
        self,
        document_repository: DocumentRepository,
        world_repository: WorldRepository,
        rag_client: RagClient,  # ← добавить
    ) -> None:
        self._doc_repo = document_repository
        self._world_repo = world_repository
        self._rag = rag_client  # ← добавить

    async def _check_world_access(self, world_id: int, user_id: int) -> None:
        world = await self._world_repo.get_by_id(world_id)
        if not world or world.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found",
            )

    async def create_document(
        self,
        world_id: int,
        user_id: int,
        title: str,
        content: str,
        doc_type: str,
    ) -> Document:
        await self._check_world_access(world_id, user_id)
        doc = await self._doc_repo.create(
            world_id=world_id,
            title=title,
            content=content,
            doc_type=doc_type,
            is_indexed=False,
        )

        # Индексируем сразу после создания
        try:
            await self._rag.ingest(
                document_id=doc.id,
                world_id=world_id,
                user_id=user_id,
                doc_type=doc_type,
                content=content,
            )
            await self._doc_repo.update(doc.id, is_indexed=True)  # ← помечаем
            doc.is_indexed = True
        except Exception as e:
            print(f"[RAG] ingest failed for doc {doc.id}: {e}")
            # is_indexed остаётся False — можно переиндексировать позже

        return doc

    async def get_documents(
            self, world_id: int, user_id: int, limit: int = 20, offset: int = 0
    ) -> tuple[list[Document], int]:
        await self._check_world_access(world_id, user_id)
        items = await self._doc_repo.get_by_world_id(world_id, limit=limit, offset=offset)
        total = await self._doc_repo.count_by_world(world_id)
        return items, total

    async def get_document(
        self, world_id: int, document_id: int, user_id: int
    ) -> Document:
        await self._check_world_access(world_id, user_id)
        doc = await self._doc_repo.get_by_id(document_id)
        if not doc or doc.world_id != world_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        return doc

    async def update_document(
        self,
        world_id: int,
        document_id: int,
        user_id: int,
        **kwargs,
    ) -> Document:
        doc = await self.get_document(world_id, document_id, user_id)
        if "content" in kwargs or "title" in kwargs:
            kwargs["is_indexed"] = False

        updated = await self._doc_repo.update(doc.id, **kwargs)

        # Переиндексируем если изменился контент
        if "content" in kwargs:
            try:
                await self._rag.ingest(
                    document_id=updated.id,
                    world_id=updated.world_id,
                    user_id=user_id,
                    doc_type=updated.doc_type,
                    content=updated.content,
                )
                await self._doc_repo.update(updated.id, is_indexed=True)
                updated.is_indexed = True
            except Exception as e:
                print(f"[RAG] re-ingest failed for doc {updated.id}: {e}")

        return updated

    async def delete_document(
            self, world_id: int, document_id: int, user_id: int
    ) -> None:
        doc = await self.get_document(world_id, document_id, user_id)
        try:
            await self._rag.delete_document(doc.id)
        except Exception as e:
            print(f"[RAG] delete failed for doc {doc.id}: {e}")
        await self._doc_repo.delete(doc.id)

    async def get_unindexed(self, world_id: int, user_id: int) -> list[Document]:
        await self._check_world_access(world_id, user_id)
        return await self._doc_repo.get_unindexed_by_world(world_id)

