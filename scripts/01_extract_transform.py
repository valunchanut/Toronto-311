"""Extract 311 SR data (2021–2025 YTD), clean, and export tidy CSVs."""
from pathlib import Path
import pandas as pd
from src.ckan_311 import discover_year_resources, pull_year_counts, pull_daily

# --- Config ---
WANT_YEARS = {2021, 2022, 2023, 2024, 2025}
TOP_N = 15
EXCLUDE_CANCELED = True

EXPORT = Path('export')
EXPORT.mkdir(parents=True, exist_ok=True)

print('Discovering resources...')
year_to_res = discover_year_resources(WANT_YEARS)
print('Years found:', list(year_to_res.keys()))

# Year/type/division/ward counts
frames = []
daily_frames = []
for y, res in year_to_res.items():
    print(f'Pulling aggregated counts for {y} ...')
    frames.append(pull_year_counts(res, exclude_canceled=EXCLUDE_CANCELED))
    print(f'Pulling daily totals for {y} ...')
    daily_frames.append(pull_daily(res, exclude_canceled=EXCLUDE_CANCELED))

df_counts = (pd.concat(frames, ignore_index=True)
               .astype({'year': int, 'n': int})
               .sort_values(['year','n'], ascending=[True, False]))

# Top by year
top_by_year = (df_counts.groupby(['year','type'], as_index=False)['n'].sum()
                        .sort_values(['year','n'], ascending=[True, False])
                        .groupby('year').head(TOP_N))

# Daily totals across years
daily = (pd.concat(daily_frames, ignore_index=True)
           .dropna(subset=['day'])
           .groupby('day', as_index=False)['n'].sum()
           .sort_values('day'))

# Exports
df_counts.to_csv(EXPORT/'311_counts_year_type_division_ward_2021_2025.csv', index=False)
top_by_year.to_csv(EXPORT/'311_top_types_by_year_2021_2025.csv', index=False)
daily.to_csv(EXPORT/'311_daily_totals_2021_2025.csv', index=False)

print('Done. Files written to export/.')
