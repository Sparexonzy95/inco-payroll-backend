import api from './http'
import type { MeResponse, WalletLoginResponse, WalletNonceResponse } from './types'

export const getWalletNonce = async (wallet: string): Promise<WalletNonceResponse> => {
  const response = await api.post<WalletNonceResponse>('/api/auth/nonce/', { wallet })
  return response.data
}

export const walletLogin = async (payload: {
  wallet: string
  signature: string
  nonce: string
}): Promise<WalletLoginResponse> => {
  const response = await api.post<WalletLoginResponse>('/api/auth/wallet-login/', payload)
  return response.data
}

export const getMe = async (): Promise<MeResponse> => {
  const response = await api.get<MeResponse>('/api/auth/me/')
  return response.data
}

export const setActiveOrg = async (orgId: number): Promise<{ org_id: number; role: string }> => {
  const response = await api.post<{ org_id: number; role: string }>('/api/auth/set-active-org/', { org_id: orgId })
  return response.data
}
