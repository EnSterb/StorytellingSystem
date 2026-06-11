import { api } from "./client"

export const documentsApi = {
  list: (worldId) =>
    api.get(`/worlds/${worldId}/documents?limit=20&offset=0`),
  create: (worldId, body) =>
    api.post(`/worlds/${worldId}/documents`, body, true),
  update: (worldId, docId, body) =>
    api.patch(`/worlds/${worldId}/documents/${docId}`, body),
  delete: (worldId, docId) =>
    api.delete(`/worlds/${worldId}/documents/${docId}`),
}