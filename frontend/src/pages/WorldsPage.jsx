import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { api } from "../api/client"
import Navbar from "../components/Navbar"
import "../styles/global.css"
import "../styles/worlds.css"

export default function WorldsPage() {
  const [worlds, setWorlds] = useState([])
  const [expanded, setExpanded] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) { navigate("/login"); return }
    loadWorlds()
  }, [])

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") {
        closeModal()
        setConfirmDelete(null)
      }
    }
    if (showModal || confirmDelete) window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [showModal, confirmDelete])

  const loadWorlds = async () => {
    const data = await api.get("/worlds")
    if (Array.isArray(data)) setWorlds(data)
  }

  const toggleExpand = (id) => {
    setExpanded(prev => prev === id ? null : id)
  }

  const closeModal = () => {
    setShowModal(false)
    setName("")
    setDescription("")
    setError("")
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!name.trim()) { setError("Название обязательно"); return }
    const data = await api.post("/worlds", { name, description }, true)
    if (data.id) {
      closeModal()
      loadWorlds()
    } else {
      setError(data.detail || "Ошибка создания")
    }
  }

  const handleDelete = async () => {
    await api.delete(`/worlds/${confirmDelete}`)
    setConfirmDelete(null)
    setExpanded(null)
    loadWorlds()
  }

  return (
    <>
      <Navbar />
      <div className="worlds-container">
        <div className="worlds-header">
          <h2>Мои миры</h2>
          <button onClick={() => setShowModal(true)}>+ Создать мир</button>
        </div>

        {worlds.length === 0 ? (
          <p className="empty-state">Миров пока нет — создай первый!</p>
        ) : (
          <div className="worlds-grid">
            {worlds.map(w => (
              <div key={w.id} className={`world-card ${expanded === w.id ? "expanded" : ""}`}>
                <div className="world-card-header" onClick={() => toggleExpand(w.id)}>
                  <span>{w.name}</span>
                  <span className="world-arrow">{expanded === w.id ? "▲" : "▼"}</span>
                </div>
                <div className="world-card-body-wrapper" style={{
                  maxHeight: expanded === w.id ? "300px" : "0px",
                  overflow: "hidden",
                  transition: expanded === w.id ? "max-height 0.4s ease" : "max-height 0.2s ease"
                }}>
                  <div className="world-card-body">
                      <p>{w.description || "Описание не указано"}</p>
                      <div className="world-card-actions">
                        <button onClick={() => navigate(`/worlds/${w.id}`)}>Открыть</button>
                        <button className="btn-danger" onClick={() => setConfirmDelete(w.id)}>Удалить</button>
                      </div>
                    </div>

                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Модалка создания */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>Новый мир</h3>
            <form onSubmit={handleCreate}>
              <input
                placeholder="Название *"
                value={name}
                onChange={e => setName(e.target.value)}
              />
              <textarea
                placeholder="Описание (необязательно)"
                value={description}
                onChange={e => setDescription(e.target.value)}
                rows={4}
              />
              {error && <p className="error">{error}</p>}
              <div className="modal-actions">
                <button type="button" className="btn-ghost" onClick={closeModal}>Отмена</button>
                <button type="submit">Создать</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модалка подтверждения удаления */}
      {confirmDelete && (
        <div className="modal-overlay" onClick={() => setConfirmDelete(null)}>
          <div className="modal modal-confirm" onClick={e => e.stopPropagation()}>
            <h3>Удалить мир?</h3>
            <p>Это действие нельзя отменить. Все данные мира будут удалены.</p>
            <div className="modal-actions">
              <button type="button" className="btn-ghost" onClick={() => setConfirmDelete(null)}>Отмена</button>
              <button className="btn-danger-solid" onClick={handleDelete}>Удалить</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
