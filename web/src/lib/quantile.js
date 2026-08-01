// Percentile with linear interpolation between order statistics — matches
// numpy's default ("linear" / type-7), which is what pandas Series.quantile uses.
// NaN/undefined values are skipped (as pandas does).

export function quantile(values, q) {
  const xs = []
  for (const v of values) {
    if (v !== null && v !== undefined && !Number.isNaN(v)) xs.push(v)
  }
  if (xs.length === 0) return NaN
  xs.sort((a, b) => a - b)
  if (xs.length === 1) return xs[0]
  const h = (xs.length - 1) * q
  const lo = Math.floor(h)
  const frac = h - lo
  if (lo + 1 >= xs.length) return xs[lo]
  return xs[lo] + frac * (xs[lo + 1] - xs[lo])
}

// Population (ddof=0) or sample (ddof=1) variance, skipping NaN.
export function variance(values, ddof = 0) {
  const xs = values.filter((v) => v !== null && v !== undefined && !Number.isNaN(v))
  const n = xs.length
  if (n - ddof <= 0) return NaN
  const mean = xs.reduce((s, v) => s + v, 0) / n
  const ss = xs.reduce((s, v) => s + (v - mean) * (v - mean), 0)
  return ss / (n - ddof)
}

export function mean(values) {
  const xs = values.filter((v) => v !== null && v !== undefined && !Number.isNaN(v))
  if (xs.length === 0) return NaN
  return xs.reduce((s, v) => s + v, 0) / xs.length
}
