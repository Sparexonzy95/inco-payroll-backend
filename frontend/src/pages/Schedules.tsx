import { useEffect, useState } from 'react'
import Card from '../components/Card'
import FormField from '../components/FormField'
import Table from '../components/Table'
import { createSchedule, listSchedules, toggleSchedule } from '../api/payroll'
import type { Schedule, SchedulePayload, ScheduleType } from '../api/types'
import { formatDateTime } from '../utils/format'
import { validateSchedulePayload } from '../utils/validators'
import { tokenStore } from '../auth/tokenStore'

const scheduleTypes: ScheduleType[] = ['instant', 'daily', 'weekly', 'monthly', 'yearly']

const Schedules = () => {
  const [orgId, setOrgId] = useState(tokenStore.getOrgId() ?? '')
  const [name, setName] = useState('')
  const [scheduleType, setScheduleType] = useState<ScheduleType>('instant')
  const [timeOfDay, setTimeOfDay] = useState('09:00')
  const [weekday, setWeekday] = useState('')
  const [dayOfMonth, setDayOfMonth] = useState('')
  const [monthOfYear, setMonthOfYear] = useState('')
  const [dayOfYear, setDayOfYear] = useState('')
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const loadSchedules = async (currentOrgId = orgId) => {
    if (!currentOrgId) return
    setLoading(true)
    setError(null)
    try {
      const data = await listSchedules(currentOrgId)
      setSchedules(data)
    } catch (err) {
      setError('Failed to load schedules.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (orgId) {
      tokenStore.setOrgId(orgId)
      void loadSchedules(orgId)
    }
  }, [orgId])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    const payload: SchedulePayload = {
      org_id: orgId,
      name,
      schedule_type: scheduleType,
      time_of_day: scheduleType === 'instant' ? undefined : timeOfDay,
      weekday: weekday ? Number(weekday) : undefined,
      day_of_month: dayOfMonth ? Number(dayOfMonth) : undefined,
      month_of_year: monthOfYear ? Number(monthOfYear) : undefined,
      day_of_year: dayOfYear ? Number(dayOfYear) : undefined,
    }

    const errors = validateSchedulePayload(payload)
    setFieldErrors(errors)
    if (Object.keys(errors).length > 0) return

    setLoading(true)
    setError(null)
    try {
      await createSchedule(payload)
      setName('')
      await loadSchedules()
    } catch (err) {
      setError('Unable to create schedule. Check the form values.')
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = async (schedule: Schedule) => {
    setError(null)
    try {
      await toggleSchedule(schedule.id, { enabled: !schedule.enabled })
      await loadSchedules()
    } catch (err) {
      setError('Unable to toggle schedule.')
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Schedules</h1>
          <p className="muted">Create automated payroll schedules.</p>
        </div>
      </header>

      <div className="grid two">
        <Card title="Create schedule">
          <form onSubmit={handleSubmit} className="stack">
            <FormField label="Organization ID" error={fieldErrors.org_id}>
              <input value={orgId} onChange={(event) => setOrgId(event.target.value)} required />
            </FormField>
            <FormField label="Schedule name" error={fieldErrors.name}>
              <input value={name} onChange={(event) => setName(event.target.value)} required />
            </FormField>
            <FormField label="Schedule type" error={fieldErrors.schedule_type}>
              <select value={scheduleType} onChange={(event) => setScheduleType(event.target.value as ScheduleType)}>
                {scheduleTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </FormField>
            {scheduleType !== 'instant' ? (
              <FormField label="Time of day" hint="HH:MM" error={fieldErrors.time_of_day}>
                <input type="time" value={timeOfDay} onChange={(event) => setTimeOfDay(event.target.value)} />
              </FormField>
            ) : null}
            {scheduleType === 'weekly' ? (
              <FormField label="Weekday (0=Sun)" error={fieldErrors.weekday}>
                <input value={weekday} onChange={(event) => setWeekday(event.target.value)} type="number" min={0} max={6} />
              </FormField>
            ) : null}
            {scheduleType === 'monthly' ? (
              <FormField label="Day of month" error={fieldErrors.day_of_month}>
                <input
                  value={dayOfMonth}
                  onChange={(event) => setDayOfMonth(event.target.value)}
                  type="number"
                  min={1}
                  max={31}
                />
              </FormField>
            ) : null}
            {scheduleType === 'yearly' ? (
              <>
                <FormField label="Month of year" error={fieldErrors.month_of_year}>
                  <input
                    value={monthOfYear}
                    onChange={(event) => setMonthOfYear(event.target.value)}
                    type="number"
                    min={1}
                    max={12}
                  />
                </FormField>
                <FormField label="Day of year" error={fieldErrors.day_of_year}>
                  <input
                    value={dayOfYear}
                    onChange={(event) => setDayOfYear(event.target.value)}
                    type="number"
                    min={1}
                    max={31}
                  />
                </FormField>
              </>
            ) : null}
            {error ? <div className="error-banner">{error}</div> : null}
            <button className="button" type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Create schedule'}
            </button>
          </form>
        </Card>

        <Card title="Schedule list">
          {loading ? <p>Loading schedules...</p> : null}
          <Table headers={[
            'ID',
            'Name',
            'Type',
            'Next run',
            'Enabled',
            'Actions',
          ]}>
            {schedules.map((schedule) => (
              <tr key={schedule.id}>
                <td>{schedule.id}</td>
                <td>{schedule.name}</td>
                <td>{schedule.schedule_type}</td>
                <td>{formatDateTime(schedule.next_run_at)}</td>
                <td>{schedule.enabled ? 'Yes' : 'No'}</td>
                <td>
                  <button
                    className="button small"
                    type="button"
                    onClick={() => handleToggle(schedule)}
                  >
                    {schedule.enabled ? 'Disable' : 'Enable'}
                  </button>
                </td>
              </tr>
            ))}
          </Table>
        </Card>
      </div>
    </div>
  )
}

export default Schedules
