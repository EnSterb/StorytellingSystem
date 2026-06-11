import { useState, useEffect } from "react"
import { useNavigate, Link } from "react-router-dom"
import { api } from "../api/client"
import "../styles/global.css"
import "../styles/auth.css"
import Navbar from "../components/Navbar.jsx"

const isEmailValid = (email) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

const isPasswordValid = (password) =>
  password.length >= 8 && /\d/.test(password)

export default function RegisterPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [username, setUsername] = useState("")
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState("")
  const [successMsg, setSuccessMsg] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (localStorage.getItem("token")) navigate("/")
  }, [navigate])

  const validate = () => {
    const errors = {}

    const nameTrim = username.trim()
    const emailTrim = email.trim()

    if (!nameTrim) errors.username = "Введите имя пользователя"
    else if (nameTrim.length < 3)
      errors.username = "Минимум 3 символа"

    if (!emailTrim) errors.email = "Введите email"
    else if (!isEmailValid(emailTrim))
      errors.email = "Некорректный email (name@example.com)"

    if (!password) errors.password = "Введите пароль"
    else if (!isPasswordValid(password))
      errors.password = "Минимум 8 символов и хотя бы одна цифра"

    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (loading) return
    setFormError("")
    setSuccessMsg("")
    if (!validate()) return

    setLoading(true)
    try {
      const data = await api.post("/auth/register", {
        email: email.trim(),
        password,
        username: username.trim(),
      })

      if (data.id) {
        setSuccessMsg(
          "Письмо с подтверждением отправлено на вашу почту. Перейдите по ссылке из письма."
        )
        // опционально: очистить форму
        setEmail("")
        setPassword("")
        setUsername("")
      } else if (data.detail) {
        // если сервер вернул «User with this email already exists» и т.п.
        if (email.trim() && username.trim()) {
          setFormError("Такой email или имя пользователя уже заняты")
        } else {
          setFormError(data.detail)
        }
      } else {
        setFormError("Ошибка регистрации")
      }
    } catch {
      setFormError("Сервис временно недоступен, попробуйте позже")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Navbar />
      <div className="auth-container">
        <div className="auth-card">
          <h2>Регистрация</h2>
          <form onSubmit={handleSubmit} className={loading ? "form-disabled" : ""}>
            <div className="field">
              <input
                placeholder="Имя пользователя"
                value={username}
                onChange={e => setUsername(e.target.value)}
                disabled={loading}
              />
              {fieldErrors.username && (
                <p className="error small">{fieldErrors.username}</p>
              )}
            </div>

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
            {successMsg && <p className="success">{successMsg}</p>}

            <button type="submit" disabled={loading}>
              {loading ? "Регистрация..." : "Зарегистрироваться"}
            </button>
            {loading && <div className="spinner" />}
          </form>
          <p>Уже есть аккаунт? <Link to="/login">Войти</Link></p>
        </div>
      </div>
    </>
  )
}
