import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../components/Card'
import FormField from '../components/FormField'
import { createInstantRun } from '../api/payroll'
import { tokenStore } from '../auth/tokenStore'

const CreateRun = () => {
  const navigate = useNavigate()
  const [orgId, setOrgId] = useState(tokenStore.getOrgId() ?? '')
  const [claimWindowDays, setClaimWindowDays] = useState('14')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const run = await createInstantRun({
        org_id: orgId,
        claim_window_days: claimWindowDays ? Number(claimWindowDays) : undefined,
      })
      tokenStore.setOrgId(orgId)
      setSuccess(`Run ${run.run_id ?? run.id} created.`)
      if (run.run_id || run.id) {
        navigate(`/runs/${run.run_id ?? run.id}`)
      }
    } catch (err) {
      setError('Failed to create run. Confirm org ID and that employees are active.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Create instant run</h1>
          <p className="muted">Instant runs generate payroll immediately for active employees.</p>
        </div>
      </header>

      <Card title="Run details">
        <form className="stack" onSubmit={handleSubmit}>
          <FormField label="Organization ID">
            <input value={orgId} onChange={(event) => setOrgId(event.target.value)} required />
          </FormField>
          <FormField label="Claim window (days)">
            <input
              type="number"
              min={1}
              value={claimWindowDays}
              onChange={(event) => setClaimWindowDays(event.target.value)}
            />
          </FormField>
          {error ? <div className="error-banner">{error}</div> : null}
          {success ? <div className="success-banner">{success}</div> : null}
          <button className="button" type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create run'}
          </button>
        </form>
      </Card>
    </div>
  )
}

export default CreateRun
