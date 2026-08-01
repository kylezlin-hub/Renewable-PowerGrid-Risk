# ERCOT Grid Risk Simulator (web)

An interactive, static website that explains how the ERCOT power grid balances supply and demand,
then lets visitors scale solar/wind/battery and watch net-load ramping risk respond — computed live
in the browser from the project's 2025 ERCOT data, using the same math as `src/metrics.py`. A live
panel shows the current ERCOT grid via the EIA Open Data API.

## Stack

- **React + Vite** (static build, no backend)
- Hand-rolled SVG charts (validated dataviz palette; light/dark)
- All scenario math runs client-side; verified against the Python metrics via a dev self-test

## Prerequisites

- **Node 20+** and npm (for local dev/build). Not required to deploy — GitHub Actions builds it.
- **Python 3** with `pandas` (only to re-export the data JSON).

## Local development

```bash
cd web
npm install
npm run dev          # http://localhost:5173
```

In dev, open the browser console: a self-test recomputes the risk metrics in JS for all four
scenarios and confirms they match the Python-exported targets (`✓` on success).

## Data

The site reads two committed files in `public/data/`:

- `ercot_2025.json` — compact hourly load/solar/wind for 2025 (~414 KB)
- `baseline_metrics.json` — Python-computed validation targets for the self-test

To regenerate them from the project's processed dataset:

```bash
npm run export-data          # runs scripts/export_data.py
# (requires data/processed/hourly_load_renewable_merged.csv from notebook 01)
```

The exporter rounds the hourly values to 1 decimal and computes the validation targets from those
same rounded values, so the browser reproduces them exactly.

## Live data (EIA) key

The "current grid" panel uses the free EIA Open Data API v2.

1. Get a key at <https://www.eia.gov/opendata/register.php>.
2. Local: copy `.env.example` to `.env` and set `VITE_EIA_API_KEY`.
3. Deploy: add a GitHub Actions repository secret named `VITE_EIA_API_KEY`.

The key is embedded in the client bundle (visible in page source). EIA keys are free and read-only,
so this is acceptable for a public demo. If the key is absent, the panel shows a friendly notice and
the rest of the simulator works normally.

## Deploy (GitHub Pages)

`.github/workflows/deploy.yml` (at the repo root) builds `web/` and publishes to GitHub Pages on any
push to `main` that touches `web/`. One-time setup:

1. Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Add the `VITE_EIA_API_KEY` secret (optional; without it the live panel is disabled).
3. Push to `main`. The site publishes at `https://<user>.github.io/<repo>/`.

Vite `base` is `./` (relative), so the build works both at a domain root and under the Pages
project subpath without changes.

## Project layout

```
web/
  scripts/export_data.py     # CSV -> public/data/*.json (+ validation targets)
  public/data/               # committed exported data
  src/lib/                   # quantile, metrics (port of src/metrics.py), netload, battery, eia
  src/components/            # Hero, ExplainerGrid, ScenarioExplorer, LiveGridPanel, Findings, About
  src/components/charts/     # LineChart, Donut, MetricTile
```
