import { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import Nav from './Nav'
import { useAuth } from '../auth/AuthProvider'

interface LayoutProps {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation()
  const { isAuthenticated } = useAuth()
  const showNav = isAuthenticated && location.pathname !== '/login'

  return (
    <div className="app-shell">
      {showNav ? <Nav /> : null}
      <main className={showNav ? 'app-main' : 'app-main full'}>{children}</main>
    </div>
  )
}

export default Layout
