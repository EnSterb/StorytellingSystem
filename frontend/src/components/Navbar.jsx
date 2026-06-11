import { useNavigate, Link } from "react-router-dom"
import "../styles/navbar.css"

export default function Navbar() {
  const navigate = useNavigate()
  const token = localStorage.getItem("token")

  const handleLogout = () => {
    localStorage.removeItem("token")
    navigate("/")
  }

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo">Storytelling</Link>
      <div className="navbar-actions">
        {token ? (
          <>
            <button onClick={() => navigate("/worlds")} className="btn-ghost">Творить</button>
            <button onClick={handleLogout}>Выйти</button>
          </>
        ) : (
          <>
            <button onClick={() => navigate("/login")} className="btn-ghost">Войти</button>
            <button onClick={() => navigate("/register")}>Регистрация</button>
          </>
        )}
      </div>
    </nav>
  )
}
