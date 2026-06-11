from app.clients.rag_client import RagClient
from app.clients.llm_client import LLMClient
from app.services.session_manager import SessionManager
from app.models.message import RoleEnum
from app.models.session import SessionModeEnum

# Каждые N сообщений пересчитываем summary сессии
SUMMARY_INTERVAL = 10
# Максимум попыток rewrite если consistency check провалился
MAX_REWRITE_ATTEMPTS = 2


class ChatService:
    def __init__(
        self,
        session_manager: SessionManager,
        rag_client: RagClient,
        llm_client: LLMClient,
    ) -> None:
        self._manager = session_manager
        self._rag = rag_client
        self._llm = llm_client

    # ─────────────────────────────────────────────
    #  Построение инструкции режима (без изменений)
    # ─────────────────────────────────────────────

    async def _build_mode_instruction(self, session) -> str:
        if session.mode == SessionModeEnum.narrator:
            return (
                "Ты выступаешь в роли рассказчика настольной ролевой игры. "
                "Описываешь мир, события, NPC и последствия действий героя. "
                "Говори от третьего лица или как ведущий, не беря на себя роль игрока."
            )
        if session.mode == SessionModeEnum.player:
            if session.character_name:
                return (
                    f"Ты играешь за персонажа по имени {session.character_name}. "
                    "Отвечай строго от его лица, в первом лице, как этот герой. "
                    "Передавай его мысли, мотивацию и речь. "
                    "Не описывай действия ведущего и мира, только реакцию персонажа."
                )
            return (
                "Ты играешь за персонажа. Отвечай от первого лица, как этот герой. "
                "Передавай его мысли, мотивацию и речь. "
                "Не описывай действия ведущего и мира, только реакцию персонажа."
            )
        return ""

    # ─────────────────────────────────────────────
    #  НОВОЕ: Summary — сжатое состояние истории
    # ─────────────────────────────────────────────

    async def _rebuild_summary(self, session_id: int, user_id: int) -> str:
        """
        Сжимает последние 20 сообщений в 3-5 предложений.
        Вызывается каждые SUMMARY_INTERVAL сообщений.
        """
        history = await self._manager.get_history(
            session_id=session_id,
            user_id=user_id,
            last_n=20,
        )
        history_text = "\n".join(
            f"{m.role.value}: {m.content}" for m in history
        )
        return await self._llm.generate(
            system_prompt=(
                "Ты ведёшь журнал сюжета. "
                "Сожми историю в 3-5 предложений: "
                "ключевые события, статус персонажей, незакрытые конфликты. "
                "Только факты, без художественного стиля."
            ),
            history=[{"role": "user", "content": history_text}],
        )

    # ─────────────────────────────────────────────
    #  НОВОЕ: Plot progression — движется ли сюжет
    # ─────────────────────────────────────────────

    async def _check_plot_progression(
        self,
        summary: str,
        last_answer: str,
    ) -> bool:
        """
        Возвращает True если сюжет продвигается вперёд.
        False — если модель повторяет уже сказанное или топчется на месте.
        """
        if not summary:
            return True  # нет истории для сравнения — всё ок

        result = await self._llm.generate(
            system_prompt=(
                "Ты аналитик нарратива. Отвечай ТОЛЬКО одним словом: 'yes' или 'no'.\n\n"
                "Состояние истории до этой сцены:\n" + summary
            ),
            history=[{
                "role": "user",
                "content": (
                    f"Новая сцена:\n{last_answer}\n\n"
                    "Продвигает ли эта сцена историю вперёд, "
                    "или она повторяет уже известное и не добавляет ничего нового?"
                ),
            }],
        )
        return "yes" in result.strip().lower()

    # ─────────────────────────────────────────────
    #  НОВОЕ: Consistency check — соответствие канону
    # ─────────────────────────────────────────────

    async def _check_consistency(
        self,
        world_context: str,
        answer: str,
    ) -> list[str]:
        """
        Проверяет ответ на противоречия с фактами мира.
        Возвращает список нарушений или пустой список если всё ок.
        """
        if not world_context:
            return []

        result = await self._llm.generate(
            system_prompt=(
                "Ты редактор лора. Проверяй текст строго по фактам мира.\n\n"
                "Факты и правила мира:\n" + world_context
            ),
            history=[{
                "role": "user",
                "content": (
                    f"Текст сцены:\n{answer}\n\n"
                    "Перечисли все противоречия с фактами мира (если есть). "
                    "Если противоречий нет — ответь ровно одним словом: OK"
                ),
            }],
        )
        if result.strip().upper() == "OK":
            return []
        return [result.strip()]

    # ─────────────────────────────────────────────
    #  НОВОЕ: Rewrite — перегенерация с учётом ошибок
    # ─────────────────────────────────────────────

    async def _rewrite_answer(
        self,
        system_prompt: str,
        history: list[dict],
        bad_answer: str,
        violations: list[str],
        stale: bool,
    ) -> str:
        """
        Перегенерирует ответ с указанием конкретных проблем.
        violations — список нарушений канона.
        stale — True если сюжет не двигался вперёд.
        """
        issues: list[str] = []
        if violations:
            issues.append("Нарушения канона мира:\n" + "\n".join(f"- {v}" for v in violations))
        if stale:
            issues.append(
                "Сюжет не продвигается: сцена повторяет уже известное. "
                "Введи новое событие, поворот или раскрой незакрытый конфликт."
            )

        correction_note = (
            "ВАЖНО — предыдущий вариант сцены содержал ошибки:\n"
            + "\n".join(issues)
            + "\n\nНапиши сцену заново, исправив все указанные проблемы."
        )

        rewrite_history = history + [
            {"role": "assistant", "content": bad_answer},
            {"role": "user", "content": correction_note},
        ]

        return await self._llm.generate(
            system_prompt=system_prompt,
            history=rewrite_history,
        )

    # ─────────────────────────────────────────────
    #  Основной метод chat (дополнен)
    # ─────────────────────────────────────────────

    async def chat(
        self,
        session_id: int,
        user_id: int,
        user_message: str,
    ) -> str:
        session = await self._manager.get_session(session_id, user_id)

        await self._manager.append_message(
            session_id=session_id,
            user_id=user_id,
            role=RoleEnum.user,
            content=user_message,
        )

        # RAG: получаем контекст + id чанков для трейсабилити
        world_context = ""
        chunk_ids: list[int] = []
        if session.world_id:
            world_context, chunk_ids = await self._rag.retrieve_context(
                query=user_message,
                world_id=session.world_id,
            )

        mode_instruction = await self._build_mode_instruction(session)

        # НОВОЕ: подключаем summary к system_prompt если есть
        system_prompt_parts = [mode_instruction]
        if session.summary:
            system_prompt_parts.append(
                "Краткое состояние истории до этого момента:\n" + session.summary
            )
        if world_context:
            system_prompt_parts.append(world_context)
        system_prompt = "\n\n".join(p for p in system_prompt_parts if p)

        history_messages = await self._manager.get_history(
            session_id=session_id,
            user_id=user_id,
            last_n=10,
        )
        history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in history_messages
        ]

        # Генерация + цикл проверки и rewrite
        answer = await self._llm.generate(
            system_prompt=system_prompt,
            history=history,
        )

        for _ in range(MAX_REWRITE_ATTEMPTS):
            violations = await self._check_consistency(world_context, answer)
            is_progressing = await self._check_plot_progression(session.summary, answer)

            if not violations and is_progressing:
                break  # всё ок — выходим из цикла

            answer = await self._rewrite_answer(
                system_prompt=system_prompt,
                history=history,
                bad_answer=answer,
                violations=violations,
                stale=not is_progressing,
            )

        # Сохраняем ответ с chunk_ids
        await self._manager.append_message(
            session_id=session_id,
            user_id=user_id,
            role=RoleEnum.assistant,
            content=answer,
            used_chunks=",".join(str(i) for i in chunk_ids) if chunk_ids else None,
        )

        # НОВОЕ: пересчитываем summary каждые SUMMARY_INTERVAL сообщений
        msg_count = await self._manager.count_messages(session_id)
        if msg_count % SUMMARY_INTERVAL == 0:
            new_summary = await self._rebuild_summary(session_id, user_id)
            await self._manager.update_summary(session_id, new_summary)

        return answer

    # ─────────────────────────────────────────────
    #  generate_intro (минимальные изменения)
    # ─────────────────────────────────────────────

    async def generate_intro(
        self,
        session_id: int,
        user_id: int,
    ) -> str:
        session = await self._manager.get_session(session_id, user_id)

        world_context = ""
        chunk_ids: list[int] = []
        if session.world_id:
            world_context, chunk_ids = await self._rag.retrieve_context(
                query="лор мира, персонажи, локации, события",
                world_id=session.world_id,
            )

        mode_instruction = await self._build_mode_instruction(session)

        system_prompt_parts = [mode_instruction]
        if world_context:
            system_prompt_parts.append(world_context)
        system_prompt = "\n\n".join(p for p in system_prompt_parts if p)

        if session.mode == SessionModeEnum.narrator:
            intro_prompt = (
                "Дай атмосферное вступление к этой сессии. "
                "Опиши мир, его лор, ключевых персонажей, важные локации и события. "
                "Говори в стиле ведущего/рассказчика."
            )
        else:
            if session.character_name:
                intro_prompt = (
                    "Дай атмосферное вступление от лица персонажа, "
                    f"которого зовут {session.character_name}. "
                    "Пусть он опишет, где находится, что чувствует и что его окружает."
                )
            else:
                intro_prompt = (
                    "Дай атмосферное вступление от лица персонажа. "
                    "Пусть он опишет, где находится, что чувствует и что его окружает."
                )

        answer = await self._llm.generate(
            system_prompt=system_prompt,
            history=[{"role": "user", "content": intro_prompt}],
        )

        await self._manager.append_message(
            session_id=session_id,
            user_id=user_id,
            role=RoleEnum.assistant,
            content=answer,
            used_chunks=",".join(str(i) for i in chunk_ids) if chunk_ids else None,
        )

        return answer
