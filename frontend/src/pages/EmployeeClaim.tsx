import { useState } from 'react'
import Card from '../components/Card'
import FormField from '../components/FormField'
import { getClaim } from '../api/payroll'
import type { PayrollClaimResponse } from '../api/types'

const EmployeeClaim = () => {
  const [payrollId, setPayrollId] = useState('')
  const [wallet, setWallet] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [claim, setClaim] = useState<PayrollClaimResponse | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setClaim(null)

    try {
      const data = await getClaim(payrollId, wallet)
      setClaim(data)
    } catch (err) {
      setError('Unable to fetch claim. Ensure run is open and wallet is correct.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Employee claim lookup</h1>
          <p className="muted">Fetch claim payloads for a payroll ID and wallet.</p>
        </div>
      </header>

      <Card title="Lookup claim">
        <form className="stack" onSubmit={handleSubmit}>
          <FormField label="Payroll ID">
            <input value={payrollId} onChange={(event) => setPayrollId(event.target.value)} required />
          </FormField>
          <FormField label="Wallet address">
            <input value={wallet} onChange={(event) => setWallet(event.target.value)} required />
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
