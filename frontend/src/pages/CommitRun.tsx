import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import Card from '../components/Card'
import FormField from '../components/FormField'
import { commitRun } from '../api/payroll'
import { CommitItem } from '../api/types'

const CommitRun = () => {
  const { runId } = useParams()
  const navigate = useNavigate()
  const [itemsJson, setItemsJson] = useState('[\n  {\n    "wallet": "0x...",\n    "net_ciphertext_b64": "...",\n    "encrypted_ref": "0x..."\n  }\n]')
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

    let items: CommitItem[]
    try {
      items = JSON.parse(itemsJson) as CommitItem[]
    } catch (err) {
      setError('Invalid JSON. Provide a list of items.')
      return
    }

    setLoading(true)
    try {
      await commitRun(runId, { items })
      setSuccess('Run committed. Merkle root updated.')
      navigate(`/runs/${runId}`)
    } catch (err) {
      setError('Failed to commit run. Ensure ciphertexts match run size.')
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
            <textarea value={itemsJson} onChange={(event) => setItemsJson(event.target.value)} rows={12} />
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
