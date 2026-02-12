import { Link } from 'react-router-dom'
import Card from '../components/Card'

const EmployerDashboard = () => {
  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Employer Dashboard</h1>
          <p className="muted">Manage payroll schedules, runs, and on-chain actions.</p>
        </div>
      </header>

      <div className="grid">
        <Card title="Schedules">
          <p>Create payroll schedules and enable or disable them.</p>
          <Link className="button secondary" to="/schedules">
            Manage schedules
          </Link>
        </Card>
        <Card title="Runs">
          <p>Create instant payroll runs, commit ciphertexts, and open runs.</p>
          <Link className="button secondary" to="/runs">
            View runs
          </Link>
        </Card>
        <Card title="Employee Claim">
          <p>Retrieve claim payloads for employees once a run is open.</p>
          <Link className="button secondary" to="/employee-claim">
            Lookup claim
          </Link>
        </Card>
      </div>
    </div>
  )
}

export default EmployerDashboard
