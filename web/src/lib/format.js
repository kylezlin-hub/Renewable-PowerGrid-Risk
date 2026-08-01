// Display formatting helpers.

export function fmtMW(v) {
  if (v == null || Number.isNaN(v)) return '—'
  return `${Math.round(v).toLocaleString()} MW`
}

export function fmtGW(v) {
  if (v == null || Number.isNaN(v)) return '—'
  return `${(v / 1000).toFixed(1)} GW`
}

export function fmtPct(v, digits = 1) {
  if (v == null || Number.isNaN(v)) return '—'
  return `${(v * 100).toFixed(digits)}%`
}

export function fmtInt(v) {
  if (v == null || Number.isNaN(v)) return '—'
  return Math.round(v).toLocaleString()
}

// Signed delta string, e.g. "+3,412" or "−0.8".
export function fmtDelta(v, kind = 'int') {
  if (v == null || Number.isNaN(v)) return ''
  const sign = v > 0 ? '+' : v < 0 ? '−' : ''
  const mag = Math.abs(v)
  if (kind === 'pct') return `${sign}${(mag * 100).toFixed(1)} pp`
  if (kind === 'mw') return `${sign}${Math.round(mag).toLocaleString()} MW`
  return `${sign}${Math.round(mag).toLocaleString()}`
}
