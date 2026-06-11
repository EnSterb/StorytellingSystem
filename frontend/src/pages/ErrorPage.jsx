import { useNavigate } from "react-router-dom"
import "../styles/global.css"
import "../styles/auth.css"

export default function ErrorPage() {
  const navigate = useNavigate()

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>500 — Ошибка сервера</h2>
        <p className="auth-subtitle">
          Что‑то пошло не так. Попробуйте позже или вернитесь на главную.
        </p>
        <div style={{ display: "flex", gap: "12px", marginTop: "8px" }}>
          <button onClick={() => navigate("/")}>На главную</button>
          <button
            className="btn-ghost"
            onClick={() => window.location.reload()}
          >
            Попробовать снова
          </button>
        </div>
      </div>
    </div>
  )
}
