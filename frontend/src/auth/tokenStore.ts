const ACCESS_TOKEN_KEY = 'inco_access_token'
const REFRESH_TOKEN_KEY = 'inco_refresh_token'
const USERNAME_KEY = 'inco_username'
const ORG_ID_KEY = 'inco_org_id'

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
  getUsername: () => localStorage.getItem(USERNAME_KEY),
  setUsername: (username: string) => {
    localStorage.setItem(USERNAME_KEY, username)
  },
  clearUsername: () => {
    localStorage.removeItem(USERNAME_KEY)
  },
  getOrgId: () => localStorage.getItem(ORG_ID_KEY),
  setOrgId: (orgId: string) => {
    localStorage.setItem(ORG_ID_KEY, orgId)
  },
}
