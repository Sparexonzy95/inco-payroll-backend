import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthProvider'

const RequireAuth = () => {
  const { isAuthenticated, me, loadingMe } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (loadingMe) {
    return <p>Loading profile...</p>
  }

  if (me && me.orgs.length > 0 && !me.active_org_id && location.pathname !== '/org-select') {
    return <Navigate to="/org-select" replace />
  }

  return <Outlet />
}

export default RequireAuth
