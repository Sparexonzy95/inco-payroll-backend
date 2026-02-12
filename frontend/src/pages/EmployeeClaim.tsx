import { useState } from 'react'
import { getClaim } from '../api/payroll'
import type { PayrollClaimResponse } from '../api/types'
import { useAuth } from '../auth/AuthProvider'
import Card from '../components/Card'
import FormField from '../components/FormField'

const EmployeeClaim = () => {
  const { me } = useAuth()
  const [payrollId, setPayrollId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [claim, setClaim] = useState<PayrollClaimResponse | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setClaim(null)

    if (!me?.wallet) {
      setError('No wallet found in profile. Complete wallet login first.')
      setLoading(false)
      return
    }

    try {
      const data = await getClaim(payrollId, me.wallet)
      setClaim(data)
    } catch {
      setError('Unable to fetch claim. Ensure run is open and wallet is authorized.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>My claim</h1>
          <p className="muted">Fetch claim payload for your wallet.</p>
        </div>
      </header>

      <Card title="Lookup claim">
        <form className="stack" onSubmit={handleSubmit}>
          <FormField label="Payroll ID">
            <input value={payrollId} onChange={(event) => setPayrollId(event.target.value)} required />
          </FormField>
          <FormField label="Wallet">
            <input value={me?.wallet ?? ''} readOnly />
          </FormField>
          {error ? <div className="error-banner">{error}</div> : null}
          <button className="button" type="submit" disabled={loading}>
            {loading ? 'Loading...' : 'Fetch claim'}
          </button>
        </form>
      </Card>

      <Card title="Claim payload">
        {claim ? <pre className="code-block">{JSON.stringify(claim, null, 2)}</pre> : <p>No claim loaded.</p>}
      </Card>
    </div>
  )
}

export default EmployeeClaim
