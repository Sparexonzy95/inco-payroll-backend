import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Card from '../components/Card'
import FormField from '../components/FormField'
import { commitRun } from '../api/payroll'
import type { CommitItem } from '../api/types'

const ZERO_REF = '0x' + '00'.repeat(32)

const CommitRun = () => {
  const { runId } = useParams()
  const navigate = useNavigate()

  const [itemsJson, setItemsJson] = useState(
    '[\n  {\n    "wallet": "0x...",\n    "net_ciphertext_b64": "...",\n    "encrypted_ref": "0x..."\n  }\n]',
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    if (!runId) {
      setError('Missing run ID.')
      return
    }

    let raw: unknown
    try {
      raw = JSON.parse(itemsJson)
    } catch {
      setError('Invalid JSON. Provide a list (array) of items.')
      return
    }

    if (!Array.isArray(raw)) {
      setError('Payload must be a JSON array: [{ wallet, net_ciphertext_b64, encrypted_ref? }, ...]')
      return
    }

    // Validate + normalize items
    const items: CommitItem[] = raw.map((x: any, idx: number) => {
      const wallet = typeof x?.wallet === 'string' ? x.wallet : ''
      const net_ciphertext_b64 = typeof x?.net_ciphertext_b64 === 'string' ? x.net_ciphertext_b64 : ''
      const encrypted_ref = typeof x?.encrypted_ref === 'string' && x.encrypted_ref.length > 0 ? x.encrypted_ref : ZERO_REF

      if (!wallet || !net_ciphertext_b64) {
        throw new Error(`Item #${idx + 1} is missing wallet or net_ciphertext_b64`)
      }

      return { wallet, net_ciphertext_b64, encrypted_ref }
    })

    setLoading(true)
    try {
      await commitRun(runId, { items })
      setSuccess('Run committed. Merkle root updated.')
      navigate(`/runs/${runId}`)
    } catch {
      setError('Failed to commit run. Confirm run ID, wallets, and ciphertext payload.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Commit run</h1>
          <p className="muted">Run ID: {runId}</p>
        </div>
      </header>

      <Card title="Commit payload">
        <form className="stack" onSubmit={handleSubmit}>
          <FormField label="Items JSON">
            <textarea value={itemsJson} onChange={(event) => setItemsJson(event.target.value)} rows={14} />
          </FormField>

          {error ? <div className="error-banner">{error}</div> : null}
          {success ? <div className="success-banner">{success}</div> : null}

          <button className="button" type="submit" disabled={loading}>
            {loading ? 'Committing...' : 'Commit run'}
          </button>
        </form>
      </Card>
    </div>
  )
}

export default CommitRun
