import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import WorldsPage from "./pages/WorldsPage"
import HomePage from "./pages/HomePage"
import WorldPage from "./pages/WorldPage"
import SessionPage from "./pages/SessionPage"
import VerifyPage from "./pages/VerifyPage"
import ErrorPage from "./pages/ErrorPage"

function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/worlds" element={<WorldsPage />} />
          <Route path="/worlds/:id" element={<WorldPage />} />
          <Route path="/worlds/:worldId/sessions/:sessionId" element={<SessionPage />} />
          <Route path="/verify" element={<VerifyPage />} />
        <Route path="/500" element={<ErrorPage />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
