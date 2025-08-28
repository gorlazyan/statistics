# -*- coding: utf-8 -*-
"""
Created on Thu Aug 28 14:54:11 2025

@author: Gor_Lazyan
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# --- Load data
file_path = "C:/Users/Gor_Lazyan/Downloads/Deposits by sectors.xlsx"
df = pd.read_excel(file_path, sheet_name=0)

# Prepare structure
data = df.iloc[2:].copy()
data.columns = ["Sector","Type","Currency","Residency"] + list(df.columns[4:])
for c in ["Sector","Type","Currency","Residency"]:
    data[c] = data[c].astype(str).str.strip()

# Latest column
latest_col = data.columns[-1]

# Filter residents only
data["Value"] = pd.to_numeric(data[latest_col], errors="coerce").fillna(0.0)
res_data = data[~data["Residency"].str.lower().str.contains("non")].copy()

# Drop any totals rows
for col in ["Sector","Type","Currency"]:
    res_data = res_data[~res_data[col].str.contains("Total", case=False, na=False)]

# Aggregate flows (residents only)
flows = res_data.groupby(["Residency","Currency","Type","Sector"], as_index=False)["Value"].sum()

# Grand total (residents only)
grand_total = flows["Value"].sum()

# Totals per level
res_totals   = flows.groupby("Residency")["Value"].sum().sort_values(ascending=False)
cur_totals   = flows.groupby("Currency")["Value"].sum().sort_values(ascending=False)
type_totals  = flows.groupby("Type")["Value"].sum().sort_values(ascending=False)
sector_totals= flows.groupby("Sector")["Value"].sum().sort_values(ascending=False)

# Palette
residency_colors = {"Resident":"#16A34A"}  # bright green
currency_colors  = {"AMD":"#2563EB", "FX":"#9333EA"}  # AMD blue, FX purple
type_colors      = {"Demand deposits":"#06B6D4","Time deposits":"#EF4444"}  # cyan, red
sector_colors    = {
    "Households":"#F97316",  # orange per request
    "Non-Financial Corporations":"#3B82F6",
    "Financial Corporations":"#A855F7",
    "Government":"#DC2626",
    "Non-Profit Organizations":"#EC4899",
    "Other":"#22C55E",
}

def fmt_bln(v):  # v in mln AMD
    return f"{v/1000:,.1f} bln AMD"

# Build node lists and positions (x/y). We'll stack by value with small gaps.
gap = 0.012

def make_positions(items_series):
    # items_series is a pd.Series indexed by item name with values=sum
    items = list(items_series.index)
    totals = list(items_series.values)
    total_sum = sum(totals)
    heights = [ (v/total_sum) * (1 - gap*(len(items)+1)) if total_sum>0 else 0 for v in totals ]
    y_positions = []
    y = gap
    for h in heights:
        y_positions.append(y)
        y += h + gap
    return items, totals, heights, y_positions

# Residency (only one likely, but generalize)
res_items, res_vals, res_h, res_y = make_positions(res_totals)
cur_items, cur_vals, cur_h, cur_y = make_positions(cur_totals)
typ_items, typ_vals, typ_h, typ_y = make_positions(type_totals)
sec_items, sec_vals, sec_h, sec_y = make_positions(sector_totals)  # sorted by size already

# Node labels and colors
labels = []
colors = []
x = []
y = []

# Helper to add node
def add_node(name, color, xpos, ypos):
    labels.append(name)  # will override sector labels later
    colors.append(color)
    x.append(xpos)
    y.append(ypos)

# Add nodes by columns with fixed x
x_res, x_cur, x_typ, x_sec = 0.00, 0.33, 0.66, 0.99

# Residency nodes
for n, yy in zip(res_items, res_y):
    add_node(n, residency_colors.get(n, "#16A34A"), x_res, yy)

# Currency nodes
for n, yy in zip(cur_items, cur_y):
    add_node(n, currency_colors.get(n, "#9CA3AF"), x_cur, yy)

# Type nodes
for n, yy in zip(typ_items, typ_y):
    add_node(n, type_colors.get(n, "#cbd5e1"), x_typ, yy)

# Sector nodes (labels will be blank and added as annotations)
for n, yy in zip(sec_items, sec_y):
    add_node(" ", sector_colors.get(n, "#9CA3AF"), x_sec, yy)  # placeholder label

# Build index mapping
node_index = {name: idx for idx, name in enumerate(labels)}

# Because sector labels are " ", we need separate mapping for sectors by order
sector_node_indices = {sec_items[i]: (len(labels)-len(sec_items)+i) for i in range(len(sec_items))}

# Link arrays
sources = []
targets = []
values  = []
link_colors = []
link_hovers = []

# Residency -> Currency
rc = flows.groupby(["Residency","Currency"])["Value"].sum().reset_index()
for _, row in rc.iterrows():
    s = node_index[row["Residency"]]
    t = node_index[row["Currency"]]
    v = float(row["Value"])
    sources.append(s); targets.append(t); values.append(v)
    link_colors.append(currency_colors.get(row["Currency"], "#9CA3AF"))
    pct = v/grand_total*100 if grand_total>0 else 0
    link_hovers.append(f"{row['Residency']} → {row['Currency']}<br>{v:,.0f} mln AMD ({pct:.1f}%)")

# Currency -> Type
ct = flows.groupby(["Currency","Type"])["Value"].sum().reset_index()
for _, row in ct.iterrows():
    s = node_index[row["Currency"]]
    t = node_index[row["Type"]]
    v = float(row["Value"])
    sources.append(s); targets.append(t); values.append(v)
    link_colors.append(type_colors.get(row["Type"], "#cbd5e1"))
    pct = v/grand_total*100 if grand_total>0 else 0
    link_hovers.append(f"{row['Currency']} → {row['Type']}<br>{v:,.0f} mln AMD ({pct:.1f}%)")

# Type -> Sector
ts = flows.groupby(["Type","Sector"])["Value"].sum().reset_index()
for _, row in ts.iterrows():
    s = node_index[row["Type"]]
    t = sector_node_indices[row["Sector"]]
    v = float(row["Value"])
    sources.append(s); targets.append(t); values.append(v)
    link_colors.append(sector_colors.get(row["Sector"], "#9CA3AF"))
    pct = v/grand_total*100 if grand_total>0 else 0
    link_hovers.append(f"{row['Type']} → {row['Sector']}<br>{v:,.0f} mln AMD ({pct:.1f}%)")

# Build node display labels (Residency/Currency/Type with totals and shares)
display_labels = []
# Residency
for n, val in zip(res_items, res_vals):
    display_labels.append(f"{n}<br>{fmt_bln(val)} ({(val/grand_total*100 if grand_total>0 else 0):.1f}%)")
# Currency
for n, val in zip(cur_items, cur_vals):
    display_labels.append(f"{n}<br>{fmt_bln(val)} ({(val/grand_total*100 if grand_total>0 else 0):.1f}%)")
# Type
for n, val in zip(typ_items, typ_vals):
    # type totals are over residents only, already
    display_labels.append(f"{n}<br>{fmt_bln(val)} ({(val/grand_total*100 if grand_total>0 else 0):.1f}%)")
# Sector (leave blank inside nodes)
for n, val in zip(sec_items, sec_vals):
    display_labels.append(f"{n}<br>{fmt_bln(val)} ({(val/grand_total*100 if grand_total>0 else 0):.1f}%)")

# Create figure
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=16, thickness=20,
        line=dict(color="rgba(0,0,0,0.25)", width=0.8),
        label=display_labels,
        color=colors,
        x=x, y=y
    ),
    link=dict(
        source=sources, target=targets, value=values,
        color=link_colors,
        hovertemplate="%{customdata}<extra></extra>",
        customdata=link_hovers
    )
)])

# # Add annotations for sector labels just to the right of each sector node
# annotations = []
# for sec, yy, val in zip(sec_items, sec_y, sec_vals):
#     pct = val/grand_total*100 if grand_total>0 else 0
#     text = f"{sec}<br>{fmt_bln(val)} ({pct:.1f}%)"
#     annotations.append(dict(
#         x=1.1, y=yy ,  # approx center + ( (val/sector_totals.sum()) * (1 - gap*(len(sec_items)+1)) )/2
#         xref="paper", yref="paper",
#         text=text, showarrow=False, align="left",
#         font=dict(size=12, color="#111827")
#     ))

fig.update_layout(
    title=dict(text="The structure of residents' deposits in Armenia (as of July 2025)", x=0.5, xanchor="center"),
    font_size=12, margin=dict(l=10,r=10,t=80,b=10),  # extra right margin for labels
    paper_bgcolor="white"# ,    annotations=annotations
)


# open the figure in your default web browser
pio.renderers.default = "browser"

fig.show()  # <-- preview first in a browser window



out_path = "C:/Users/Gor_Lazyan/Downloads/deposit_alluvial.html"
pio.write_html(fig, file=out_path, auto_open=False)
out_path

