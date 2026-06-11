import { useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import Navbar from "../components/Navbar"
import { sessionsApi } from "../api/sessions"
import "../styles/global.css"
import "../styles/session.css"

export default function SessionPage() {
  const { worldId, sessionId } = useParams()
  const navigate = useNavigate()

  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const bottomRef = useRef(null)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) { navigate("/login"); return }
    loadSession()
    loadHistory()
  }, [worldId, sessionId])

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, loading])

  const loadSession = async () => {
    const data = await sessionsApi.get(worldId, sessionId)
    if (data.id) setSession(data)
  }

  const loadHistory = async () => {
    const data = await sessionsApi.history(worldId, sessionId)
    if (Array.isArray(data)) setMessages(data)
  }

  const handleSend = async (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || loading) return

    setError("")
    setInput("")

    // сразу добавляем пользовательское сообщение в историю
    const userMsg = {
      id: `tmp-user-${Date.now()}`,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMsg])

    setLoading(true)
    try {
      const res = await sessionsApi.chat(worldId, sessionId, text)
      const botMsg = {
        id: `tmp-bot-${Date.now()}`,
        role: "assistant",
        content: res.answer,
        created_at: new Date().toISOString(),
      }
      setMessages(prev => [...prev, botMsg])
    } catch (err) {
      setError("Ошибка при отправке сообщения")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Navbar />
      <div className="session-page">
        <div className="session-header">
          <button
            className="btn-ghost btn-back"
            onClick={() => navigate(`/worlds/${worldId}`)}
          >
            ← К миру
          </button>
          {session && <h2>{session.title || "Без названия"}</h2>}
        </div>

        <div className="chat-container">
          <div className="chat-messages">
            {messages.map((m) => (
              <div
                key={m.id}
                className={
                  "chat-message " +
                  (m.role === "assistant" ? "chat-assistant" : "chat-user")
                }
              >
                <div className="chat-bubble">
                  {m.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message chat-assistant">
                <div className="chat-bubble typing">
                  Модель думает…
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <form className="chat-input-row" onSubmit={handleSend}>
            <textarea
              rows={2}
              placeholder="Напишите сообщение..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Отправить
            </button>
          </form>
          {error && <p className="error chat-error">{error}</p>}
        </div>
      </div>
    </>
  )
}
