import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { getWalletNonce } from '../api/auth'
import { useAuth } from '../auth/AuthProvider'
import Card from '../components/Card'

declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] | object }) => Promise<unknown>
    }
  }
}

const Login = () => {
  const { loginWithWallet } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const from = (location.state as { from?: Location })?.from?.pathname ?? '/'

  const handleWalletLogin = async () => {
    if (!window.ethereum) {
      setError('No wallet provider found. Install MetaMask or another EVM wallet.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const accounts = (await window.ethereum.request({ method: 'eth_requestAccounts' })) as string[]
      const wallet = accounts?.[0]
      if (!wallet) {
        throw new Error('No wallet account selected.')
      }

      const nonceResponse = await getWalletNonce(wallet)
      const signature = (await window.ethereum.request({
        method: 'personal_sign',
        params: [nonceResponse.message, wallet],
      })) as string

      const user = await loginWithWallet(wallet, signature, nonceResponse.nonce)
      navigate(user?.is_employer_registered ? from : '/employer-onboarding', { replace: true })
    } catch {
      setError('Wallet login failed. Please retry the sign-in flow.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="centered">
      <Card title="Wallet Login">
        <div className="stack">
          <p className="muted">Connect your wallet and sign the nonce challenge to receive JWT tokens.</p>
          {error ? <div className="error-banner">{error}</div> : null}
          <button className="button" type="button" disabled={loading} onClick={handleWalletLogin}>
            {loading ? 'Signing in...' : 'Connect wallet'}
          </button>
        </div>
      </Card>
    </div>
  )
}

export default Login
