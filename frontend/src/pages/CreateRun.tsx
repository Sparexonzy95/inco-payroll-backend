import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../components/Card'
import FormField from '../components/FormField'
import { createRun } from '../api/payroll'
import { tokenStore } from '../auth/tokenStore'

const CreateRun = () => {
  const navigate = useNavigate()
  const [orgId, setOrgId] = useState(tokenStore.getOrgId() ?? '')
  const [payrollId, setPayrollId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const pid = Number(payrollId)
      if (!Number.isFinite(pid) || pid <= 0) {
        setError('Payroll ID must be a positive number.')
        setLoading(false)
        return
      }

      const run = await createRun({
        org_id: orgId,
        payroll_id: pid,
      })

      tokenStore.setOrgId(orgId)
      const rid = run.run_id ?? run.id
      setSuccess(`Run ${rid ?? ''} created.`)

      if (rid) {
        navigate(`/runs/${rid}`)
      }
    } catch {
      setError('Failed to create run. Confirm org ID, payroll ID, and that employees are active.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Create run</h1>
          <p className="muted">Creates a draft payroll run for all active employees in the org.</p>
        </div>
      </header>

      <Card title="Run details">
        <form className="stack" onSubmit={handleSubmit}>
          <FormField label="Organization ID">
            <input value={orgId} onChange={(event) => setOrgId(event.target.value)} required />
          </FormField>

          <FormField label="Payroll ID (required by backend)">
            <input
              type="number"
              min={1}
              value={payrollId}
              onChange={(event) => setPayrollId(event.target.value)}
              required
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
