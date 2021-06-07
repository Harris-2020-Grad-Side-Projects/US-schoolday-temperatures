# Check plot:
# simple point plot to verify that the controuform is not misleading


import os
import geopandas
import pandas as pd
import matplotlib.pyplot as plt

#change this only
os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures')
date = 'Winter 2020-21'
title = 'Average Daily Temp (with Wind Chill)'

#df = pd.read_csv('{} temperature.csv'.format(date))
data_folder = 'Data'
filename = '{} temperature.csv'.format(date)
data_file = os.path.join(data_folder, filename)

df = pd.read_csv(data_file)

gdf = geopandas.GeoDataFrame(df, 
                             geometry=geopandas.points_from_xy(df['lon'], df['lat']),
                             crs = 'epsg:4269') #crs for North America

#from https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
#can also get school districts here!
state_file = os.path.join(data_folder, 'cb_2019_us_state_20m/cb_2019_us_state_20m.shp')
state = geopandas.read_file(state_file)

#https://stackoverflow.com/questions/19960077/how-to-filter-pandas-dataframe-using-in-and-not-in-like-in-sql
state_abres = ['AK', 'PR', 'HI'] # contenental US only, remove Alaska, Puerto Rico and Hawaii 
contenental_states = state[~state['STUSPS'].isin(state_abres)]
#state_test.head()

fig, ax = plt.subplots(figsize=(30,8))
#contenental_states.plot(ax=ax, color = 'none', edgecolor='black')
gdf.plot(ax=ax, column = 'average_windchill', markersize = 10,
         cmap = 'RdYlBu_r', legend=True)
contenental_states.plot(ax=ax, color = 'none', edgecolor='black')

ax.axis('off')
ax.set_title('{} 8:30AM-3:30PM {}'.format(title, date),
            size=16)
plt.show()