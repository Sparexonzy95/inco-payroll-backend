import { createContext, ReactNode, useContext, useMemo, useState } from 'react'
import { login as loginRequest } from '../api/auth'
import { tokenStore } from './tokenStore'

interface AuthContextValue {
  isAuthenticated: boolean
  username: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [accessToken, setAccessToken] = useState(tokenStore.getAccessToken())
  const [username, setUsername] = useState(tokenStore.getUsername())

  const login = async (user: string, password: string) => {
    const data = await loginRequest(user, password)
    tokenStore.setTokens(data.access, data.refresh)
    tokenStore.setUsername(user)
    setAccessToken(data.access)
    setUsername(user)
  }

  const logout = () => {
    tokenStore.clearTokens()
    tokenStore.clearUsername()
    setAccessToken(null)
    setUsername(null)
  }

  const value = useMemo(
    () => ({
      isAuthenticated: Boolean(accessToken),
      username,
      login,
      logout,
    }),
    [accessToken, username],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
