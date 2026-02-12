import { ReactNode } from 'react'

interface FormFieldProps {
  label: string
  children: ReactNode
  hint?: string
  error?: string
}

const FormField = ({ label, children, hint, error }: FormFieldProps) => {
  return (
    <label className="form-field">
      <span>{label}</span>
      {children}
      {hint ? <small className="muted">{hint}</small> : null}
      {error ? <small className="error">{error}</small> : null}
    </label>
  )
}

export default FormField
