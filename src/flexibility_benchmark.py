"""
Dispatchable Fleet Flexibility Benchmark Calculation
=====================================================
Estimates the aggregate hourly ramp capability (MW/hr) of ERCOT's
dispatchable fleet, used as the operational feasibility threshold
in the ramping risk analysis.

The benchmark accounts for real-world constraints:
- Not all units are online at any given hour
- Online units have limited headroom (already partially loaded)
- Start-up times limit offline unit contributions within 1 hour

Sources:
- Gas turbine ramp rates: Lew et al., NREL/TP-5500-55588 (2013)
- ERCOT fleet capacity: ERCOT CDR Report 2025-2034 (Dec 2024)
- Battery storage: EIA Battery Storage Market Trends (July 2024)
"""

# =============================================================
# ERCOT Fleet Installed Capacity (MW) — from ERCOT CDR 2025
# =============================================================
nameplate_cc = 25000       # Combined-cycle gas turbines
nameplate_peakers = 15000  # Simple-cycle gas turbines (peakers)
nameplate_battery = 5000   # Grid-scale battery storage
nameplate_other = 2000     # Hydro + demand response

# =============================================================
# Effective Fleet Ramp Capability
# =============================================================
# These are NOT raw engineering ramp rates of individual units.
# They represent the EFFECTIVE hourly ramp contribution from each
# resource class, accounting for:
#   - Fraction of fleet online during sunset hours
#   - Available headroom (units already partially loaded)
#   - Start-up time constraints for offline units
#   - Maintenance and forced outage rates

# Combined-cycle gas turbines
# Engineering rate: 2-5%/min per unit (Lew et al. 2013)
# Effective fleet contribution: limited by ~50% online fraction
# and ~50% average headroom on online units
cc_online_fraction = 0.50       # ~50% of CC fleet online at sunset
cc_headroom_fraction = 0.50     # average upward headroom on online units
ramp_cc = nameplate_cc * cc_online_fraction * cc_headroom_fraction
# = 25,000 × 0.50 × 0.50 = 6,250 MW/hr

# Gas peakers (simple-cycle turbines)
# Engineering rate: 8-12%/min per unit (Lew et al. 2013)
# Fast-start capability: can reach full output from cold in ~10-20 min
# Effective fleet contribution: ~67% of fleet dispatchable within 1 hour
# (accounts for maintenance, location constraints, gas supply)
peaker_dispatch_fraction = 2/3    # ~2/3 of peaker fleet available
ramp_peakers = nameplate_peakers * peaker_dispatch_fraction
# = 15,000 × 0.667 = 10,000 MW/hr

# Battery storage
# Near-instantaneous ramp (inverter-limited, full output in seconds)
# Full nameplate capacity available as 1-hour ramp contribution
ramp_battery = nameplate_battery
# = 5,000 MW/hr

# Other flexible resources (hydro + demand response)
# Conservative estimate of fast-acting flexible capacity
ramp_other = nameplate_other
# = 2,000 MW/hr

# =============================================================
# AGGREGATE FLEXIBILITY BENCHMARK
# =============================================================
FLEXIBILITY_BENCHMARK = ramp_cc + ramp_peakers + ramp_battery + ramp_other

# =============================================================
# Output
# =============================================================
print("=" * 60)
print("ERCOT Dispatchable Fleet Flexibility Benchmark")
print("=" * 60)
print(f"\nComponent breakdown (effective hourly ramp capability):")
print(f"  Combined-cycle:  {nameplate_cc/1000:.0f} GW × "
      f"{cc_online_fraction*100:.0f}% online × "
      f"{cc_headroom_fraction*100:.0f}% headroom = "
      f"{ramp_cc:,.0f} MW/hr")
print(f"  Gas peakers:     {nameplate_peakers/1000:.0f} GW × "
      f"{peaker_dispatch_fraction*100:.0f}% dispatchable       = "
      f"{ramp_peakers:,.0f} MW/hr")
print(f"  Battery storage: {nameplate_battery/1000:.0f} GW "
      f"(full dispatch, instantaneous)    = "
      f"{ramp_battery:,.0f} MW/hr")
print(f"  Other (hydro+DR): {nameplate_other/1000:.0f} GW "
      f"(conservative estimate)     = "
      f"{ramp_other:,.0f} MW/hr")
print(f"\n  {'─' * 50}")
print(f"  TOTAL FLEXIBILITY BENCHMARK:  {FLEXIBILITY_BENCHMARK:,.0f} MW/hr")
print(f"\n{'=' * 60}")
print(f"Key assumptions and limitations:")
print(f"  - CC online fraction ({cc_online_fraction*100:.0f}%) reflects typical")
print(f"    sunset-hour commitment; actual varies by day/season")
print(f"  - Peaker availability ({peaker_dispatch_fraction*100:.0f}%) accounts for")
print(f"    maintenance, gas supply, and location constraints")
print(f"  - Battery assumed fully charged at sunset (optimistic)")
print(f"  - Does NOT account for: transmission constraints,")
print(f"    simultaneous contingencies, or reserve requirements")
print(f"  - Treat as ASSUMED BENCHMARK, not measured system limit")
print(f"{'=' * 60}")
