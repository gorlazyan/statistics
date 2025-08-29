# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 15:34:51 2025

@author: gor.lazyan
"""

# Re-read data with appropriate column type conversion and sanitization
df = pd.read_excel(excel_path, sheet_name='value, month')
df.columns = df.iloc[0]
df = df[1:]
df = df.rename(columns={'Activity value': 'Date'})
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Rename and convert columns properly
df_reserves = df[['Date',
                  'Monetary base, AMD',
                  'Currency outside of the CBA, AMD',
                  'Correspondent accounts (in dram), AMD',
                  'Correspondent accounts (in FX), AMD',
                  ' Other accounts (in dram), AMD',
                  'Other accounts (in FX), AMD']].copy()

df_reserves.columns = ['Date', 'Monetary Base', 'Currency Outside CBA',
                       'Corr AMD', 'Corr FX', 'Other AMD', 'Other FX']

# Convert all values to numeric
for col in df_reserves.columns[1:]:
    df_reserves[col] = pd.to_numeric(df_reserves[col], errors='coerce')

# Calculate reserve components
df_reserves['Reserves AMD'] = df_reserves['Corr AMD'] + df_reserves['Other AMD']
df_reserves['Reserves FX'] = df_reserves['Corr FX'] + df_reserves['Other FX']
df_reserves['Currency Outside CBA'] = df_reserves['Currency Outside CBA']

# Filter for plotting
df_reserves_filtered = df_reserves[['Date', 'Currency Outside CBA', 'Reserves AMD', 'Reserves FX']].dropna()

# Plot updated stacked area chart
plt.figure(figsize=(14, 7))
plt.stackplot(df_reserves_filtered['Date'],
              df_reserves_filtered['Currency Outside CBA'] / 1e3,
              df_reserves_filtered['Reserves AMD'] / 1e3,
              df_reserves_filtered['Reserves FX'] / 1e3,
              labels=['Currency Outside CBA', 'Reserves in AMD', 'Reserves in FX'])

plt.title('Currency and Reserve Composition of Armenia’s Monetary Base (1995–2025)', fontsize=14)
plt.xlabel('Date')
plt.ylabel('Billion AMD')
plt.legend(loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Save chart
reserve_by_currency_chart = "/mnt/data/monetary_base_reserve_by_currency.png"
plt.savefig(reserve_by_currency_chart)
plt.show()

reserve_by_currency_chart

























# Define start and end date for x-axis
start_date = pd.Timestamp('1995-01-01')
end_date = pd.Timestamp('2025-06-30')

# Filter the data within that range
df_reserves_filtered_final = df_reserves_filtered[
    (df_reserves_filtered['Date'] >= start_date) & 
    (df_reserves_filtered['Date'] <= end_date)
]

# Plot with defined x-axis limits
plt.figure(figsize=(14, 7))
plt.stackplot(df_reserves_filtered_final['Date'],
              df_reserves_filtered_final['Currency Outside CBA'] / 1e3,
              df_reserves_filtered_final['Reserves AMD'] / 1e3,
              df_reserves_filtered_final['Reserves FX'] / 1e3,
              labels=['Currency Outside CBA', 'Reserves in AMD', 'Reserves in FX'])

# Add vertical event lines
plt.axvline(pd.Timestamp('2006-01-01'), color='black', linestyle='--', label='Shift to Inflation Targeting (2006)')
plt.axvline(pd.Timestamp('2008-09-01'), color='red', linestyle='--', label='Global Financial Crisis (2008)')
plt.axvline(pd.Timestamp('2014-12-01'), color='purple', linestyle='--', label='Ruble Crisis Spillover (2014)')
plt.axvline(pd.Timestamp('2020-03-01'), color='green', linestyle='--', label='COVID-19 & 44-Day War (2020)')
plt.axvline(pd.Timestamp('2022-02-01'), color='orange', linestyle='--', label='Russian-Ukrainian Conflict (2022)')

# Format chart
plt.title('Currency and Reserve Composition of Armenia’s Monetary Base (Jan 1995 – Jun 2025)', fontsize=14)
plt.xlabel('Date')
plt.ylabel('Billion AMD')
plt.legend(loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.gca().set_xlim([start_date, end_date])
plt.gca().xaxis.set_major_locator(mdates.YearLocator(1))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.xticks(rotation=45)

# Save final chart
final_fixed_range_chart = "/mnt/data/monetary_base_reserve_final_range.png"
plt.savefig(final_fixed_range_chart)
plt.show()

final_fixed_range_chart
