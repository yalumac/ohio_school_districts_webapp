---
output:
  pdf_document: default
  html_document: default
---
**Ohio School Districts Web App**

Welcome to the Ohio School Districts Web App! This interactive Dash application allows users to explore demographic, segregation, charter school enrollment trends across Ohio’s school districts over time. Built with Python, Plotly Dash, and GeoPandas, it combines map-based choropleth visualizations with linked time-series charts for an engaging, data-driven experience.

---

## Table of Contents

1. [Features](#features)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Running the App](#running-the-app)
3. [Application Layout & Functionality](#application-layout--functionality)
   - [Map & Year Slider](#map-year-slider)
   - [Measure Type Toggle](#measure-type-toggle)
   - [Measure Dropdowns](#measure-dropdowns)
   - [Time Series & Overlays](#time-series-overlays)
   - [Responsive Design](#responsive-design)
4. [Customization & Extension](#customization-extension)
   - [Data Inputs](#data-inputs)
   - [Adding New Measures](#adding-new-measures)
   - [Styling & Layout](#styling-layout)
   - [Performance Tuning](#performance-tuning)
5. [Architecture Overview](#architecture-overview)
6. [Future Improvements](#future-improvements)
7. [Acknowledgements](#acknowledgements)

---

## Features

- **Interactive Choropleth Map**: Visualize district-level demographic and segregation measures on a static, zoomable Ohio map.
- **Year Slider**: Slide through years to animate changes over time, with angled tick labels for clarity.
- **Measure Type Toggle**: Switch between demographic measures (% Black, % Hispanic, % White), segregation indices (Exposure, Isolation, Dissimilarity), and charter share (Virtual, B&M, ECOT).
- **Linked Time Series**: Click a district on the map to display its trend over time in the adjacent chart.
- **Statewide Overlays**: Overlay Ohio-wide average trends for selected measures via intuitive checkboxes.
- **Responsive Design**: Fluid Bootstrap-powered layout that adapts seamlessly to desktops, tablets, and mobile devices.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Virtual environment (strongly recommended)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ohio-school-districts-webapp

# Set up a virtual environment
python -m venv venv
# Activate:
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
# Launch the Dash app
gunicorn ohio_school_districts_webapp:app --workers 1 --reload --bind 0.0.0.0:8050
# Or, for development:
python ohio_school_districts_webapp.py --port 8060
```

Then open `http://localhost:8050` in your browser (or replace with your host/port).

---

## Application Layout & Functionality

### Map & Year Slider

- **Choropleth Map**: Uses Plotly Express to render Ohio school district polygons filled by the chosen metric. GeoJSON is simplified for performance.
- **Year Slider**: Positioned directly beneath the map; tick labels are styled with a 45° rotation and additional bottom margin for readability.

### Measure Type Toggle

- A set of radio buttons lets you choose **Demographic**,  **Segregation**, or  **Charter Share**. Based on selection, the appropriate dropdown becomes visible.

### Measure Dropdowns

- **Demographic Measures**: `% Black`, `% Hispanic`, `% White`. Selecting one updates the map coloring and the time-series chart. 
- **Segregation Measures**: `Dissimilarity Index`, `Isolation Index`, `Exposure Index`. Works identically to demographics. 
- **Charter Share**: `Virtual Charter Share`, `B&M Charter Share`, `ECOT Share`. This dropdown allows users to view the proportion of district students who enroll in virtual or brick-and-mortar charter schools. Selecting this pull‐down repaints both the map and time series to reflect charter penetration by district. In instances where districts do not have charter enrollment data, the displayed map is empty. 

### Time Series & Overlays

- **Primary Line**: Plots the selected district’s metric over time. Legend entry is explicitly set to "District {leaid} {Measure Label}."
- **Overlay Checkboxes**: Below the chart, checkboxes for statewide averages of key measures (e.g., Ohio % Black, Ohio Isolation Index). When checked, dashed or dotted lines are added dynamically.
- **Interactive Legend**: All traces (district & overlays) appear with distinct names and styles, enabling toggling on/off. To avoid clutter, refrain from checking too many boxes. 

### Responsive Design

Built with Dash Bootstrap Components:

- **Container**: `dbc.Container(fluid=True)` provides full-width responsiveness.
- **Grid**: `dbc.Row` and `dbc.Col` specify column widths at breakpoints (`xs`, `sm`, `md`, `lg`).
- **Graphs**: `config={'responsive': True}` and percentage/`vh` sizing ensure charts resize correctly.

---

## Customization & Extension

### Data Inputs

- **CSV Schema**: Ensure your data has `leaid` (string), `year` (int), and metric columns (float 0–1).
- **GeoJSON**: Swap in any custom boundary file; update `featureidkey='properties.leaid'` as needed.
- **Preprocessing**: Scripts handle `.0` stripping, NA-dropping, and optional outlier smoothing (IQR, winsorizing, or rolling averages).

### Adding New Measures

1. **Label Dictionaries**: Extend `DEMO_LABELS` or `SEG_LABELS` at the top of the app.
2. **Dropdown Options**: Add new items to `demo-dropdown` or `seg-dropdown` options.
3. **Overlay Logic**: Include new checkbox options in `overlay-checkboxes` and define their line styles in `overlay_styles` within the time series callback.

### Styling & Layout

- **Themes**: Replace `dbc.themes.BOOTSTRAP` with other Bootswatch themes (e.g., `CYBORG`, `SOLAR`) for a fresh look.
- **Color Scales**: Modify `color_continuous_scale` in the map callback or apply Plotly templates (`plotly_white`, `ggplot2`).
- **Global CSS**: Place custom styles in `/assets/custom.css` (e.g., font-family: Arial globally, breakpoint-specific margin adjustments).

### Performance Tuning

- **Caching**: Leverage Flask-Caching decorators (`@cache.memoize`) to store heavy computations (GeoJSON loads, grouped means).
- **GeoJSON Simplification**: Use `gdf.simplify(tolerance=…)` to reduce polygon complexity if needed.
- **Debounce Controls**: Enable `debounce=True` on sliders to limit callback frequency during dragging.

---

## Architecture Overview

1. **App Initialization**: Creates Dash app with Bootstrap theme and loads data.
2. **Layout Definition**: Combines header, control panels, map/slider left column, time series/overlays right column, and hidden `dcc.Store`.
3. **Callbacks**:
   - `update_map`: Listens to year, dropdowns, and radio selections; returns a choropleth figure.
   - `update_time_series`: Listens to `leaid`, controls, and overlays; returns a multi-trace line chart.
4. **Data Merge**: GeoDataFrame and CSV DataFrame are merged on `leaid`, ensuring one-to-many relationships by year.

---

## Future Improvements

- **Localization**: Externalize UI text for multilingual support.
- **User Sessions**: Add login and persistent user settings (favorite districts, bookmarks).
- **Annotations**: Integrate contextual notes on historical policy changes or key events.
- **Export Options**: Enable data/figure downloads (CSV, PNG, SVG).
- **Advanced Analytics**: Build clustering and small-multiples dashboards for comparative exploration.
- **Narrative Insights**: Generate auto-summaries of trends using NLP techniques.

---

## Acknowledgements

- Powered by [Plotly Dash](https://dash.plotly.com/) & [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/).
- Geospatial processing courtesy of [GeoPandas](https://geopandas.org/).
- Data sourced from the National Center for Education Statistics (NCES) and the Ohio Department of Education (ODE).

Enjoy exploring and expanding on this app. I welcome collaborations to extend this app to other states or jurisdictions. Together, our passion make data come alive!
