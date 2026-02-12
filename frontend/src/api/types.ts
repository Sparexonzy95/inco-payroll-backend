export type ScheduleType = 'instant' | 'daily' | 'weekly' | 'monthly' | 'yearly'

export interface OrgMembership {
  id: number
  name: string
  role: string
}

export interface MeResponse {
  user_id: number
  wallet: string | null
  roles: string[]
  active_org_id: number | null
  orgs: OrgMembership[]
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
    id: number
    username: string
    wallet: string | null
    roles: string[]
    orgs: OrgMembership[]
    active_org_id: number | null
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

export interface RunClaimItem {
  index: number
  employee_wallet: string
  status: string
  salary_units: number | null
  leaf: string
  has_ciphertext: boolean
  claim_tx_hash?: string | null
  claimed_at?: string | null
}

export interface RunClaimsResponse {
  run_id: number
  payroll_id: string
  status: string
  merkle_root: string
  total: number
  total_amount_units: number
  claims: RunClaimItem[]
}

export interface CommitItem {
  wallet: string
  net_ciphertext_b64: string
  encrypted_ref: string
}

export interface CommitRunPayload {
  items: CommitItem[]
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
