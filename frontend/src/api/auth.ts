import api from './http'

export interface AuthTokens {
  access: string
  refresh: string
}

export const login = async (username: string, password: string): Promise<AuthTokens> => {
  const response = await api.post<AuthTokens>('/api/auth/login/', { username, password })
  return response.data
}

export const refresh = async (refreshToken: string): Promise<{ access: string }> => {
  const response = await api.post<{ access: string }>('/api/auth/refresh/', { refresh: refreshToken })
  return response.data
}
