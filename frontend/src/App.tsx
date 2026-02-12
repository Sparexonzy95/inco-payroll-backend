import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthProvider'
import RequireAuth from './auth/RequireAuth'
import Layout from './components/Layout'
import CommitRun from './pages/CommitRun'
import CreateRun from './pages/CreateRun'
import EmployeeClaim from './pages/EmployeeClaim'
import EmployerDashboard from './pages/EmployerDashboard'
import EmployerOnboarding from './pages/EmployerOnboarding'
import Login from './pages/Login'
import RunDetail from './pages/RunDetail'
import Runs from './pages/Runs'
import Schedules from './pages/Schedules'
import TxHelper from './pages/TxHelper'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<RequireAuth />}>
              <Route path="/employer-onboarding" element={<EmployerOnboarding />} />
              <Route path="/" element={<EmployerDashboard />} />
              <Route path="/schedules" element={<Schedules />} />
              <Route path="/runs" element={<Runs />} />
              <Route path="/runs/create" element={<CreateRun />} />
              <Route path="/runs/:runId" element={<RunDetail />} />
              <Route path="/runs/:runId/commit" element={<CommitRun />} />
              <Route path="/runs/:runId/tx" element={<TxHelper />} />
              <Route path="/employee-claim" element={<EmployeeClaim />} />
            </Route>
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
