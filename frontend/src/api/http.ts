import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { tokenStore } from '../auth/tokenStore'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

const api: AxiosInstance = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let subscribers: Array<(token: string | null) => void> = []

const subscribeTokenRefresh = (cb: (token: string | null) => void) => {
  subscribers.push(cb)
}

const notifySubscribers = (token: string | null) => {
  subscribers.forEach((cb) => cb(token))
  subscribers = []
}

const refreshAccessToken = async (): Promise<string | null> => {
  const refresh = tokenStore.getRefreshToken()
  if (!refresh) {
    return null
  }

  try {
    const response = await axios.post(
      `${apiBaseUrl}/api/auth/refresh/`,
      { refresh },
      { headers: { 'Content-Type': 'application/json' } },
    )
    const newAccess = response.data?.access as string | undefined
    if (newAccess) {
      tokenStore.setTokens(newAccess, refresh)
      return newAccess
    }
  } catch {
    tokenStore.clearTokens()
  }

  return null
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/api/auth/refresh/')
    ) {
      originalRequest._retry = true

      if (!isRefreshing) {
        isRefreshing = true
        refreshAccessToken()
          .then((token) => {
            notifySubscribers(token)
          })
          .finally(() => {
            isRefreshing = false
          })
      }

      return new Promise((resolve, reject) => {
        subscribeTokenRefresh((token) => {
          if (!token) {
            reject(error)
            return
          }
          originalRequest.headers = {
            ...originalRequest.headers,
            Authorization: `Bearer ${token}`,
          }
          resolve(api(originalRequest))
        })
      })
    }

    return Promise.reject(error)
  },
)

export default api
