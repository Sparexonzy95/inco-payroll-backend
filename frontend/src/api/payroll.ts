import api from './http'
import type {
  CommitRunPayload,
  PayrollClaimResponse,
  PayrollRun,
  RunClaimsResponse,
  Schedule,
  SchedulePayload,
  ToggleSchedulePayload,
  TxPayload,
} from './types'

export const createSchedule = async (payload: SchedulePayload): Promise<Schedule> => {
  const response = await api.post<Schedule>('/api/payroll/schedules/create/', payload)
  return response.data
}

export const listSchedules = async (orgId: string): Promise<Schedule[]> => {
  const response = await api.get<Schedule[]>('/api/payroll/schedules/', { params: { org_id: orgId } })
  return response.data
}

export const toggleSchedule = async (
  scheduleId: number,
  payload: ToggleSchedulePayload,
): Promise<{ id: number; enabled: boolean }> => {
  const response = await api.post<{ id: number; enabled: boolean }>(
    `/api/payroll/schedules/${scheduleId}/toggle/`,
    payload,
  )
  return response.data
}

export const listRuns = async (orgId: string): Promise<PayrollRun[]> => {
  const response = await api.get<PayrollRun[]>('/api/payroll/runs/', { params: { org_id: orgId } })
  return response.data
}

/**
 * Backend endpoint is: POST /api/payroll/runs/create/
 * Your backend create_run expects: { org_id, payroll_id }
 * So we wire it exactly.
 */
export const createRun = async (payload: { org_id: string; payroll_id: number }): Promise<PayrollRun> => {
  const response = await api.post<PayrollRun>('/api/payroll/runs/create/', payload)
  return response.data
}

export const listRunClaims = async (runId: string | number): Promise<RunClaimsResponse> => {
  const response = await api.get<RunClaimsResponse>(`/api/payroll/runs/${runId}/claims/`)
  return response.data
}

export const commitRun = async (runId: string | number, payload: CommitRunPayload): Promise<PayrollRun> => {
  const response = await api.post<PayrollRun>(`/api/payroll/runs/${runId}/commit/`, payload)
  return response.data
}

export const getClaim = async (payrollId: string | number, wallet: string): Promise<PayrollClaimResponse> => {
  const response = await api.get<PayrollClaimResponse>(`/api/payroll/claims/${payrollId}/${wallet}/`)
  return response.data
}

export const txCreatePayroll = async (runId: string | number): Promise<TxPayload> => {
  const response = await api.post<TxPayload>(`/api/payroll/runs/${runId}/tx/createPayroll/`)
  return response.data
}

export const txFundPlan = async (runId: string | number): Promise<TxPayload> => {
  const response = await api.post<TxPayload>(`/api/payroll/runs/${runId}/tx/fundPlan/`)
  return response.data
}

export const openRun = async (runId: string | number): Promise<{ run_id: number; status: string }> => {
  const response = await api.post<{ run_id: number; status: string }>(`/api/payroll/runs/${runId}/open/`)
  return response.data
}
