import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { api } from "../api/client"
import Navbar from "../components/Navbar"
import DocumentsTab from "../components/DocumentsTab"
import "../styles/global.css"
import "../styles/world.css"

export default function WorldPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [world, setWorld] = useState(null)
  const [sessions, setSessions] = useState([])
  const [activeTab, setActiveTab] = useState("sessions")

  const [showModal, setShowModal] = useState(false)
  const [sessionTitle, setSessionTitle] = useState("")
  const [mode, setMode] = useState("narrator")          // дефолт – рассказчик
  const [characterName, setCharacterName] = useState("")
  const [generateIntro, setGenerateIntro] = useState(false)
  const [creating, setCreating] = useState(false)

  const [confirmDelete, setConfirmDelete] = useState(null)
  const [error, setError] = useState("")

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
      return
    }
    loadWorld()
    loadSessions()
  }, [id, navigate])

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") {
        if (showModal) closeModal()
        if (confirmDelete) setConfirmDelete(null)
      }
    }
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [showModal, confirmDelete])

  const loadWorld = async () => {
    const data = await api.get(`/worlds/${id}`)
    if (data?.id) setWorld(data)
  }

  const loadSessions = async () => {
    const data = await api.get(`/worlds/${id}/sessions?limit=100&offset=0`)
    if (Array.isArray(data?.items)) setSessions(data.items)
  }

  const openCreateModal = () => {
    setSessionTitle("")
    setMode("narrator")         // всегда по умолчанию рассказчик
    setCharacterName("")
    setGenerateIntro(false)
    setError("")
    setShowModal(true)
  }

  const closeModal = () => {
    if (creating) return
    setShowModal(false)
    setSessionTitle("")
    setMode("narrator")
    setCharacterName("")
    setGenerateIntro(false)
    setError("")
  }

  const handleCreateSession = async (e) => {
    e.preventDefault()
    if (!sessionTitle.trim()) {
      setError("Название обязательно")
      return
    }
    if (mode === "player" && !characterName.trim()) {
      setError("Укажи имя персонажа")
      return
    }
    if (creating) return

    setCreating(true)
    setError("")

    const body = {
      title: sessionTitle.trim(),
      generate_intro: generateIntro,
      mode,
      character_name: mode === "player" ? characterName.trim() : null,
    }

    const data = await api.post(`/worlds/${id}/sessions`, body, true)

    setCreating(false)

    if (data?.id) {
      closeModal()
      navigate(`/worlds/${id}/sessions/${data.id}`)
    } else {
      setError(data?.detail || "Ошибка создания сессии")
    }
  }

  const handleDeleteSession = async () => {
    if (!confirmDelete) return
    await api.delete(`/worlds/${id}/sessions/${confirmDelete}`, true)
    setConfirmDelete(null)
    loadSessions()
  }

  const renderModeLabel = (s) => {
    if (s.mode === "player") {
      return s.character_name
        ? `Режим: игрок — ${s.character_name}`
        : "Режим: игрок"
    }
    return "Режим: рассказчик"
  }

  return (
    <>
      <Navbar />

      <div className="world-container">
        {world && (
          <div className="world-info">
            <button
              className="btn-ghost btn-back"
              onClick={() => navigate("/worlds")}
            >
              ← Назад
            </button>
            <h2>{world.name}</h2>
            {world.description && (
              <p className="world-desc">{world.description}</p>
            )}
          </div>
        )}

        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === "sessions" ? "active" : ""}`}
            onClick={() => setActiveTab("sessions")}
          >
            Сессии
          </button>
          <button
            className={`tab-btn ${activeTab === "documents" ? "active" : ""}`}
            onClick={() => setActiveTab("documents")}
          >
            Документы
          </button>
        </div>

        {activeTab === "documents" && <DocumentsTab worldId={id} />}

        {activeTab === "sessions" && (
          <>
            <div className="sessions-header">
              <h3>Сессии</h3>
              <button onClick={openCreateModal}>+ Новая сессия</button>
            </div>

            {sessions.length === 0 ? (
              <p className="empty-state">
                Сессий пока нет — создай первую.
              </p>
            ) : (
              <div className="sessions-list">
                {sessions.map((s) => (
                  <div key={s.id} className="session-card">
                    <div
                      className="session-info"
                      onClick={() =>
                        navigate(`/worlds/${id}/sessions/${s.id}`)
                      }
                    >
                      <span className="session-name">
                        {s.title || "Без названия"}
                      </span>
                      <span className="session-date">
                        {new Date(s.created_at).toLocaleDateString("ru-RU")}
                      </span>
                      <span className="session-meta">
                        {renderModeLabel(s)}
                      </span>
                    </div>
                    <button
                      className="btn-danger"
                      onClick={() => setConfirmDelete(s.id)}
                    >
                      Удалить
                    </button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Новая сессия</h3>
            <form onSubmit={handleCreateSession}>
              <input
                placeholder="Название сессии *"
                value={sessionTitle}
                onChange={(e) => setSessionTitle(e.target.value)}
                autoFocus
                disabled={creating}
              />

              {/* выбор режима — дизайн как у Локация / Другое */}
              <div className="field-label">Режим</div>
              <div className="type-switch">
                <button
                  type="button"
                  className={`type-chip ${
                    mode === "narrator" ? "type-chip-active" : ""
                  }`}
                  onClick={() => setMode("narrator")}
                  disabled={creating}
                >
                  Рассказчик
                </button>
                <button
                  type="button"
                  className={`type-chip ${
                    mode === "player" ? "type-chip-active" : ""
                  }`}
                  onClick={() => setMode("player")}
                  disabled={creating}
                >
                  Игрок
                </button>
              </div>

              {mode === "player" && (
                <input
                  placeholder="Имя персонажа *"
                  value={characterName}
                  onChange={(e) => setCharacterName(e.target.value)}
                  disabled={creating}
                />
              )}

              <div className="toggle-row">
                <div className="toggle-label">
                  <span>Вступительное сообщение</span>
                  <span className="toggle-hint">
                    ИИ опишет мир перед началом сессии
                  </span>
                </div>
                <button
                  type="button"
                  className={`toggle-switch ${
                    generateIntro ? "toggle-on" : ""
                  }`}
                  onClick={() => setGenerateIntro(!generateIntro)}
                  disabled={creating}
                >
                  <span className="toggle-thumb" />
                </button>
              </div>

              {error && <p className="error">{error}</p>}

              {creating && (
                <div className="creating-state">
                  <div className="spinner" />
                  <span>
                    {generateIntro
                      ? "Создаём сессию и генерируем вступление…"
                      : "Создаём сессию…"}
                  </span>
                </div>
              )}

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-ghost"
                  onClick={closeModal}
                  disabled={creating}
                >
                  Отмена
                </button>
                <button type="submit" disabled={creating}>
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirmDelete && (
        <div
          className="modal-overlay"
          onClick={() => setConfirmDelete(null)}
        >
          <div
            className="modal modal-confirm"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>Удалить сессию?</h3>
            <p>Все сообщения будут удалены. Это действие нельзя отменить.</p>
            <div className="modal-actions">
              <button
                type="button"
                className="btn-ghost"
                onClick={() => setConfirmDelete(null)}
              >
                Отмена
              </button>
              <button
                className="btn-danger-solid"
                onClick={handleDeleteSession}
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
