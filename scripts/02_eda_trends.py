"""EDA & plots: top types, cumulative YTD vs last year, YoY heatmap."""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date

EXPORT = Path('export')
FIG = Path('figures')
FIG.mkdir(parents=True, exist_ok=True)

counts = pd.read_csv(EXPORT/'311_counts_year_type_division_ward_2021_2025.csv')
top_by_year = pd.read_csv(EXPORT/'311_top_types_by_year_2021_2025.csv')
daily = pd.read_csv(EXPORT/'311_daily_totals_2021_2025.csv', parse_dates=['day'])

# --- Top 10 overall across all years ---
overall_top = (counts.groupby('type', as_index=False)['n'].sum()
                      .sort_values('n', ascending=False).head(10))

plt.figure(figsize=(8,5))
plt.barh(overall_top['type'], overall_top['n'])
plt.gca().invert_yaxis()
plt.title('Top 10 311 Service Request Types (2021–2025 YTD)')
plt.xlabel('Count')
plt.tight_layout()
plt.savefig(FIG/'top10_overall.png', dpi=150)

# --- Top 15 by year (2023–2025 focus) ---
focus_years = [2023, 2024, 2025]
for y in focus_years:
    sub = (top_by_year[top_by_year['year']==y]
           .sort_values('n', ascending=True))
    plt.figure(figsize=(8,5))
    plt.barh(sub['type'], sub['n'])
    plt.title(f'Top 15 Types — {y}')
    plt.xlabel('Count')
    plt.tight_layout()
    plt.savefig(FIG/f'top15_{y}.png', dpi=150)

# --- Cumulative YTD vs last year ---
today = daily['day'].max().date()  # assume latest day in data ~ run day
this_year = today.year
# Align both years to same day-of-year window
def cum_ytd(series):
    s = series.set_index('day').sort_index()
    # trim to YTD for its year
    end = date(s.index.max().year, today.month, today.day)
    s = s.loc[str(s.index.max().year):str(s.index.max().year)].loc[:pd.Timestamp(end)]
    s['cum'] = s['n'].cumsum()
    return s
ytd_this = cum_ytd(daily[daily['day'].dt.year == this_year].copy())
ytd_last = cum_ytd(daily[daily['day'].dt.year == this_year-1].copy())

plt.figure(figsize=(8,5))
plt.plot(ytd_this.index.dayofyear, ytd_this['cum'], label=str(this_year))
if not ytd_last.empty:
    plt.plot(ytd_last.index.dayofyear, ytd_last['cum'], label=str(this_year-1))
plt.title('Cumulative YTD Requests vs Last Year')
plt.xlabel('Day of Year')
plt.ylabel('Cumulative Requests')
plt.legend()
plt.tight_layout()
plt.savefig(FIG/'cumulative_ytd_vs_ly.png', dpi=150)

# --- YoY % change heatmap for top 20 categories overall ---
cats = (counts.groupby('type', as_index=False)['n'].sum()
               .sort_values('n', ascending=False).head(20)['type'].tolist())
pivot = (counts[counts['type'].isin(cats)]
         .groupby(['year','type'], as_index=False)['n'].sum()
         .pivot(index='type', columns='year', values='n').fillna(0).sort_index())

# Compute YoY % change (relative to previous year)
ycols = sorted([c for c in pivot.columns if isinstance(c, (int, np.integer))])
yoy = pivot[ycols].pct_change(axis=1) * 100

plt.figure(figsize=(10,6))
# simple heatmap using imshow
plt.imshow(yoy.values, aspect='auto', interpolation='nearest')
plt.colorbar(label='% change YoY')
plt.yticks(range(len(yoy.index)), yoy.index)
plt.xticks(range(len(ycols)), ycols)
plt.title('YoY % Change — Top 20 Categories (Counts by Year)')
plt.tight_layout()
plt.savefig(FIG/'yoy_heatmap_top20.png', dpi=150)

print('EDA figures saved to figures/.')
