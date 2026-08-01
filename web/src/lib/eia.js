// Live ERCOT grid data from the EIA Open Data API v2 (respondent "ERCO").
// Docs: https://www.eia.gov/opendata/  · v2 supports browser CORS.
// The key comes from VITE_EIA_API_KEY (see .env.example).

const BASE = 'https://api.eia.gov/v2/electricity/rto'
const KEY = import.meta.env.VITE_EIA_API_KEY

export function hasKey() {
  return !!KEY && KEY !== 'your_eia_api_key_here'
}

// Fuel display config: known ERCOT fuel codes in a fixed order, each mapped to a
// categorical color slot. Anything else folds into "Other".
export const FUELS = [
  { code: 'NG', name: 'Natural gas', color: 'var(--series-1)' },
  { code: 'WND', name: 'Wind', color: 'var(--series-3)' },
  { code: 'SUN', name: 'Solar', color: 'var(--series-4)' },
  { code: 'NUC', name: 'Nuclear', color: 'var(--series-7)' },
  { code: 'COL', name: 'Coal', color: 'var(--series-2)' },
  { code: 'WAT', name: 'Hydro', color: 'var(--series-5)' },
]
const RENEWABLE = new Set(['WND', 'SUN', 'WAT'])

async function eiaGet(path, params) {
  const url = new URL(`${BASE}/${path}/data/`)
  url.searchParams.set('api_key', KEY)
  url.searchParams.set('frequency', 'hourly')
  url.searchParams.append('data[0]', 'value')
  for (const [k, v] of params) url.searchParams.append(k, v)
  const res = await fetch(url)
  if (!res.ok) throw new Error(`EIA API ${res.status}`)
  const json = await res.json()
  return json?.response?.data ?? []
}

// Last `hours` of ERCOT demand (type D), ascending by period.
export async function fetchDemand(hours = 24) {
  const rows = await eiaGet('region-data', [
    ['facets[respondent][]', 'ERCO'],
    ['facets[type][]', 'D'],
    ['sort[0][column]', 'period'],
    ['sort[0][direction]', 'desc'],
    ['length', String(hours)],
  ])
  return rows
    .map((r) => ({ period: r.period, value: Number(r.value) }))
    .filter((r) => Number.isFinite(r.value))
    .sort((a, b) => (a.period < b.period ? -1 : 1))
}

// Generation by fuel type for the most recent hour available.
export async function fetchFuelMix() {
  const rows = await eiaGet('fuel-type-data', [
    ['facets[respondent][]', 'ERCO'],
    ['sort[0][column]', 'period'],
    ['sort[0][direction]', 'desc'],
    ['length', '250'],
  ])
  if (!rows.length) return null

  const latest = rows.reduce((m, r) => (r.period > m ? r.period : m), rows[0].period)
  const byCode = {}
  for (const r of rows) {
    if (r.period !== latest) continue
    const v = Number(r.value)
    if (Number.isFinite(v)) byCode[r.fueltype] = (byCode[r.fueltype] || 0) + v
  }

  const segments = []
  let other = 0
  let renewable = 0
  let total = 0
  const known = new Set(FUELS.map((f) => f.code))
  for (const [code, v] of Object.entries(byCode)) {
    const val = Math.max(v, 0)
    total += val
    if (RENEWABLE.has(code)) renewable += val
    if (!known.has(code)) other += val
  }
  for (const f of FUELS) {
    if (byCode[f.code] > 0) segments.push({ name: f.name, value: byCode[f.code], color: f.color })
  }
  if (other > 0) segments.push({ name: 'Other', value: other, color: 'var(--text-muted)' })

  return { period: latest, segments, renewableShare: total ? renewable / total : 0, total }
}
