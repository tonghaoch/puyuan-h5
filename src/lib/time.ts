export function shanghaiDate(date: Date): string {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(date)
  const part = (type: string) => parts.find((p) => p.type === type)?.value ?? ''
  return `${part('year')}-${part('month')}-${part('day')}`
}
export function shiftDay(day: string, offset: number): string {
  const date = new Date(`${day}T12:00:00+08:00`)
  date.setTime(date.getTime() + offset * 86400000)
  return shanghaiDate(date)
}
export function sessionStatus(
  sessions: { start: string; end: string }[],
  now = Date.now(),
): 'ongoing' | 'upcoming' | 'ended' {
  if (sessions.some((s) => Date.parse(s.start) <= now && now < Date.parse(s.end))) return 'ongoing'
  if (sessions.some((s) => Date.parse(s.start) > now)) return 'upcoming'
  return 'ended'
}
export function dayLabel(start: string, now = new Date()): string {
  const day = shanghaiDate(new Date(start))
  if (day === shanghaiDate(now)) return '今天'
  if (day === shiftDay(shanghaiDate(now), 1)) return '明天'
  return new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai',
    month: 'numeric',
    day: 'numeric',
  }).format(new Date(start))
}
