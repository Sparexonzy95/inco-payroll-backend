import type { SchedulePayload } from "../api/types";


export const validateSchedulePayload = (payload: SchedulePayload) => {
  const errors: Record<string, string> = {}

  if (!payload.org_id) {
    errors.org_id = 'Organization ID is required.'
  }
  if (!payload.name) {
    errors.name = 'Schedule name is required.'
  }
  if (!payload.schedule_type) {
    errors.schedule_type = 'Schedule type is required.'
  }

  const requiresTime = payload.schedule_type !== 'instant'
  if (requiresTime && !payload.time_of_day) {
    errors.time_of_day = 'Time of day is required.'
  }

  if (payload.schedule_type === 'weekly' && payload.weekday === undefined) {
    errors.weekday = 'Weekday is required for weekly schedules.'
  }
  if (payload.schedule_type === 'monthly' && payload.day_of_month === undefined) {
    errors.day_of_month = 'Day of month is required for monthly schedules.'
  }
  if (payload.schedule_type === 'yearly') {
    if (payload.month_of_year === undefined) {
      errors.month_of_year = 'Month of year is required for yearly schedules.'
    }
    if (payload.day_of_year === undefined) {
      errors.day_of_year = 'Day of year is required for yearly schedules.'
    }
  }

  return errors
}
