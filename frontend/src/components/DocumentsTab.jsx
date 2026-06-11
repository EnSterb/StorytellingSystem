import { useEffect, useState } from "react"
import { documentsApi } from "../api/documents"

const DOC_TYPES = [
  { value: "character", label: "Персонаж" },
  { value: "location",  label: "Локация" },
  { value: "event",     label: "Событие" },
  { value: "rule",      label: "Правило" },
  { value: "other",     label: "Другое" },
]


const EMPTY_FORM = {
  title: "",
  doc_type: "character",
  content: "",
}

export default function DocumentsTab({ worldId }) {
  const [docs, setDocs] = useState([])
  const [expanded, setExpanded] = useState(null)

  const [showModal, setShowModal] = useState(false)
  const [editDoc, setEditDoc] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const [confirmDelete, setConfirmDelete] = useState(null)

  useEffect(() => {
    loadDocs()
  }, [worldId])

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

  const loadDocs = async () => {
    const data = await documentsApi.list(worldId)
    if (Array.isArray(data.items)) {
      setDocs(data.items)
    } else if (Array.isArray(data)) {
      setDocs(data)
    } else {
      setDocs([])
    }
  }

  const openCreate = () => {
    setEditDoc(null)
    setForm(EMPTY_FORM)
    setError("")
    setShowModal(true)
  }

  const openEdit = (doc) => {
    setEditDoc(doc)
    setForm({
      title: doc.title,
      doc_type: doc.doc_type,
      content: doc.content,
    })
    setError("")
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditDoc(null)
    setForm(EMPTY_FORM)
    setError("")
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) {
      setError("Название обязательно")
      return
    }
    if (!form.content.trim()) {
      setError("Контент обязателен")
      return
    }

    setLoading(true)
    try {
      let data
      if (editDoc) {
        data = await documentsApi.update(worldId, editDoc.id, {
          title: form.title,
          doc_type: form.doc_type,
          content: form.content,
        })
      } else {
        data = await documentsApi.create(worldId, {
          title: form.title,
          doc_type: form.doc_type,
          content: form.content,
        })
      }

      if (data.id) {
        closeModal()
        loadDocs()
      } else {
        setError(data.detail || "Ошибка сохранения")
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    await documentsApi.delete(worldId, confirmDelete)
    setConfirmDelete(null)
    loadDocs()
  }

  return (
    <div className="documents-tab">
      <div className="tab-header">
        <h3>Документы</h3>
        <button onClick={openCreate}>+ Добавить документ</button>
      </div>

      {docs.length === 0 ? (
        <p className="empty-state">Документов пока нет — добавь первый!</p>
      ) : (
        <div className="documents-list">
          {docs.map((doc) => (
            <div key={doc.id} className="document-card">
              <div
                className="document-card-header"
                onClick={() =>
                  setExpanded(expanded === doc.id ? null : doc.id)
                }
              >
                <div className="document-card-meta">
                  <span className="document-title">{doc.title}</span>
                  <span className={`doc-type-badge doc-type-${doc.doc_type}`}>
                    {doc.doc_type}
                  </span>
                  {!doc.is_indexed && (
                    <span className="badge-pending">⏳ индексируется</span>
                  )}
                </div>
                <span className="expand-icon">
                  {expanded === doc.id ? "▲" : "▼"}
                </span>
              </div>

              {expanded === doc.id && (
                <div className="document-card-body">
                  <p className="document-content">{doc.content}</p>
                  <div className="document-actions">
                    <button
                      className="btn-ghost"
                      type="button"
                      onClick={() => openEdit(doc)}
                    >
                      Редактировать
                    </button>
                    <button
                      className="btn-danger"
                      type="button"
                      onClick={() => setConfirmDelete(doc.id)}
                    >
                      Удалить
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Модалка создания / редактирования */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div
            className="modal modal-document"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>{editDoc ? "Редактировать документ" : "Новый документ"}</h3>
            <form onSubmit={handleSubmit}>
              <input
                placeholder="Название *"
                value={form.title}
                onChange={(e) =>
                  setForm({ ...form, title: e.target.value })
                }
                autoFocus
              />

              {/* выбор типа документа */}
              <div className="doc-type-group">
                {DOC_TYPES.map((t) => (
                  <button
                    key={t.value}
                    type="button"
                    className={
                      "doc-type-pill" +
                      (form.doc_type === t.value
                        ? " doc-type-pill-active"
                        : "")
                    }
                    onClick={() =>
                      setForm({ ...form, doc_type: t.value })
                    }
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              <textarea
                placeholder="Контент документа *"
                rows={8}
                value={form.content}
                onChange={(e) =>
                  setForm({ ...form, content: e.target.value })
                }
              />

              {error && <p className="error">{error}</p>}
              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-ghost"
                  onClick={closeModal}
                >
                  Отмена
                </button>
                <button type="submit" disabled={loading}>
                  {loading
                    ? "Сохранение..."
                    : editDoc
                    ? "Сохранить"
                    : "Создать"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Подтверждение удаления */}
      {confirmDelete && (
        <div
          className="modal-overlay"
          onClick={() => setConfirmDelete(null)}
        >
          <div
            className="modal modal-confirm"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>Удалить документ?</h3>
            <p>Документ и его чанки в RAG будут удалены. Это действие нельзя отменить.</p>
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
                type="button"
                onClick={handleDelete}
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
