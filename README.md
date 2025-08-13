# Toronto 311 Geospatial & Trend Analysis (2021–2025 YTD)

This project analyzes **customer-initiated 311 service requests** in Toronto to surface
the most frequent complaint types over time and across space, and to provide
portfolio-ready visuals and (optionally) forecasts.

**Data source:** City of Toronto Open Data — *311 Service Requests – Customer Initiated*  
https://open.toronto.ca/dataset/311-service-requests-customer-initiated/

## Deliverables (MVP)
- `export/311_daily_totals_2021_2025.csv` – daily counts (Canceled excluded)
- `export/311_top_types_by_year_2021_2025.csv` – Top 15 types per year
- `export/311_counts_year_type_division_ward_2021_2025.csv` – tidy table for BI
- `figures/` – static PNGs (top types per year, cumulative YTD vs LY, YoY heatmap)
- `export/map_ward_rates.html` – ward-level choropleth (per 10k residents)

## How to run
1. Create a virtual env and install deps:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run extraction & exports:
   ```bash
   python scripts/01_extract_transform.py
   ```
3. Run EDA & plots:
   ```bash
   python scripts/02_eda_trends.py
   ```
4. (Optional) Forecasts later:
   ```bash
   python scripts/03_forecast_template.py
   ```

## Configuration
Edit the small config block at the top of each script:
- Years: `WANT_YEARS = {2021, 2022, 2023, 2024, 2025}`
- Top-N categories per year: `TOP_N = 15`
- Choropleth: set paths to **Ward Boundaries GeoJSON** and **Ward Population CSV**

### Ward shapes & population (manual downloads)
- **Ward Boundaries (GeoJSON)**: https://open.toronto.ca/
- **Ward Population**: City ward profiles (latest available; include ward number/name & population)

> We normalize map views to **requests per 10k residents** to reduce bias from population size.

## Notes & Limitations (from dataset documentation)
- Covers **5 of 45 divisions**: Municipal Licensing & Standards, Solid Waste Management, Toronto Water, Transportation Services, Urban Forestry.
- Represents **~30–35% of all 311 contacts**; not full City services.
- Locations are only those **validated** by the City’s geospatial system.
- **Original Service Request Type** is the customer-phrased type at creation (may differ from back-end after inspection). We use this to reflect **demand**.
- Status may change over time; default views **exclude `Canceled`**.
- Urban form, infrastructure age, and backend-only codes mean **geographic bias** can occur.

## Repository Structure
```
toronto-311-geo/
  ├─ src/
  │   ├─ ckan_311.py              # CKAN helpers for discovery & fetch
  │   └─ map_utils.py             # choropleth + hotspot helpers (ward joins)
  ├─ scripts/
  │   ├─ 01_extract_transform.py  # pulls via API, cleans, exports CSVs
  │   ├─ 02_eda_trends.py         # loads exports, plots figures
  │   └─ 03_forecast_template.py  # starter for Prophet/SARIMA
  ├─ export/                      # CSV outputs, HTML maps
  ├─ figures/                     # PNG charts
  ├─ data/                        # (optional) local cache (gitignored)
  ├─ requirements.txt
  └─ README.md
```
