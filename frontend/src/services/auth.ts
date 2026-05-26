import api from './apiClient'
import { useAuthStore } from '../store/auth'

export async function login(username: string, password: string) {
  const { data } = await api.post('/auth/token/', { username, password })
  useAuthStore.getState().setTokens(data.access, data.refresh)
  return data
}

export async function fetchMe() {
  const { data } = await api.get('/users/me/')
  useAuthStore.getState().setUser(data)
  return data
}

