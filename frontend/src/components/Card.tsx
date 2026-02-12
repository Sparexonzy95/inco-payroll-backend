import type { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  title?: string
  actions?: ReactNode
}

const Card = ({ children, title, actions }: CardProps) => {
  return (
    <section className="card">
      {title ? (
        <header className="card-header">
          <h2>{title}</h2>
          {actions ? <div className="card-actions">{actions}</div> : null}
        </header>
      ) : null}
      <div className="card-body">{children}</div>
    </section>
  )
}

export default Card
