// Loads the exported 2025 hourly dataset. Path respects Vite's base so it works
// both at a domain root and under a GitHub Pages subpath.

let cache = null

export async function loadData() {
  if (cache) return cache
  const url = `${import.meta.env.BASE_URL}data/ercot_2025.json`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`)
  cache = await res.json()
  return cache
}

export async function loadBaselineMetrics() {
  const url = `${import.meta.env.BASE_URL}data/baseline_metrics.json`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`)
  return res.json()
}
