const ACCESS_TOKEN_KEY = 'inco_access_token'
const REFRESH_TOKEN_KEY = 'inco_refresh_token'
const WALLET_KEY = 'inco_wallet'

export const tokenStore = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens: (access: string, refresh: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  },
  clearTokens: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },
  getWallet: () => localStorage.getItem(WALLET_KEY),
  setWallet: (wallet: string) => localStorage.setItem(WALLET_KEY, wallet),
  clearWallet: () => localStorage.removeItem(WALLET_KEY),
}
