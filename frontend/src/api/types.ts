export type ScheduleType = 'instant' | 'daily' | 'weekly' | 'monthly' | 'yearly'

export interface EmployerProfile {
  id: number
  name: string
  email: string
  wallet_address: string
  is_active: boolean
  created_at: string
}

export interface MeResponse {
  wallet: string | null
  is_employer_registered: boolean
  employer: EmployerProfile | null
}

export interface WalletNonceResponse {
  wallet: string
  nonce: string
  message: string
}

export interface WalletLoginResponse {
  access: string
  refresh: string
  user: {
    wallet: string | null
    is_employer_registered: boolean
    employer: EmployerProfile | null
  }
}

export interface Schedule {
  id: number
  name: string
  schedule_type: ScheduleType
  time_of_day?: string | null
  weekday?: number | null
  day_of_month?: number | null
  month_of_year?: number | null
  day_of_year?: number | null
  next_run_at?: string | null
  enabled: boolean
  created_at?: string
}

export interface SchedulePayload {
  name: string
  schedule_type: ScheduleType
  time_of_day?: string
  weekday?: number
  day_of_month?: number
  month_of_year?: number
  day_of_year?: number
}

export interface ToggleSchedulePayload {
  enabled: boolean
}

export interface PayrollRun {
  id?: number
  run_id?: number
  payroll_id: string
  token?: string
  vault?: string
  merkle_root?: string
  total?: number
  total_amount_units?: number
  status?: string
  create_tx_hash?: string | null
  fund_tx_hash?: string | null
  claim_window_days?: number
  close_at?: string
  created_at?: string
}

export interface RunClaim {
  index: number
  employee_wallet: string
  status: string
  salary_units?: number | null
  leaf?: string
  has_ciphertext?: boolean
  claim_tx_hash?: string
  claimed_at?: string | null
}

export interface RunClaimsResponse {
  run_id: number
  payroll_id: string
  status: string
  merkle_root: string
  total: number
  total_amount_units: number
  claims: RunClaim[]
}

export interface CommitRunItem {
  wallet: string
  net_ciphertext_b64: string
  encrypted_ref?: string
}

export interface CommitRunPayload {
  items: CommitRunItem[]
}

export interface PayrollClaimResponse {
  payroll_id: string
  index: number
  token: string
  vault: string
  net_ciphertext_b64: string
  encrypted_ref: string
  proof: string[]
}

export interface TxPayload {
  [key: string]: unknown
}
