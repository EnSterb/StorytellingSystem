import { useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { api } from "../api/client"
import "../styles/global.css"
import "../styles/auth.css"

export default function VerifyPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState("loading") // "loading" | "success" | "error"
  const [message, setMessage] = useState("")

  useEffect(() => {
    const token = searchParams.get("token")
    if (!token) {
      setStatus("error")
      setMessage("Токен отсутствует.")
      return
    }
    verifyEmail(token)
  }, [])

  const verifyEmail = async (token) => {
    try {
      const res = await fetch(
        `http://localhost:8000/api/v1/auth/verify?token=${token}`
      )
      if (res.ok) {
        setStatus("success")
      } else {
        const data = await res.json()
        setStatus("error")
        setMessage(data.detail || "Ссылка недействительна или истекла.")
      }
    } catch {
      setStatus("error")
      setMessage("Ошибка соединения с сервером.")
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        {status === "loading" && (
          <>
            <h2>Подтверждение email...</h2>
            <p className="auth-subtitle">Пожалуйста, подождите.</p>
          </>
        )}

        {status === "success" && (
          <>
            <h2>✅ Email подтверждён!</h2>
            <p className="auth-subtitle">
              Аккаунт активирован. Теперь вы можете войти.
            </p>
            <button onClick={() => navigate("/login")}>Войти</button>
          </>
        )}

        {status === "error" && (
          <>
            <h2>❌ Ошибка подтверждения</h2>
            <p className="error">{message}</p>
            <button
              className="btn-ghost"
              onClick={() => navigate("/login")}
            >
              На страницу входа
            </button>
          </>
        )}
      </div>
    </div>
  )
}
