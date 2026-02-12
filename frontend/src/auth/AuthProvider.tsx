import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { getMe, setActiveOrg as setActiveOrgRequest, walletLogin } from '../api/auth'
import type { MeResponse } from '../api/types'
import { tokenStore } from './tokenStore'

interface AuthContextValue {
  isAuthenticated: boolean
  me: MeResponse | null
  loadingMe: boolean
  loginWithWallet: (wallet: string, signature: string, nonce: string) => Promise<void>
  refreshMe: () => Promise<void>
  selectActiveOrg: (orgId: number) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [accessToken, setAccessToken] = useState(tokenStore.getAccessToken())
  const [me, setMe] = useState<MeResponse | null>(null)
  const [loadingMe, setLoadingMe] = useState(Boolean(tokenStore.getAccessToken()))

  const refreshMe = async () => {
    setLoadingMe(true)
    try {
      const profile = await getMe()
      setMe(profile)
      if (profile.wallet) tokenStore.setWallet(profile.wallet)
      if (profile.active_org_id) tokenStore.setActiveOrgId(String(profile.active_org_id))
    } catch {
      setMe(null)
    } finally {
      setLoadingMe(false)
    }
  }

  useEffect(() => {
    if (accessToken) {
      void refreshMe()
    }
  }, [accessToken])

  const loginWithWallet = async (wallet: string, signature: string, nonce: string) => {
    const data = await walletLogin({ wallet, signature, nonce })
    tokenStore.setTokens(data.access, data.refresh)
    setAccessToken(data.access)
    if (data.user.wallet) tokenStore.setWallet(data.user.wallet)
    await refreshMe()
  }

  const selectActiveOrg = async (orgId: number) => {
    await setActiveOrgRequest(orgId)
    tokenStore.setActiveOrgId(String(orgId))
    await refreshMe()
  }

  const logout = () => {
    tokenStore.clearTokens()
    tokenStore.clearWallet()
    tokenStore.clearActiveOrgId()
    setAccessToken(null)
    setMe(null)
  }

  const value = useMemo(
    () => ({
      isAuthenticated: Boolean(accessToken),
      me,
      loadingMe,
      loginWithWallet,
      refreshMe,
      selectActiveOrg,
      logout,
    }),
    [accessToken, me, loadingMe],
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
