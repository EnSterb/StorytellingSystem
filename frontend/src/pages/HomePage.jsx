import { useNavigate } from "react-router-dom"
import Navbar from "../components/Navbar"
import "../styles/global.css"
import "../styles/home.css"

export default function HomePage() {
  const navigate = useNavigate()

  const handleStart = () => {
    const token = localStorage.getItem("token")
    if (token) navigate("/worlds")
    else navigate("/login")
  }

  return (
    <>
      <Navbar />
      <div className="home-container">
        <div className="home-content">
          <h1 className="home-title">Storytelling</h1>
          <p className="home-subtitle">
            Создавай уникальные миры, населяй их героями и веди повествование
            вместе с искусственным интеллектом. Каждая история начинается
            с одной идеи — твоей.
          </p>
          <button onClick={handleStart}>Начать творить</button>
        </div>
      </div>
    </>
  )
}
