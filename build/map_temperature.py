import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
import cartopy.feature as cf 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap, BoundaryNorm
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures')
date = 'Summer 2019'#'Winter 2018-19'#
data_folder = 'Data'
filename = '{} temperature.csv'.format(date)
use_file = os.path.join(data_folder, filename)

df = pd.read_csv(use_file)
pilot_df = pd.read_csv(os.path.join(data_folder, 'pilot_schools.csv'))

colors = {110.0: '#a50026',
          100.0: '#d73027',
          90.0: '#cb181d', 
          80.0: '#f16913',
          70.0:'#feb24c',
          60.0:'#fed976',
          50.0:'#ffffcc',
          40.0:'#99d8c9',
          30.0: '#74add1',
          20.0: '#4575b4',
          10.0: '#313695',
          0.0: '#542788',
         -10.0: '#3f007d',
         -20.0: '#2d004b',
         -30.0: '#252525'}


def contouform_map(df, values, title, date, colors, 
                   show_pilot_schools = False, pilot_df = None, marker_color = 'red', 
                   replace_duplicate_high = False, remove_duplicate_high = False,
                   add_citation = False, citation_text = ''):
    '''values: the column name to use for temperature values
        title: what is in that column (for the plot title)
        date: month and year of the data (for the plot title)
        colors: dictionary of temperature color pairs,
    '''
    # Pivot data and apply meshgrid so plotable as contourform plot
    #https://stackoverflow.com/questions/24032282/create-contour-plot-from-pandas-groupby-dataframe
    df_pivoted = df.pivot(index = 'lat', columns = 'lon', values = values)
    df_pivoted.columns
    X=df_pivoted.columns#.levels[1].values
    Y=df_pivoted.index.values
    Z=df_pivoted.values
    lon,lat = np.meshgrid(X, Y)
    
    fig = plt.figure(figsize=(20,18)) #12,10
    
    # set geo axes
    ax = plt.axes(projection=ccrs.Mercator()) 

    # set map extent -not needed
    extent = (X.min(), X.max(), Y.min(), Y.max()-4.5) # -4.5 for summmer, the Y-max is greater than the data?! (does this mean there's a problem?)
    ax.set_extent(extent)
    
    # add North America
    ax.coastlines(resolution="110m",linewidth=0.9)
    # add State boundries
    ax.add_feature(cf.STATES, linewidth = 0.9)
    # https://coderzcolumn.com/tutorials/data-science/cartopy-basic-maps-scatter-map-bubble-map-and-connection-map 

    ## set colors and bins -currently every 10 degrees F
    use_colors = []
    rounded_temps = []

    for i in df[values]:
        if round(i,0) in colors.keys():
            rounded_temps.append(round(i,0))

    norms = sorted(list(set(rounded_temps)))  
    
    # deal with boundries (e.g min of 9 F needs to go to 0, max of 61F needs to go to 70)
    if df[values].min()<norms[0]:
        norms = [round(df[values].min()-5, -1)] + norms
        
    if df[values].max()>norms[-1]:
        norms.append(round(df[values].max()+4, -1))    
   
    #get colors from the colors dict
    for i in norms:
        use_colors.append(colors[i])
    
    #deal with duplicate colors at the high end
    
    if len((set(norms))) < len(norms):
        if replace_duplicate_high:
            use_colors[-1] = '#b30000'
        elif remove_duplicate_high:
            use_colors = use_colors[:-2]
            norms = norms[:-1]
   
    cmap = ListedColormap(use_colors)
    norm = BoundaryNorm(norms, cmap.N)

    #plot
    plt.contourf(lon, lat, Z, transform=ccrs.PlateCarree(), levels=len(norms)-1,
                 cmap=cmap, norm=norm)

    
    cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, 
                      orientation="vertical", pad=0.02, aspect=16, shrink=0.5)
    cb.ax.invert_yaxis() #interts color bar so low to high 
    cb.set_label('\u00b0F',size=18,rotation=0,labelpad=15)
    cb.ax.tick_params(labelsize=15)
    
    plt.title('{} 8:30AM-3:30PM {}'.format(title, date), size=22)
    
    # this is a crazy way to do this, but wrap isn't working 
    # add citation text to the bottom left
    if add_citation:
        plt.text(0.00, -0.03, 'Mapping and information based on data from Global Modeling and Assimilation Office (GMAO), Goddard Earth Sciences Data and', 
                 ha='left', transform=ax.transAxes, fontsize = 14)
        plt.text(0.00, -0.06, 'Information Services Center(GES DISC). Map created by Sarah Gill, MPP. 2021', 
                 ha='left', transform=ax.transAxes, fontsize = 14)
        
        '''plt.text(0.00, -0.02, citation_text, 
                 ha='left', transform=ax.transAxes)
        plt.text(0.00, -0.04,  'Map created by Sarah Gill, MPP. 2021', 
                 ha='left', transform=ax.transAxes)
        '''
       
        '''
        plt.text(0.01, 0.09, 'Mapping and information based on data from', 
                 ha='left', wrap=True, transform=ax.transAxes)
        plt.text(0.01, 0.07, 'Global Modeling and Assimilation Office (GMAO),', 
                 ha='left', wrap=True, transform=ax.transAxes)
        plt.text(0.01, 0.05, 'Goddard Earth Sciences Data and Information', 
                 ha='left', wrap=True, transform=ax.transAxes)
        plt.text(0.01, 0.03, 'Services Center(GES DISC).', 
                 ha='left', wrap=True, transform=ax.transAxes)
        plt.text(0.01, 0.01, 'Map created by Sarah Gill, MPP. 2021.', 
                 ha='left', wrap=True, transform=ax.transAxes)'''
        #https://stackoverflow.com/questions/43087087/matplotlib-set-the-limits-for-text-wrapping
        
    if show_pilot_schools:
        plt.scatter(pilot_df['lon'], pilot_df['lat'], marker = 7, color = marker_color, transform=ccrs.PlateCarree())
        plt.savefig('output/{} (F) 8:30AM-3:30PM {} with pilot schools'.format(title, date))
    else:
        plt.savefig('output/{} (F) 8:30AM-3:30PM {}'.format(title, date))
    

contouform_map(df, 'average_hi', 'Average Daily Temperature (with Heat Index)', 
               date, colors, marker_color='blue', replace_duplicate_high = True,
               add_citation = True)

