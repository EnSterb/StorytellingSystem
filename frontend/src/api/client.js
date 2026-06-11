const BASE_URL = "http://localhost:8000/api/v1"

const getToken = () => localStorage.getItem("token")

const handleAuthError = async (res) => {
  if (res.status === 401) {
    localStorage.removeItem("token")
    // редирект без React, чтобы не тянуть navigate сюда
    window.location.href = "/login"
    return null
  }
  return res
}

export const api = {
  post: async (path, body, auth = false) => {
    const headers = { "Content-Type": "application/json" }
    if (auth) headers["Authorization"] = `Bearer ${getToken()}`
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    })
    const checked = await handleAuthError(res)
    if (!checked) return {}
    return checked.json()
  },

  get: async (path) => {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    const checked = await handleAuthError(res)
    if (!checked) return {}
    return checked.json()
  },

  delete: async (path) => {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    const checked = await handleAuthError(res)
    if (!checked) return {}
    return checked.status === 204 ? {} : checked.json()
  },

  patch: async (path, body) => {
    const res = await fetch(`${BASE_URL}${path}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify(body),
    })
    const checked = await handleAuthError(res)
    if (!checked) return {}
    return checked.json()
  },
}
