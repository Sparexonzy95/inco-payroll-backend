import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createRun } from '../api/payroll'
import Card from '../components/Card'
import FormField from '../components/FormField'

const CreateRun = () => {
  const navigate = useNavigate()
  const [claimWindowDays, setClaimWindowDays] = useState('14')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const days = Number(claimWindowDays)
      if (!Number.isFinite(days) || days <= 0) {
        setError('Claim window days must be a positive number.')
        setLoading(false)
        return
      }

      const run = await createRun({ claim_window_days: days })
      const rid = run.run_id ?? run.id
      if (rid) navigate(`/runs/${rid}`)
    } catch {
      setError('Failed to create run. Ensure active employees exist and employer profile is registered.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Create run</h1>
          <p className="muted">Creates a draft payroll run for active employees under your employer profile.</p>
        </div>
      </header>

      <Card title="Run details">
        <form className="stack" onSubmit={handleSubmit}>
          <FormField label="Claim window days">
            <input type="number" min={1} value={claimWindowDays} onChange={(event) => setClaimWindowDays(event.target.value)} />
          </FormField>

          {error ? <div className="error-banner">{error}</div> : null}

          <button className="button" type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create run'}
          </button>
        </form>
      </Card>
    </div>
  )
}

export default CreateRun
