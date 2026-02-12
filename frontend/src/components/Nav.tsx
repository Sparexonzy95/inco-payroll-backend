import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'

const Nav = () => {
  const { logout, username } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="nav">
      <div className="nav-header">
        <h1>Inco Payroll</h1>
        {username ? <p className="muted">{username}</p> : null}
      </div>
      <nav className="nav-links">
        <NavLink to="/" end>
          Dashboard
        </NavLink>
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
