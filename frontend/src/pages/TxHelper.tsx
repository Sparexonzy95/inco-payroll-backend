import { useState } from 'react'
import { useParams } from 'react-router-dom'
import Card from '../components/Card'
import { txCreatePayroll, txFundPlan } from '../api/payroll'

const TxHelper = () => {
  const { runId } = useParams()
  const [payload, setPayload] = useState<object | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadPayload = async (type: 'create' | 'fund') => {
    if (!runId) return
    setLoading(true)
    setError(null)
    try {
      const data = type === 'create' ? await txCreatePayroll(runId) : await txFundPlan(runId)
      setPayload(data)
    } catch (err) {
      setError('Failed to load transaction helper payload.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Tx helper</h1>
          <p className="muted">Run ID: {runId}</p>
        </div>
      </header>

      <Card title="CreatePayroll tx payload" actions={
        <button className="button small" type="button" onClick={() => loadPayload('create')}>
          Fetch payload
        </button>
      }>
        <p className="muted">Returns the createPayroll transaction template.</p>
      </Card>

      <Card title="FundPlan payload" actions={
        <button className="button small" type="button" onClick={() => loadPayload('fund')}>
          Fetch payload
        </button>
      }>
        <p className="muted">Returns the funding plan with wrap + transfer steps.</p>
      </Card>

      <Card title="Payload viewer">
        {loading ? <p>Loading payload...</p> : null}
        {error ? <div className="error-banner">{error}</div> : null}
        <pre className="code-block">{payload ? JSON.stringify(payload, null, 2) : 'No payload loaded.'}</pre>
      </Card>
    </div>
  )
}

export default TxHelper
