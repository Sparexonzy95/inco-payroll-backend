import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'
import Card from '../components/Card'

const OrgSelect = () => {
  const { me, selectActiveOrg } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  const handleSelect = async (orgId: number) => {
    setError(null)
    try {
      await selectActiveOrg(orgId)
      navigate('/')
    } catch {
      setError('Unable to set active organization.')
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Select active organization</h1>
      </header>
      {error ? <div className="error-banner">{error}</div> : null}
      <div className="grid">
        {me?.orgs.map((org) => (
          <Card key={org.id} title={org.name}>
            <p className="muted">Role: {org.role}</p>
            <button className="button" type="button" onClick={() => handleSelect(org.id)}>
              Use this org
            </button>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default OrgSelect
