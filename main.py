#!/usr/bin/env python
# coding: utf-8

# # Task 02 - Use Bokeh + GeoPandas to plot maps.

# ### 01.import libraries

# In[1]:


import pandas as pd
import geopandas as gpd
from bokeh.models import Slider
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, HoverTool
from bokeh.layouts import column
from bokeh.palettes import Viridis256
from bokeh.models import WMTSTileSource
from bokeh.models import LinearColorMapper
from pyproj import Transformer


# ### 02. Load the  dataset

# In[2]:


df = pd.read_csv("covid_19_Global.csv")

df['Lat'] = df['Lat'].astype(str).str.replace('.', '', regex=False).astype(float)
df['Long'] = df['Long'].astype(str).str.replace('.', '', regex=False).astype(float)

# Select random 10,000 rows (without replacement)
sample_df = df.sample(n=10000, random_state=42)


# ### 03. Create GeoDataFrame

# In[3]:


gdf = gpd.GeoDataFrame(sample_df, geometry=gpd.points_from_xy(sample_df['Long'], sample_df['Lat'])) 


# ### 04.Convert lat-long to Web Mercator for Bokeh tiles

# In[4]:


transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
gdf["x"], gdf["y"] = transformer.transform(gdf["Long"].values, gdf["Lat"].values)


# ### 05. Bokeh ColumnDataSource

# In[5]:


source = ColumnDataSource(gdf)


# ### 06.Set up the main plot with tile 

# In[6]:


gdf["x"] = gdf.geometry.x
gdf["y"] = gdf.geometry.y
p = figure(x_axis_type="mercator", y_axis_type="mercator",
           title="COVID-19 Geo Dashboard", width=900, height=500)

p.add_tile("CartoDB Positron") 


# ###  07.Add color mapper

# In[7]:


color_mapper = LinearColorMapper(palette=Viridis256, low=gdf['Confirmed'].min(), high=gdf['Confirmed'].max())


# ### 08.Create figure

# In[11]:


p = figure(width=800, height=450, x_axis_type="mercator", y_axis_type="mercator")
points = p.scatter(
    x='x',
    y='y',
    source=source,
    size=8,
    color={'field': 'Confirmed', 'transform': color_mapper}, 
    alpha=0.6,
    legend_label="Confirmed Cases"
)


# ### 09. Add color bar

# In[9]:


color_bar = ColorBar(color_mapper=color_mapper, 
                     label_standoff=12, 
                     width=8, 
                     location=(0,0), 
                     title="Confirmed Cases")

p.add_layout(color_bar, 'right')


# # Task 03 -  Add interactive elements

# ## 1.Hover Tooltips

# In[12]:


hover = HoverTool(
    renderers=[points], 
    tooltips=[
        ("Country", "@{Country/Region}"),
        ("Province/State", "@{Province/State}"),
        ("Confirmed Cases", "@Confirmed"),
        ("Deaths", "@Deaths"),
        ("Recovered", "@Recovered"),
        ("Date", "@Date{%F}"),   
        ("Location", "(@Lat, @Long)")
    ],
    formatters={
        '@Date': 'datetime' 
    }
)

p.add_tools(hover)
print("Hover tooltips added.")


# ## 2.Time slider for filtering by date

# In[ ]:


dates = sorted(gdf['Date'].unique())
initial_gdf = gdf[gdf['Date'] == dates[0]]
source = ColumnDataSource(initial_gdf)

def update(attr, old, new):
    selected_date = dates[slider.value]
    filtered = gdf[gdf['Date'] == selected_date]
    source.data = ColumnDataSource.from_df(filtered)

slider = Slider(start=0, end=len(dates)-1, value=0, step=1, title="Date")
slider.on_change('value', update)

# --- Step 10: Layout ---
layout = column(p, slider)
curdoc().add_root(layout)
curdoc().title = "COVID-19 GeoDashboard"
print("Time slider added.")


# ## 3.Filter for risk categories

# In[ ]:


def categorize_risk(confirmed):
    if confirmed > 10000:
        return "High"
    elif confirmed > 1000:
        return "Medium"
    else:
        return "Low"

gdf['RiskCategory'] = gdf['Confirmed'].apply(categorize_risk)

from bokeh.models import Select
from bokeh.layouts import column

risk_select = Select(title="Risk Category:", value="All", options=["All", "High", "Medium", "Low"])

def update(attr, old, new):
    selected_date = dates[slider.value]
    
    filtered = gdf[gdf['Date'] == selected_date]
    
    selected_category = risk_select.value
    if selected_category != "All":
        filtered = filtered[filtered['RiskCategory'] == selected_category]
        source.data = ColumnDataSource.from_df(filtered)

slider.on_change('value', update)
risk_select.on_change('value', update)

print("Risk filter added.")


# ### Update Layout

# In[ ]:


layout = column(p, slider, risk_select)
curdoc().add_root(layout)
curdoc().title = "COVID-19 GeoDashboard"
curdoc().add_root(p)
print("Dashboard setup complete. Running Bokeh server...")


# # Task 04 - Choropleth-style Visualization

# ### 1.Create color mapper based on Confirmed cases 

# In[ ]:


from bokeh.models import LinearColorMapper, ColorBar
from bokeh.palettes import Plasma256

choropleth_mapper = LinearColorMapper(
    palette=Plasma256,  # Color palette for intensity
    low=gdf['Confirmed'].min(),
    high=gdf['Confirmed'].max(),
    nan_color='blue'  # Color for missing values
)


# ### 2.Plot circle points with intensity coloring

# In[ ]:


p.renderers = [p.renderers[0]]

choropleth_points = p.scatter(
    x='x',
    y='y',
    source=source,
    size=12, 
    color={'field': 'Confirmed', 'transform': choropleth_mapper},
    alpha=0.8,
    line_color='white',
    line_width=0.5,
    legend_label="Confirmed Cases"
)


# ### 3.Add color bar

# In[ ]:


color_bar = ColorBar(
    color_mapper=choropleth_mapper,
    label_standoff=15,
    width=20,
    height=400,
    location=(0, 0),
    title="Confirmed Cases",
    title_text_font_size='12pt'
)
p.add_layout(color_bar, 'right')

print("Choropleth-style visualization added with intensity-based coloring.")

