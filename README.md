# Renewable-PowerGrid-Risk
This is an independent research project that investigates the impact of increasing renewable energy on power grid variability and explores AI-driven risk detection methods.
Title: Uncertainty-Aware AI Risk Detection for Power Grids Under High Renewable Penetration

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

---

## 🔋 Battery Storage Model

Battery storage is modeled as a smoothing factor:

# Uncertainty-Aware Grid Risk Detection under High Renewable Penetration

## Overview
This project develops an uncertainty-aware machine learning framework to detect power grid risk under increasing renewable energy penetration. The approach integrates historical load, wind, solar, and weather data to model variability and identify extreme grid stress events.

## Key Contributions
- Net load variability modeling using ERCOT data
- Weather-driven uncertainty using 26-year ensemble (2000–2025)
- AI-based grid risk detection
- Battery storage mitigation modeling
- Extreme event backtesting (Winter Storm Uri-style scenario)
- Predictive uncertainty as early warning signal

## Methodology
1. Construct net load = load − wind − solar
2. Extract ramp rate and volatility features
3. Train machine learning risk detection model
4. Apply Monte Carlo perturbations for uncertainty
5. Model battery storage as ramp smoothing
6. Evaluate extreme weather stress scenarios

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


## Example Results
- Battery storage reduces extreme ramp events
- Weather variability increases risk uncertainty
- Uncertainty rises before stress events

## Requirements
- Python 3.10+
- pandas
- numpy
- scikit-learn
- matplotlib

## How to Run

python main.py


## Author
Independent research project investigating AI-driven risk detection for renewable-heavy power gr