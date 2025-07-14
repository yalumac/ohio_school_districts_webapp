#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 13 16:43:27 2025

@author: yaluma.1
"""

## Yaluma Segregation Data  

import json
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import geopandas as gpd
import os


# replace with your desired path
# os.chdir(r"/Users/yaluma.1/Library/CloudStorage/OneDrive-TheOhioStateUniversity/Py Projects/Diss App")

# confirm its working
# print("Working directory is now:", os.getcwd())


# df = pd.read_stata("/Users/yaluma.1/Library/CloudStorage/OneDrive-TheOhioStateUniversity/Research Projects/Yaluma do-files/yaluma_segregation_shiny_data.dta")
df = pd.read_csv("app_data.csv")

# Searching for variables starting with ecot
#ecot_cols = [c for c in df.columns if c.startswith('ecot')]
#ecot_df   = df[ecot_cols]


# Drop unneccesary columns
# df.iloc[row_indexer, col_indexer]
# df = df.iloc[:, :100]
df = df.loc[:, list(df.columns[:100]) + ["fracpaychartdig", "fracpaychartbm", "chartershare", "ecotpct"]]

# For testing the interactive maps
# df_app = df.iloc[:100, :20]

# 1) Read the shapefile
gdf = gpd.read_file("cb_2018_39_unsd_500k.shp")
print(gdf.head())

# Convert gdf["leaid"] to string (strip whitespace, drop rows where leaid is null/NaN)
#     This ensures you won’t have a mix of float and string in the GeoDataFrame.
gdf["leaid"] = gdf["GEOID"].astype(str).str.strip()
gdf = gdf[gdf["leaid"].notna()]  # drop any rows where leaid was NaN originally
gdf = gdf.drop_duplicates(subset="leaid", keep="first").reset_index(drop=True)

print(f"> GeoDataFrame: {len(gdf)} unique leaid after dropping duplicates.")
print(f"  Sample IDs from gdf: {gdf['leaid'].unique()[:5]}")
print(gdf.head())
# 2) Make sure the district ID column matches your CSV's `leaid` (as string)
#    e.g. if your shapefile has a column called "leaid":
    
gdf["leaid"] = gdf["leaid"].astype(str)


# 4) Write/Save to GeoJSON & CSV
# gdf.to_file("ohio_districts_2018.geojson", driver="GeoJSON")
# gdf.to_csv("gdf_data.csv", index=False)
# -------------------------
# APP code starts here
# -------------------------
# Combine fracpaychartdig with chartershare
# Method 1: using .loc
mask = df['year'] > 2012
df.loc[mask, 'fracpaychartbm'] = df.loc[mask, 'chartershare']

# Change percents into 0-1 scale
# Drop missing values
df = df.dropna(subset = ["pctblk", "pcthis", "pctwht", "leaid"])

# Save
# Assuming df already has columns "leaid" and "leaid"
cols = df.columns.tolist()
# Build new order: put "leaid" first, then "leaid", then all other columns in their original order
new_order = ["leaid"] + [c for c in cols if c not in ("leaid")]
df = df[new_order]

# Ensure leaid is a string so it matches the GeoJSON feature IDs
# df["year"] = df["year"].astype(int)
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

# 3) Convert any demographic columns you plan to color by into floats
#   DEMOGRAPHICS
df["pctblk"] = pd.to_numeric(df["pctblk"], errors="coerce")
df["pcthis"] = pd.to_numeric(df["pcthis"], errors="coerce")
df["pctwht"] = pd.to_numeric(df["pctwht"], errors="coerce")

#   SEGREGATION
df["pctmin_raceineq"] = pd.to_numeric(df["pctmin_raceineq"], errors="coerce")
df["iso_pctmin_raceineq"] = pd.to_numeric(df["iso_pctmin_raceineq"], errors="coerce")
df["dis_pctmin_raceineq"] = pd.to_numeric(df["dis_pctmin_raceineq"], errors="coerce")

#   CHARTER
df["fracpaychartdig"] = pd.to_numeric(df["fracpaychartdig"], errors="coerce")
df["fracpaychartbm"] = pd.to_numeric(df["fracpaychartbm"], errors="coerce")
df["ecotpct"] = pd.to_numeric(df["ecotpct"], errors="coerce")

# Divide each by 100
df["pctblk"] = df["pctblk"] / 100
df["pcthis"] = df["pcthis"] / 100
df["pctwht"] = df["pctwht"] / 100

df["pctblk"].describe()

# Pick a few demographic columns to expose in the dropdown:
#   - Percent Black (pctblk)
#   - Percent Hispanic (pcthis)
#   - Percent White (pctwht)
#   - ... you can add others as needed.
DEMOGRAPHIC_MEASURES = {
    "Percent Black": "pctblk",
    "Percent Hispanic": "pcthis",
    "Percent White": "pctwht"
}

SEGREGATION_MEASURES = {
    "Relative Exposure Index": "pctmin_raceineq",
    "Isolation Index": "iso_pctmin_raceineq",
    "Dissimilarity Index": "dis_pctmin_raceineq"
    # …add others as needed…
}

CHARTER_MEASURES = {
    "Virtual Charter Share": "fracpaychartdig",
    "B&M Charter Share": "fracpaychartbm",
    "ECOT Share": "ecotpct",
}

# --- Constants for Styling & Labels ---
FONT_FAMILY = "Arial, sans-serif"
PRIMARY_COLOR = "#1f77b4"  # Muted blue for primary district line

# Create a dict of nice labels for plots
DEMO_LABELS = {
    "pctblk": "% Black",
    "pcthis": "% Hispanic",
    "pctwht": "% White",
}

SEG_LABELS = {
    "pctmin_raceineq": "Rel. Exposure Index",
    "iso_pctmin_raceineq": "Isolation Index",
    "dis_pctmin_raceineq": "Dissimilarity Index",
}

CHARTER_LABELS = {
    "fracpaychartdig": "Virtual Charter Share",
    "fracpaychartbm": "B&M Charter Share",
    "ecotpct": "ECOT Share",
}


# If you want to merge/join them to see how many rows match exactly:
# drop empty leaids
df = df.dropna(subset = ["leaid"])
# If df["leaid"] is numeric or float:
df["leaid"] = df["leaid"].astype(str).str.strip()


merged = df.merge(gdf, on="leaid", how="left", indicator=True)

matched = merged[merged["_merge"] == "both"].shape[0]
only_in_gdf = merged[merged["_merge"] == "left_only"].shape[0]
only_in_df = merged[merged["_merge"] == "right_only"].shape[0]

print(f"Matched districts: {matched}")
print(f"In gdf only (not in df): {only_in_gdf}")
print(f"In df only (not in gdf): {only_in_df}")

# 2) LOAD GEOJSON for Ohio school districts
# The GeoJSON must have each feature's properties.leaid = district ID (matching df["leaid"])
with open("ohio_districts_2018.geojson", "r") as f:
    ohio_geojson = json.load(f)

# PLOT THE MAP IN HERE
#gdf.plot()
#plt.show() 
#gdf.head()
         
# 3) INITIALIZE DASH APP
app = dash.Dash(__name__)
server = app.server  # for potential deployment

# Determine the range of years present in the data
YEARS = sorted(df["year"].unique())

app.layout = html.Div(style={"fontFamily": FONT_FAMILY, "maxWidth": "1400px", "margin": "0 auto", "padding": "1rem 2rem"}, children=[
    html.H1("Ohio School Districts", style={"text-align": "center"}),
    
    # Subtitle
    html.H2("Demographic and Segregation Changes Over Time", 
            style = {"text-align": "center", "color": "#666", "marginTop": "-10px", "marginBottom": "2rem"}
            ),

    # ─── Measure Type Toggle ─────────────────────────────────────────────────────
    html.Div(
        style={"display": "flex", "align-items": "center", "marginBottom": "1rem"},
        children=[
            html.Label("Select Measure Type:", style={"fontWeight": "bold", "marginRight": "1rem"}),
            dcc.RadioItems(
                id="measure-type",
                options=[
                    {"label": "Demographic", "value": "demo"},
                    {"label": "Segregation",  "value": "seg"},
                    {"label": "Charter Share",  "value": "charter"},
                ],
                value="demo",
                labelStyle={"marginRight": "1rem"},
                inline=True,
            ),
        ],
    ),

    # ─── Demographic & Segregation Dropdowns ─────────────────────────────────────
    html.Div(
        style={"display": "flex", "align-items": "center", "marginBottom": "1rem", "gap": "2rem"},
        children=[
            # Demographic Measure
            html.Div(
                id="demo-container",
                children=[
                    html.Label("Demographic Measure:", style={"font-weight": "bold"}),
                    dcc.Dropdown(
                        id="demo-dropdown",
                        options=[{"label": k, "value": v} for k, v in DEMOGRAPHIC_MEASURES.items()],
                        value="pctblk",
                        clearable=False,
                        style={"width": "250px"},
                    ),
                ],
                style={}, # Let flexbox handle sizing
            ),
            # Segregation Measure
            html.Div(
                id="seg-container",
                children=[
                    html.Label("Segregation Measure:", style={"font-weight": "bold"}),
                    dcc.Dropdown(
                        id="seg-dropdown",
                        options=[{"label": k, "value": v} for k, v in SEGREGATION_MEASURES.items()],
                        value="pctmin_raceineq",
                        clearable=False,
                        style={"width": "250px"},
                    ),
                ],
                style={}, # Let flexbox handle sizing
            ),
            # Charter Share Measure
            html.Div(
                id="charter-container",
                children=[
                    html.Label("Charter Measure:", style={"font-weight": "bold"}),
                    dcc.Dropdown(
                        id="charter-dropdown",
                        options=[{"label": k, "value": v} for k, v in CHARTER_MEASURES.items()],
                        value="fracpaychartbm",
                        clearable=False,
                        style={"width": "250px"},
                    ),
                ],
                style={}, # Let flexbox handle sizing
            ),
        ],
    ),

    # ─── Main content: map + slider on left; time series on right ────────────────
    html.Div(
        style={"display": "flex"},
        children=[
            # ─── Left column: map + slider ──────────────────────────────────────────
            html.Div(
                style={"flex": "0 0 60%", "display": "flex", "flex-direction": "column"},
                children=[
                    # Map (with Loading)
                    dcc.Loading(
                        id="loading-map",
                        type="circle",
                        children=dcc.Graph(
                            id="district-map", 
                            config={"displayModeBar": False},
                            style={"height": "450px"}  # adjust height as needed
                        ),
                    ),

                    # Year Slider (just under map)
                    html.Div(
                        style={"margin": "4rem"},
                        children=[
                            html.Label("Select Year:", style={"fontWeight": "bold", "display": "block", "textAlign": "center", "marginBottom": "0.5rem"}),
                            dcc.Slider(
                                id="year-slider",
                                min=YEARS[0],
                                max=YEARS[-1],
                                step=1,
                                value=YEARS[-1],
                                marks={
                                    str(y): {
                                        "label": str(y),
                                        "style": {
                                            "transform": "rotate(45deg)",
                                            "transformOrigin": "top right",
                                            "whiteSpace": "nowrap",
                                            "display": "inline-block",
                                            "marginTop": "15px"
                                            }
                                        }
                                    for y in YEARS
                                    },
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                        ],
                    ),
                ],
            ),

            # ─── Right column: time series ──────────────────────────────────────────
            html.Div(
                style={"flex": "0 0 40%", "padding-left": "1rem"},
                children=[
                    dcc.Loading(
                        id="loading-ts",
                        type="circle",
                        children=dcc.Graph(
                            id="time-series",
                            config={"displayModeBar": False},
                            style={"height": "550px"}  # ensure ample height
                        ),
                    ),
                ],
            ),
        ],
    ),
    
    # ─── Two overlay checkboxes right below the time series ─────────────
        html.Div(
            style={"marginTop": "10px", "marginBottom": "30px"},
            children=[
                # Note above the demo boxes:
                html.P(
                    "Check boxes to overlay average trends across the state:",
                    style={"fontSize": "12px", "fontStyle": "italic", "marginBottom": "6px"}
                    ),
                html.Div( # This is the parent div for the three checklist groups
                    style={"display": "flex", "gap": "50px"}, # Increased gap for more spacing
                    children=[
                        # Demographic Overlays
                        html.Div(
                            children=[
                                html.Label("Demographic:", style={"fontWeight": "bold", "marginBottom": "5px", "display": "block"}),
                                dcc.Checklist(
                                    id="overlay-checkboxes-demo",
                                    options=[
                                        {"label": "Ohio % Black", "value": "pctblk"},
                                        {"label": "Ohio % Hispanic", "value": "pcthis"},
                                        {"label": "Ohio % White", "value": "pctwht"},
                                    ],
                                    value=[],
                                    labelStyle={
                                        "display": "block",
                                        "marginBottom": "3px",
                                        "fontSize": "12px",
                                    },
                                ),
                            ]
                        ),
                        # Segregation Overlays
                        html.Div(
                            children=[
                                html.Label("Segregation:", style={"fontWeight": "bold", "marginBottom": "5px", "display": "block"}),
                                dcc.Checklist(
                                    id="overlay-checkboxes-seg",
                                    options=[
                                        {"label": "Ohio Rel. Exposure Index", "value": "pctmin_raceineq"},
                                        {"label": "Ohio Isolation Index", "value": "iso_pctmin_raceineq"},
                                        {"label": "Ohio Dissimilarity Index", "value": "dis_pctmin_raceineq"},
                                    ],
                                    value=[],
                                    labelStyle={
                                        "display": "block",
                                        "marginBottom": "3px",
                                        "fontSize": "12px",
                                    },
                                ),
                            ],
                        ),
                        # Charter Share Overlays
                        html.Div(
                            children=[
                                html.Label("Charter Share:", style={"fontWeight": "bold", "marginBottom": "5px", "display": "block"}),
                                dcc.Checklist(
                                    id="overlay-checkboxes-charter",
                                    options=[
                                        {"label": "Ohio B&M Charter Share", "value": "fracpaychartbm"},
                                        {"label": "Ohio Virtual Charter Share", "value": "fracpaychartdig"},
                                        {"label": "Ohio ECOT Share", "value": "ecotpct"},
                                    ],
                                    value=[],
                                    labelStyle={
                                        "display": "block",
                                        "marginBottom": "3px",
                                        "fontSize": "12px",
                                    },
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
    # Data source note fixed to bottom-right
           html.Div(
               children=[
                   "© Chris B. Yaluma, Ph.D.",                # first line (copyright)
                   html.Br(),                     # line break
                   "Data sources: National Center for Education Statistics/ Ohio Department of Education",
                   ],
               style={
                   "fontFamily": FONT_FAMILY,
                   "position": "fixed",
                   "bottom": "10px",
                   "right": "10px",
                   "fontSize": "12px",
                   "color": "#666",
                   "backgroundColor": "rgba(255,255,255,0.8)",
                   "padding": "4px 8px",
                   "borderRadius": "4px",
                   "boxShadow": "0 0 2px rgba(0,0,0,0.2)",
                   "zIndex": 1000,
    },
),

    # ─── Hidden Store for Clicked District ───────────────────────────────────────
    dcc.Store(id="selected-district", data=None),
])

# Radio buttons call back
@app.callback(
    Output("demo-container", "style"),
    Output("seg-container",  "style"),
    Output("charter-container", "style"),
    Input("measure-type",    "value"),
)

def toggle_dropdowns(measure_type):
    if measure_type == "demo":
        return {"display": "block"}, {"display": "none"}, {"display": "none"}
    elif measure_type == "seg":
        return {"display": "none"}, {"display": "block"}, {"display": "none"}
    elif measure_type == "charter":
        return {"display": "none"}, {"display": "none"}, {"display": "block"}
    return {"display": "none"}, {"display": "none"}, {"display": "none"}
    

# 4) CALLBACK: Update Choropleth Map when Year or Demographic changes
@app.callback(
    Output("district-map", "figure"),
    Input("year-slider", "value"),
    Input("demo-dropdown", "value"),
    Input("seg-dropdown", "value"),
    Input("charter-dropdown", "value"),
    Input("measure-type",  "value"),
)

def update_map(selected_year, selected_demo, selected_seg, selected_charter, measure_type):
    
    # Pick the active column and style parameters
    if measure_type == "demo":
        active_col = selected_demo
        label_dict = DEMO_LABELS
        tick_fmt = ".0%"
        color_range = (0, 1)
        color_scale = "Viridis"
    elif measure_type == "seg":
        active_col = selected_seg
        label_dict = SEG_LABELS
        tick_fmt = ".3f"
        color_range = (0, 1)
        color_scale = "Cividis"
    else: # charter
        active_col = selected_charter
        label_dict = CHARTER_LABELS
        tick_fmt = ".1%"
        color_range = (0, 0.25) # Charter share rarely exceeds 25%
        color_scale = "Plasma"

        
    # Filter your DataFrame for that year and drop NA
    dff = df[df["year"] == selected_year].copy() 
    dff = dff.dropna(subset=[active_col])

    # Converting PCTs into 0-100% scale for hover data (use dff, not df)
    dff["pctblk100"] = dff["pctblk"] * 100
    dff["pcthis100"] = dff["pcthis"] * 100
    dff["pctwht100"] = dff["pctwht"] * 100
    dff["fracpaychartdig100"] = dff["fracpaychartdig"] * 100
    dff["fracpaychartbm100"] = dff["fracpaychartbm"] * 100
    dff["ecotpct100"] = dff["ecotpct"] * 100
   
    # Build a *static* Plotly choropleth (no Mapbox)
    fig = px.choropleth(
        dff,
        geojson=ohio_geojson,                 # your cleaned GeoJSON
        locations="leaid",                  # column in dff that matches feature.properties.leaid
        color=active_col,
        featureidkey="properties.leaid",
        hover_data={                          # Define a consistent set of hover data
            "leaid": True,
            "enrolltotal": True,
            "pctblk100": True,
            "pcthis100": True,
            "pctwht100": True,
            "pctmin_raceineq": True,
            "iso_pctmin_raceineq": True,
            "dis_pctmin_raceineq": True,
            "fracpaychartdig100": True,
            "fracpaychartbm100": True,
            "ecotpct100": True,
        },
        color_continuous_scale=color_scale,
        range_color=color_range,
    )
    

    # Zoom/clip to ONLY your district polygons (remove all other map elements)
    fig.update_geos(
        fitbounds="locations",
        visible=False
    )
    
    # Build the hovertemplate string dynamically
    if measure_type == "demo":
        # Show demographics and highlight the active one
        #active_label = label_dict.get(active_col, active_col)
        hover_tmpl = (
            "<b>District ID:</b> %{location}<br>"
            "<b>Total Enrollment:</b> %{customdata[1]:,.0f}<br><br>"
            "<b>Black:</b> %{customdata[2]:.1f}%<br>"
            "<b>Hispanic:</b> %{customdata[3]:.1f}%<br>"
            "<b>White:</b> %{customdata[4]:.1f}%<br>"
            #f"<b>{active_label}:</b> %{{color:.1%}}<extra></extra>"
        )
    elif measure_type == "seg":
        # Show all segregation measures and highlight the active one
        #active_label = label_dict.get(active_col, active_col)
        hover_tmpl = (
            "<b>District ID:</b> %{location}<br>"
            "<b>Total Enrollment:</b> %{customdata[1]:,.0f}<br><br>"
            "<b>Rel. Exposure:</b> %{customdata[5]:.3f}<br>"
            "<b>Isolation:</b> %{customdata[6]:.3f}<br>"
            "<b>Dissimilarity:</b> %{customdata[7]:.3f}<br>"
            #f"<b>{active_label}:</b> %{{color:.3f}}<extra></extra>"
        )
    else: # charter
        # Show both charter measures and highlight the active one
        #active_label = label_dict.get(active_col, active_col)
        hover_tmpl = (
            "<b>District ID:</b> %{location}<br>"
            "<b>Total Enrollment:</b> %{customdata[1]:,.0f}<br><br>"
            "<b>B&M Charter Share:</b> %{customdata[9]:.1f}%<br>"
            "<b>Virtual Charter Share:</b> %{customdata[8]:.1f}%<br>"
            # Note: The index [10] correctly points to ecotpct100 in hover_data
            "<b>ECOT Share:</b> %{customdata[10]:.1f}%<br>" 
            #f"<b>{active_label}:</b> %{{color:.1%}}<extra></extra>"
        )

    # Thicken district outlines so you can see individual shapes
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="white",
        hovertemplate=hover_tmpl,
    )

 # 6) Set the colorbar title to the human‐readable label
    colorbar_title = label_dict.get(active_col, active_col)
    
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title_text=f"{colorbar_title} by School District, {selected_year}",
        title_x=0.5,
        title_font_size=18,
        coloraxis_colorbar=dict(
            title=dict(text=colorbar_title, side="right"),
            ticks="outside",
            tickformat=tick_fmt,
        ),
    )

    return fig


# 5) CALLBACK: Store which district was clicked
@app.callback(
    Output("selected-district", "data"),
    Input("district-map", "clickData"),
    Input("year-slider", "value"),
)
def store_clicked_district(clickData, current_year):
    if clickData is None:
        # If nothing clicked, or user moved the year slider (to clear selection), return None
        return None
    # Extract the district ID from the clickData
    leaid_clicked = clickData["points"][0]["location"]
    return leaid_clicked

# 6) CALLBACK: Update Time Series for the selected district (or show a message if none)
@app.callback(
    Output("time-series", "figure"),
    Input("selected-district",      "data"),
    Input("demo-dropdown",          "value"),
    Input("seg-dropdown",           "value"),
    Input("charter-dropdown",       "value"),
    Input("measure-type",           "value"),
    Input("overlay-checkboxes-demo", "value"),
    Input("overlay-checkboxes-seg", "value"),
    Input("overlay-checkboxes-charter",  "value"),
)
def update_time_series(
    selected_leaid,
    selected_demo,
    selected_seg,
    selected_charter,
    measure_type,
    overlays_demo,
    overlays_seg,
    overlays_charter,
):
    # 1) Placeholder if no district is selected
    if not selected_leaid:
        return {
            "data": [],
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [
                    {
                        "text": "Click on a district to see its trend over time.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 14},
                    }
                ],
                "margin": {"l": 20, "r": 20, "t": 20, "b": 20},
            },
        }

    # 2) Pick the district’s active column and label
    if measure_type == "demo":
        active_col = selected_demo
        y_label = DEMO_LABELS.get(active_col, active_col)
    elif measure_type == "seg":
        active_col = selected_seg
        y_label = SEG_LABELS.get(active_col, active_col)
    else: # charter
        active_col = selected_charter
        y_label = CHARTER_LABELS.get(active_col, active_col)

    # 3) Filter for that district and sort
    df_district = df[df["leaid"] == selected_leaid].sort_values("year").copy()
    
    
    # 3a) Correct 2012 outlier in specific columns by averaging 2011 & 2013
    cols_to_fix = ["pcthis", "pctblk", "iso_pctmin_raceineq"]
    is_2012 = df_district["year"] == 2012
    if is_2012.any():
        # Check if 2011 and 2013 exist for this district to avoid errors
        if 2011 in df_district["year"].values and 2013 in df_district["year"].values:
            for col in cols_to_fix:
                if col in df_district.columns:
                    val_2011 = df_district.loc[df_district["year"] == 2011, col].iloc[0]
                    val_2013 = df_district.loc[df_district["year"] == 2013, col].iloc[0]
                    df_district.loc[is_2012, col] = (val_2011 + val_2013) / 2

    # 4) Base line chart for the district
    fig = px.line(
        df_district,
        x="year",
        y=active_col,
        markers=True,
        labels={"year": "Year", active_col: y_label},
        title=f"<b>{y_label} Over Time</b><br>District {selected_leaid}",
        template="plotly_white",
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    
    # 5) Format y-axis ticks
    if measure_type in ["demo", "charter"]:
        fig.update_layout(yaxis_tickformat=".1%")
    else:
        fig.update_layout(yaxis_tickformat=".3f")

    fig.update_layout(
        margin={"l": 60, "r": 20, "t": 80, "b": 40},
        title_font_size=18,
        title_x=0.5,
        xaxis=dict(
            tickangle=45,
            title_font=dict(size=14),
            tickfont=dict(size=12),
            showgrid=False,
            dtick=2, # Show ticks every 2 years to avoid clutter
        ),
        yaxis=dict(
            title=y_label,
            title_font=dict(size=14),
            tickfont=dict(size=12),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # 6) Overlay state averages if checked (refactored for clarity and style)
    OVERLAY_LABELS = {**DEMO_LABELS, **SEG_LABELS, **CHARTER_LABELS}
    OVERLAY_STYLES = {
        "pctblk":              {"color": "#7f7f7f", "dash": "dash"}, # grey
        "pcthis":              {"color": "#ff7f0e", "dash": "dash"}, # orange
        "pctwht":              {"color": "#2ca02c", "dash": "dash"}, # green
        "pctmin_raceineq":     {"color": "#d62728", "dash": "dot"},  # red
        "iso_pctmin_raceineq": {"color": "#9467bd", "dash": "dot"},  # purple
        "dis_pctmin_raceineq": {"color": "#8c564b", "dash": "dot"},  # brown
        "fracpaychartbm":      {"color": "#e377c2", "dash": "longdash"}, # pink
        "fracpaychartdig":     {"color": "#17becf", "dash": "longdash"}, # cyan
        "ecotpct":      {"color": "#bcbd22", "dash": "longdash"}, # olive
    }

    # Combine overlays from all checklists
    all_overlays = overlays_demo + overlays_seg + overlays_charter

    for overlay_col in all_overlays:
        if overlay_col in df.columns:
            state_avg_df = (
                df.groupby("year")[overlay_col]
                  .mean()
                  .reset_index(name="state_avg")
            )

            # Correct 2012 outlier for specific columns
            if overlay_col in ["pctblk", "pcthis", "iso_pctmin_raceineq", "fracpaychartdig"]:
                is_2012 = state_avg_df["year"] == 2012
                if is_2012.any() and 2011 in state_avg_df['year'].values and 2013 in state_avg_df['year'].values:
                    avg_2011 = state_avg_df.loc[state_avg_df['year'] == 2011, 'state_avg'].iloc[0]
                    avg_2013 = state_avg_df.loc[state_avg_df['year'] == 2013, 'state_avg'].iloc[0]
                    state_avg_df.loc[is_2012, "state_avg"] = (avg_2011 + avg_2013) / 2

            style = OVERLAY_STYLES.get(overlay_col, {})
            label = OVERLAY_LABELS.get(overlay_col, overlay_col)

            fig.add_scatter(
                x=state_avg_df["year"],
                y=state_avg_df["state_avg"],
                mode="lines",
                name=f"Ohio Avg. {label}",
                line=dict(
                    dash=style.get("dash", "dash"),
                    width=2,
                    color=style.get("color", "#888") # Default to a neutral grey
                ),
                showlegend=True
            )

    return fig

if __name__ == "__main__":
    #app.run(debug=True)
    port = int(os.environ.get("PORT", 8080))  # Render sets the PORT env var
    app.run(host="0.0.0.0", port=port, debug=False)

