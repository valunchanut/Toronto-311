"""Starter: forecasting daily totals (baseline + placeholder for SARIMA/Prophet)."""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

EXPORT = Path('export')
FIG = Path('figures')
FIG.mkdir(parents=True, exist_ok=True)

daily = pd.read_csv(EXPORT/'311_daily_totals_2021_2025.csv', parse_dates=['day'])
daily = daily.sort_values('day')

# Baseline: average of last 28 days extrapolated forward N days
N_FWD = 90
last_28 = daily.tail(28)['n'].mean()
last_date = daily['day'].max()
future_days = [last_date + timedelta(days=i) for i in range(1, N_FWD+1)]
baseline = pd.DataFrame({'day': future_days, 'n_pred': last_28})

plt.figure(figsize=(9,5))
plt.plot(daily['day'], daily['n'], label='History', alpha=0.7)
plt.plot(baseline['day'], baseline['n_pred'], label='Baseline (28-day mean)', linestyle='--')
plt.title('Daily Requests with Baseline Forecast (next 90 days)')
plt.xlabel('Date'); plt.ylabel('Requests')
plt.legend()
plt.tight_layout()
plt.savefig(FIG/'forecast_baseline_90d.png', dpi=150)

print('Baseline forecast figure saved to figures/.')

# TODO:
# - Option A: SARIMA (statsmodels) with seasonal order (7,365)
# - Option B: Prophet (requires install) with yearly & weekly seasonality
# - Backtest: rolling-origin evaluation vs baseline (MAE, sMAPE)
