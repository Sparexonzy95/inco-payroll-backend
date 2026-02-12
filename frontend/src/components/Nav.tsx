import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'

const Nav = () => {
  const { logout, me } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="nav">
      <div className="nav-header">
        <h1>Inco Payroll</h1>
        {me?.wallet ? <p className="muted">{me.wallet}</p> : null}
        {me?.active_org_id ? <p className="muted">Org #{me.active_org_id}</p> : null}
      </div>
      <nav className="nav-links">
        <NavLink to="/" end>
          Dashboard
        </NavLink>
        <NavLink to="/org-select">Select Org</NavLink>
        <NavLink to="/schedules">Schedules</NavLink>
        <NavLink to="/runs">Runs</NavLink>
        <NavLink to="/employee-claim">Employee Claim</NavLink>
      </nav>
      <button className="button secondary" type="button" onClick={handleLogout}>
        Logout
      </button>
    </aside>
  )
}

export default Nav
