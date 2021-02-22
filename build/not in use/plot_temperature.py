import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker

os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures/')
#date = '2020-12'
#df = pd.read_csv('{} temperature.csv'.format(date))
df = pd.read_csv('12-2020 temp and wind.csv')

df['average_temp'][(df['lat']>= 25) & (df['lat']<=26) & (df['lon']>= -80.9) & (df['lon']<= -80)]

#https://stackoverflow.com/questions/24032282/create-contour-plot-from-pandas-groupby-dataframe
df_pivoted = df.pivot(index = 'lat', columns = 'lon', values = 'average_temp')
df_pivoted.columns
X=df_pivoted.columns#.levels[1].values
Y=df_pivoted.index.values
Z=df_pivoted.values
lon,lat = np.meshgrid(X, Y)

#lon, lat = np.meshgrid(df['lon'], df['lat'])

fig = plt.figure(figsize=(20,10))
ax = plt.axes(projection=ccrs.Robinson())
ax.set_extent([-400,-180,80,300])
    #ax.set_global()
    #ax.coastlines(resolution="50m",linewidth=1)
ax.coastlines(resolution="110m",linewidth=1)
ax.gridlines(linestyle='--',color='black')

# Plot windspeed
#clevs = np.arange(0,14.5,1)
plt.contourf(lon, lat, Z, transform=ccrs.PlateCarree(),cmap=plt.cm.jet)
plt.title('Temperatur (F) Dec 2020', size=16)
cb = plt.colorbar(ax=ax, orientation="vertical", pad=0.02, aspect=16, shrink=0.8)
cb.set_label('F',size=14,rotation=0,labelpad=15)
cb.ax.tick_params(labelsize=10)
plt.savefig('test')

#base_map = Basemap(llcrnrlon=-121,llcrnrlat=20,urcrnrlon=-62,urcrnrlat=51,
#            projection='lcc',lat_1=32,lat_2=45,lon_0=-95)

#base_map.drawstates()


#notes for plot
# https://www.dkrz.de/up/services/analysis/visualization/sw/python-matplotlib/matplotlib-sourcecode/python-matplotlib-example-contour-filled-plot 
# https://stackoverflow.com/questions/16371725/getting-a-contour-plot-to-use-data-from-a-csv-file
# https://matplotlib.org/basemap/users/geography.html
