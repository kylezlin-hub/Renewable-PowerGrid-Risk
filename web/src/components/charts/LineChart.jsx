import { useRef, useState, useMemo } from 'react'

// Reusable SVG line chart following the dataviz mark specs:
// thin 2px lines with round joins, recessive hairline grid, muted axes,
// an always-on legend for >=2 series, and a crosshair + tooltip on hover.
//
// props:
//   series: [{ name, color, points: [{x, y}] }]   (points share an x-domain)
//   yFormat, xFormat: (v) => string
//   xTicks: number[] (optional explicit tick positions)
//   refLines: [{ y, label, color }] (e.g. capacity line)
//   height: viewBox height (default 320)
//   markers: draw dots at each point (default false; off for dense series)

const VB_W = 720
const M = { top: 16, right: 18, bottom: 40, left: 64 }

export default function LineChart({
  series,
  yFormat = (v) => `${v}`,
  xFormat = (v) => `${v}`,
  xTicks,
  refLines = [],
  height = 320,
  markers = false,
  yLabel,
  xLabel,
}) {
  const wrapRef = useRef(null)
  const [hover, setHover] = useState(null) // {i, px, py}

  const VB_H = height
  const plot = {
    x: M.left,
    y: M.top,
    w: VB_W - M.left - M.right,
    h: VB_H - M.top - M.bottom,
  }

  const { xMin, xMax, yMin, yMax, xs } = useMemo(() => {
    let xmin = Infinity, xmax = -Infinity, ymin = Infinity, ymax = -Infinity
    const xset = series[0]?.points.map((p) => p.x) ?? []
    for (const s of series) {
      for (const p of s.points) {
        if (p.x < xmin) xmin = p.x
        if (p.x > xmax) xmax = p.x
        if (p.y < ymin) ymin = p.y
        if (p.y > ymax) ymax = p.y
      }
    }
    for (const r of refLines) {
      if (r.y < ymin) ymin = r.y
      if (r.y > ymax) ymax = r.y
    }
    // pad y a touch
    const pad = (ymax - ymin) * 0.06 || 1
    return { xMin: xmin, xMax: xmax, yMin: ymin - pad, yMax: ymax + pad, xs: xset }
  }, [series, refLines])

  const sx = (x) => plot.x + ((x - xMin) / (xMax - xMin || 1)) * plot.w
  const sy = (y) => plot.y + plot.h - ((y - yMin) / (yMax - yMin || 1)) * plot.h

  const yTickVals = useMemo(() => {
    const n = 4
    const out = []
    for (let i = 0; i <= n; i++) out.push(yMin + ((yMax - yMin) * i) / n)
    return out
  }, [yMin, yMax])

  const xTickVals = xTicks ?? autoTicks(xMin, xMax, 6)

  const pathFor = (pts) =>
    pts
      .filter((p) => p.y != null && !Number.isNaN(p.y))
      .map((p, i) => `${i === 0 ? 'M' : 'L'}${sx(p.x).toFixed(1)},${sy(p.y).toFixed(1)}`)
      .join(' ')

  function onMove(e) {
    const rect = wrapRef.current.getBoundingClientRect()
    const svgX = ((e.clientX - rect.left) / rect.width) * VB_W
    // nearest index in shared x domain
    let best = 0, bestd = Infinity
    for (let i = 0; i < xs.length; i++) {
      const d = Math.abs(sx(xs[i]) - svgX)
      if (d < bestd) { bestd = d; best = i }
    }
    setHover({ i: best })
  }

  const hoverX = hover != null ? xs[hover.i] : null

  return (
    <div className="chart-wrap" ref={wrapRef}>
      <svg
        viewBox={`0 0 ${VB_W} ${VB_H}`}
        style={{ width: '100%', height: 'auto', display: 'block' }}
        onMouseMove={onMove}
        onMouseLeave={() => setHover(null)}
        role="img"
      >
        {/* y grid + labels */}
        {yTickVals.map((v, i) => (
          <g key={`y${i}`}>
            <line
              x1={plot.x} x2={plot.x + plot.w}
              y1={sy(v)} y2={sy(v)}
              stroke="var(--gridline)" strokeWidth="1"
            />
            <text x={plot.x - 8} y={sy(v) + 4} textAnchor="end"
              fontSize="11" fill="var(--text-muted)" style={{ fontVariantNumeric: 'tabular-nums' }}>
              {yFormat(v)}
            </text>
          </g>
        ))}
        {/* x axis baseline + ticks */}
        <line x1={plot.x} x2={plot.x + plot.w} y1={sy(yMin)} y2={sy(yMin)}
          stroke="var(--baseline)" strokeWidth="1" />
        {xTickVals.map((v, i) => (
          <text key={`x${i}`} x={sx(v)} y={plot.y + plot.h + 20} textAnchor="middle"
            fontSize="11" fill="var(--text-muted)">
            {xFormat(v)}
          </text>
        ))}

        {/* reference lines (e.g. capacity) */}
        {refLines.map((r, i) => (
          <g key={`r${i}`}>
            <line x1={plot.x} x2={plot.x + plot.w} y1={sy(r.y)} y2={sy(r.y)}
              stroke={r.color || 'var(--status-critical)'} strokeWidth="1.5"
              strokeDasharray="5 4" />
            <text x={plot.x + plot.w} y={sy(r.y) - 5} textAnchor="end"
              fontSize="11" fill={r.color || 'var(--status-critical)'}>
              {r.label}
            </text>
          </g>
        ))}

        {/* series */}
        {series.map((s, si) => (
          <path key={si} d={pathFor(s.points)} fill="none" stroke={s.color}
            strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
        ))}

        {/* markers */}
        {markers && series.map((s, si) =>
          s.points.map((p, pi) =>
            p.y == null || Number.isNaN(p.y) ? null : (
              <circle key={`${si}-${pi}`} cx={sx(p.x)} cy={sy(p.y)} r="3.5"
                fill={s.color} stroke="var(--surface-1)" strokeWidth="1.5" />
            ),
          ),
        )}

        {/* crosshair */}
        {hoverX != null && (
          <line x1={sx(hoverX)} x2={sx(hoverX)} y1={plot.y} y2={plot.y + plot.h}
            stroke="var(--text-muted)" strokeWidth="1" strokeDasharray="3 3" />
        )}
        {hoverX != null && series.map((s, si) => {
          const p = s.points[hover.i]
          if (!p || p.y == null || Number.isNaN(p.y)) return null
          return <circle key={`h${si}`} cx={sx(p.x)} cy={sy(p.y)} r="4"
            fill={s.color} stroke="var(--surface-1)" strokeWidth="2" />
        })}

        {/* axis labels */}
        {yLabel && (
          <text x={14} y={plot.y + plot.h / 2} transform={`rotate(-90 14 ${plot.y + plot.h / 2})`}
            textAnchor="middle" fontSize="11" fill="var(--text-secondary)">{yLabel}</text>
        )}
        {xLabel && (
          <text x={plot.x + plot.w / 2} y={VB_H - 4} textAnchor="middle"
            fontSize="11" fill="var(--text-secondary)">{xLabel}</text>
        )}
      </svg>

      {hoverX != null && (
        <Tooltip
          wrapRef={wrapRef} vbW={VB_W} hoverPx={sx(hoverX)}
          xLabel={xFormat(hoverX)} series={series} i={hover.i} yFormat={yFormat}
        />
      )}

      {series.length >= 2 && (
        <div className="legend">
          {series.map((s, i) => (
            <span className="item" key={i}>
              <span className="swatch" style={{ background: s.color }} />
              {s.name}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

function Tooltip({ wrapRef, vbW, hoverPx, xLabel, series, i, yFormat }) {
  // position as a % of width so it tracks the responsive SVG
  const leftPct = (hoverPx / vbW) * 100
  const flip = leftPct > 60
  return (
    <div
      className="tooltip"
      style={{
        left: `${leftPct}%`,
        top: 8,
        transform: flip ? 'translateX(-110%)' : 'translateX(10px)',
      }}
    >
      <div style={{ color: 'var(--text-secondary)', marginBottom: 4 }}>{xLabel}</div>
      {series.map((s, si) => {
        const p = s.points[i]
        if (!p || p.y == null || Number.isNaN(p.y)) return null
        return (
          <div key={si} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span className="swatch" style={{ background: s.color, width: 10, height: 10, borderRadius: 2 }} />
            <span style={{ color: 'var(--text-secondary)' }}>{s.name}</span>
            <span style={{ marginLeft: 'auto', fontWeight: 600 }}>{yFormat(p.y)}</span>
          </div>
        )
      })}
    </div>
  )
}

function autoTicks(min, max, count) {
  const step = niceStep((max - min) / count)
  const start = Math.ceil(min / step) * step
  const out = []
  for (let v = start; v <= max + 1e-9; v += step) out.push(Math.round(v))
  return out
}
function niceStep(raw) {
  const mag = Math.pow(10, Math.floor(Math.log10(raw || 1)))
  const norm = raw / mag
  const nice = norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10
  return nice * mag
}
