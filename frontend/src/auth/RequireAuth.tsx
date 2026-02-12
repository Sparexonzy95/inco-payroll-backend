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

  if (me && !me.is_employer_registered && location.pathname !== '/employer-onboarding' && location.pathname !== '/employee-claim') {
    return <Navigate to="/employer-onboarding" replace />
  }

  return <Outlet />
}

export default RequireAuth
