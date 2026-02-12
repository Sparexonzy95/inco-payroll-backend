import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Card from '../components/Card'
import Table from '../components/Table'
import { listRunClaims, openRun } from '../api/payroll'
import type { RunClaimsResponse } from '../api/types'
import { formatDateTime } from '../utils/format'

const RunDetail = () => {
  const { runId } = useParams()
  const [runDetails, setRunDetails] = useState<RunClaimsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [openStatus, setOpenStatus] = useState<string | null>(null)

  const loadRun = async () => {
    if (!runId) return
    setLoading(true)
    setError(null)
    try {
      const data = await listRunClaims(runId)
      setRunDetails(data)
    } catch (err) {
      setError('Failed to load run details.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadRun()
  }, [runId])

  const handleOpenRun = async () => {
    if (!runId) return
    setOpenStatus(null)
    try {
      const response = await openRun(runId)
      setOpenStatus(`Run opened: ${response.status}`)
      await loadRun()
    } catch (err) {
      setOpenStatus('Failed to open run. Ensure tx hashes are recorded.')
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Run detail</h1>
          <p className="muted">Run ID: {runId}</p>
        </div>
        <div className="actions">
          <Link className="button secondary" to={`/runs/${runId}/commit`}>
            Commit run
          </Link>
          <Link className="button secondary" to={`/runs/${runId}/tx`}>
            Tx helper
          </Link>
          <button className="button" type="button" onClick={handleOpenRun}>
            Open run
          </button>
        </div>
      </header>

      {openStatus ? <div className="info-banner">{openStatus}</div> : null}

      <Card title="Run overview">
        {loading ? <p>Loading run...</p> : null}
        {error ? <div className="error-banner">{error}</div> : null}
        {runDetails ? (
          <div className="stack">
            <div className="grid two">
              <div>
                <strong>Status:</strong> {runDetails.status}
              </div>
              <div>
                <strong>Payroll ID:</strong> {runDetails.payroll_id}
              </div>
              <div>
                <strong>Total employees:</strong> {runDetails.total}
              </div>
              <div>
                <strong>Total amount units:</strong> {runDetails.total_amount_units}
              </div>
              <div>
                <strong>Merkle root:</strong> {runDetails.merkle_root}
              </div>
            </div>
          </div>
        ) : null}
      </Card>

      <Card title="Claims">
        {runDetails ? (
          <Table headers={['Index', 'Wallet', 'Status', 'Salary units', 'Ciphertext', 'Claimed at']}>
            {runDetails.claims.map((claim) => (
              <tr key={claim.index}>
                <td>{claim.index}</td>
                <td>{claim.employee_wallet}</td>
                <td>{claim.status}</td>
                <td>{claim.salary_units ?? '-'}</td>
                <td>{claim.has_ciphertext ? 'Yes' : 'No'}</td>
                <td>{formatDateTime(claim.claimed_at)}</td>
              </tr>
            ))}
          </Table>
        ) : (
          <p className="muted">No claims available.</p>
        )}
      </Card>
    </div>
  )
}

export default RunDetail
