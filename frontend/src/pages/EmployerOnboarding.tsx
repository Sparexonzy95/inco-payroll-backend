import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'
import Card from '../components/Card'
import FormField from '../components/FormField'

const EmployerOnboarding = () => {
  const { submitEmployerOnboarding } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await submitEmployerOnboarding(name, email)
      navigate('/')
    } catch {
      setError('Unable to register employer profile. Check name/email and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Employer onboarding</h1>
      </header>
      <Card title="Complete your profile">
        <form className="stack" onSubmit={handleSubmit}>
          <FormField label="Company/Employer name">
            <input value={name} onChange={(event) => setName(event.target.value)} required />
          </FormField>
          <FormField label="Email">
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </FormField>
          {error ? <div className="error-banner">{error}</div> : null}
          <button className="button" type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save and continue'}
          </button>
        </form>
      </Card>
    </div>
  )
}

export default EmployerOnboarding
