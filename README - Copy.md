# Renewable-PowerGrid-Risk
This is an independent research project that investigates the impact of increasing renewable energy on power grid variability and explores AI-driven risk detection methods.
Research: Uncertainty-Aware AI Risk Detection for Power Grids Under High Renewable Penetration
Author: Kyle Lin. St Mark's School of Texas, Class of 2028
Research start date: 03/15/2026

# Data Sources
ERCOT Historical Hourly Load:
https://www.ercot.com/gridinfo/load/load_hist

ERCOT Hourly Aggregated Wind and Solar Output:
https://www.ercot.com/mp/data-products/data-product-details?id=pg7-126-m

Weather Hourly Data:
https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data

Cite as: Kantor, Diana; Casey, Nancy W.; Menne, Matthew J.; Buddenberg, Andrew. 2023. Local Climatological Data (LCD), Version 2. ['KDFW','KIAH','KSAT']. NOAA National Centers for Environmental Information. https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc:C01689.
Access Date: 04/11/2026

Web service: https://www.ncei.noaa.gov/cdo-web/webservices/v2

Weather stations selection logic:
KDFW → North load
KIAH → Coast humidity
KSAT → South heat
KAMA → Panhandle wind
KLBB → West wind
KABI -> Farwest wind

ERCOT Load Forecast for next 5 years:
https://www.ercot.com/gridinfo/load/forecast


# Load Growth
Significant YOY growth was oberseved in ERCOT load driven by population growth, increased oil and gas activity, cryptocurrency mining, and expanding data center demand in Texas. The long-run growth trend is removed, and the trend component is re-centered to the terminal level as of 12/31/2025. Intraday variation is preserved.
![Load Plot](figures/load_detrending_diagnostic.png)


This project develops an uncertainty-aware machine learning framework to detect power grid risk under high renewable penetration using ERCOT data.

---

## 🎯 Objective

To study how increasing wind and solar penetration affects grid stability and how battery storage can reduce operational risk.

---

## 📊 Key Features

- ERCOT load, wind, and solar analysis  
- NOAA weather integration  
- Ramp rate and volatility modeling  
- Machine learning-based risk detection  
- Monte Carlo weather uncertainty simulation  
- Battery storage impact modeling  

---


## 🧠 Method Overview

1. Construct net load = load − wind − solar  
2. Compute ramp rate and volatility  
3. Define risk events using extreme thresholds  
4. Train ML model (XGBoost)  
5. Simulate weather uncertainty (Monte Carlo)  
6. Model battery storage as ramp smoothing  

## Renewable Grid Risk Framework
Quantifying and Predicting Net Load Risk Under High Renewable Penetration Using AI-Guided Energy Storage

A unified computational research framework for analyzing renewable-driven grid instability, weather-driven uncertainty, and predictive mitigation using artificial intelligence and battery energy storage systems.

## Project Overview

The rapid growth of renewable energy resources such as solar and wind is fundamentally transforming modern electric power systems. Although renewable generation reduces carbon emissions, its dependence on weather conditions introduces variability and uncertainty into grid operations.

## This research project develops a multi-stage computational framework to:

quantify renewable-induced net load risk
model weather-driven uncertainty
predict high-risk ramp events
mitigate instability using AI-guided battery dispatch

The project investigates how increasing renewable penetration changes net load behavior and explores how predictive intelligence and energy storage can improve grid reliability under uncertain operating conditions.

## Research Architecture

The project is organized as a progressive three-stage research framework.

Stage 1:
Quantify renewable-induced net load risk
        ↓
Stage 2:
Model weather-driven uncertainty
        ↓
Stage 3:
Predict and mitigate instability using
AI-guided energy storage
Research Papers

## Paper 1 — Renewable Risk Quantification (Current focus 05/12/2026)
Title

Quantifying Net Load Variability Under Increasing Renewable Penetration

Objective

Quantify how increasing solar and wind penetration alters net load behavior and increases ramping risk.

Key Contributions
Net load reconstruction using ERCOT data
Renewable penetration scenario analysis
Ramp distribution analysis
Extreme event quantification
Tail-risk metrics
Nonlinear renewable risk characterization
Core Finding

Extreme net load ramp events increase nonlinearly as renewable penetration increases.

## Paper 2 — Weather Uncertainty Modeling  (Planning phase...)
Title

Modeling Weather-Driven Renewable Variability and Grid Uncertainty Under High Renewable Penetration

Objective

Evaluate how interannual weather variability amplifies renewable-induced grid uncertainty.

## Repository Structure

grid-risk-ai/
│
├── data/
├── src/
├── notebooks/
├── figures/
├── results/
├── main.py
└── README.md




