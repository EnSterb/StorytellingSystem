import { api } from "./client"

export const sessionsApi = {
  get: (worldId, sessionId) =>
    api.get(`/worlds/${worldId}/sessions/${sessionId}`),

  history: (worldId, sessionId, last_n = null) => {
    const q = last_n ? `?last_n=${last_n}` : ""
    return api.get(`/worlds/${worldId}/sessions/${sessionId}/history${q}`)
  },

  chat: async (worldId, sessionId, message) =>
    api.post(
      `/worlds/${worldId}/sessions/${sessionId}/chat`,
      { message },
      true
    ),
}
