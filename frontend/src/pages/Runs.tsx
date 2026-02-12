import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Card from '../components/Card'
import Table from '../components/Table'
import FormField from '../components/FormField'
import { listRuns } from '../api/payroll'
import { PayrollRun } from '../api/types'
import { formatDateTime } from '../utils/format'
import { tokenStore } from '../auth/tokenStore'

const Runs = () => {
  const [orgId, setOrgId] = useState(tokenStore.getOrgId() ?? '')
  const [runs, setRuns] = useState<PayrollRun[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadRuns = async (currentOrgId = orgId) => {
    if (!currentOrgId) return
    setLoading(true)
    setError(null)
    try {
      const data = await listRuns(currentOrgId)
      setRuns(data)
    } catch (err) {
      setError('Failed to load runs.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (orgId) {
      tokenStore.setOrgId(orgId)
      void loadRuns(orgId)
    }
  }, [orgId])

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Payroll Runs</h1>
          <p className="muted">Review run status, totals, and on-chain hashes.</p>
        </div>
        <div className="actions">
          <Link className="button" to="/runs/create">
            Create instant run
          </Link>
        </div>
      </header>

      <Card title="Filter">
        <FormField label="Organization ID">
          <input value={orgId} onChange={(event) => setOrgId(event.target.value)} />
        </FormField>
      </Card>

      <Card title="Runs">
        {loading ? <p>Loading runs...</p> : null}
        {error ? <div className="error-banner">{error}</div> : null}
        <Table headers={['ID', 'Payroll ID', 'Status', 'Total', 'Close at', 'Actions']}>
          {runs.map((run) => (
            <tr key={run.id ?? run.run_id}>
              <td>{run.id ?? run.run_id}</td>
              <td>{run.payroll_id}</td>
              <td>{run.status ?? '-'}</td>
              <td>{run.total ?? '-'}</td>
              <td>{formatDateTime(run.close_at)}</td>
              <td>
                {run.id ? (
                  <Link className="button small" to={`/runs/${run.id}`}>
                    View
                  </Link>
                ) : null}
              </td>
            </tr>
          ))}
        </Table>
      </Card>
    </div>
  )
}

export default Runs
