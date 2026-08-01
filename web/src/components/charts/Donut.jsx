// Generation-mix donut. Segments carry their own categorical colors (assigned in
// fixed order by the caller). Identity is never color-alone: every segment is
// direct-labeled in the legend with its value and share.

export default function Donut({ segments, centerTop, centerBottom, size = 200 }) {
  const total = segments.reduce((s, seg) => s + Math.max(seg.value, 0), 0) || 1
  const r = size / 2
  const inner = r * 0.62
  const cx = r
  const cy = r
  let angle = -Math.PI / 2 // start at top
  const gap = 0.012 // radians, the 2px surface gap between fills

  const arcs = segments.map((seg) => {
    const frac = Math.max(seg.value, 0) / total
    const a0 = angle + gap / 2
    const a1 = angle + frac * 2 * Math.PI - gap / 2
    angle += frac * 2 * Math.PI
    const large = a1 - a0 > Math.PI ? 1 : 0
    const p = (rad, ang) => [cx + rad * Math.cos(ang), cy + rad * Math.sin(ang)]
    const [x0o, y0o] = p(r, a0)
    const [x1o, y1o] = p(r, a1)
    const [x1i, y1i] = p(inner, a1)
    const [x0i, y0i] = p(inner, a0)
    const d = `M${x0o},${y0o} A${r},${r} 0 ${large} 1 ${x1o},${y1o} L${x1i},${y1i} A${inner},${inner} 0 ${large} 0 ${x0i},${y0i} Z`
    return { d, seg, frac }
  })

  return (
    <div style={{ display: 'flex', gap: 20, alignItems: 'center', flexWrap: 'wrap' }}>
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} role="img">
        {arcs.map((a, i) => (
          <path key={i} d={a.d} fill={a.seg.color} stroke="var(--surface-1)" strokeWidth="2" />
        ))}
        {centerTop && (
          <text x={cx} y={cy - 2} textAnchor="middle" fontSize="20" fontWeight="700"
            fill="var(--text-primary)">{centerTop}</text>
        )}
        {centerBottom && (
          <text x={cx} y={cy + 16} textAnchor="middle" fontSize="11"
            fill="var(--text-secondary)">{centerBottom}</text>
        )}
      </svg>
      <div className="legend" style={{ flexDirection: 'column', gap: 6 }}>
        {arcs.map((a, i) => (
          <span className="item" key={i}>
            <span className="swatch" style={{ background: a.seg.color }} />
            <span style={{ color: 'var(--text-secondary)' }}>{a.seg.name}</span>
            <span style={{ marginLeft: 8, fontWeight: 600, color: 'var(--text-primary)' }}>
              {(a.frac * 100).toFixed(0)}%
            </span>
          </span>
        ))}
      </div>
    </div>
  )
}
