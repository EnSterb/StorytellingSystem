import { useState, useEffect } from "react"
import { useNavigate, Link } from "react-router-dom"
import { api } from "../api/client"
import "../styles/global.css"
import "../styles/auth.css"
import Navbar from "../components/Navbar.jsx"

const validateEmail = (email) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [formError, setFormError] = useState("")
  const [fieldErrors, setFieldErrors] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (localStorage.getItem("token")) navigate("/")
  }, [navigate])

  const validate = () => {
    const errors = {}

    if (!email.trim()) errors.email = "Введите email"
    else if (!validateEmail(email.trim()))
      errors.email = "Некорректный email"

    if (!password) errors.password = "Введите пароль"

    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e) => {
  e.preventDefault()
  if (loading) return
  setFormError("")

  if (!validate()) return

  setLoading(true)
  try {
    const res = await fetch("http://localhost:8000/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email.trim(), password }),
    })

    if (res.status === 401) {
      setFormError("Неверный email или пароль")
      return
    }

    if (res.status === 500 || res.status === 404) {
      navigate("/500")
      return
    }

    const data = await res.json()

    if (data.access_token) {
      localStorage.setItem("token", data.access_token)
      navigate("/worlds")
    } else {
      setFormError(data.detail || "Ошибка входа")
    }
  } catch {
    navigate("/500")
  } finally {
    setLoading(false)
  }
}


  return (
    <>
      <Navbar />
      <div className="auth-container">
        <div className="auth-card">
          <h2>Вход</h2>
          <form onSubmit={handleSubmit} className={loading ? "form-disabled" : ""}>
            <div className="field">
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                disabled={loading}
              />
              {fieldErrors.email && (
                <p className="error small">{fieldErrors.email}</p>
              )}
            </div>

            <div className="field">
              <input
                type="password"
                placeholder="Пароль"
                value={password}
                onChange={e => setPassword(e.target.value)}
                disabled={loading}
              />
              {fieldErrors.password && (
                <p className="error small">{fieldErrors.password}</p>
              )}
            </div>

            {formError && <p className="error">{formError}</p>}
            <button type="submit" disabled={loading}>
              {loading ? "Входим..." : "Войти"}
            </button>
            {loading && <div className="spinner" />}
          </form>
          <p>Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
        </div>
      </div>
    </>
  )
}
