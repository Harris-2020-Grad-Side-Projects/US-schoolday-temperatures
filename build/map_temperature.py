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
                   add_citation = False, citation_text = '', set_extent = False):
    '''values: the column name to use for temperature values
        title: what is in that column (for the plot title)
        date: month and year of the data (for the plot title)
        colors: dictionary of temperature-color pairs,
        show_pilot_schools: overlays a scatterplot with data in pilot_df
        pilot_df: df of pilot school locations under colnames 'lan' and 'lon'
        marker_color: color of schatter plot points (only shown if show_pilot_schools is ture)
        replace_duplicate_high: input for fixed_colors()
        remove_duplicate_high: input for fixed_colors()
        add_citation: runs add_citation_text() -if true adds some citation text to the bottom
        set_extent: I grabed slightly different data ranges for summer and winter, if set_extent = True
        it resolves this discrepency on the summer data
    '''
    # Pivot data and apply meshgrid so plotable as contourform plot
    #https://stackoverflow.com/questions/24032282/create-contour-plot-from-pandas-groupby-dataframe
    df_pivoted = df.pivot(index = 'lat', columns = 'lon', values = values)
    df_pivoted.columns
    X=df_pivoted.columns
    Y=df_pivoted.index.values
    Z=df_pivoted.values
    lon,lat = np.meshgrid(X, Y)
    
    fig = plt.figure(figsize=(15,13)) #20,18
    
    # set geo axes
    ax = plt.axes(projection=ccrs.Mercator()) 

    if set_extent:
        # set map extent -summer only
        extent = (X.min(), X.max(), Y.min(), Y.max()-4.5) 
        ax.set_extent(extent)
    
    # add lines for North America
    ax.coastlines(resolution="110m",linewidth=0.9)
    # add lines for State boundries
    ax.add_feature(cf.STATES, linewidth = 0.9)
    # https://coderzcolumn.com/tutorials/data-science/cartopy-basic-maps-scatter-map-bubble-map-and-connection-map 

    ## set colors and bins -currently every 10 degrees F
    norms, cmap, norm = fixed_colors(df, values, colors, 
                                        replace_duplicate_high = replace_duplicate_high, 
                                        remove_duplicate_high = remove_duplicate_high)
    
    # plot
    plt.contourf(lon, lat, Z, transform=ccrs.PlateCarree(), levels=len(norms)-1,
                 cmap=cmap, norm=norm)

    cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, 
                      orientation="vertical", pad=0.02, aspect=16, shrink=0.5)
    cb.ax.invert_yaxis() #interts color bar so low to high 
    cb.set_label('\u00b0F',size=14,rotation=0,labelpad=4) #18
    cb.ax.tick_params(labelsize=12)
    
    plt.title('{} 8:30AM-3:30PM {}'.format(title, date), size=16)
    
    # this isn't a clean way to do this, but wrap isn't working here
    # add citation text to the bottom left
    if add_citation:
        add_citation_text(ax=ax)

    # add points for pilot school locations   
    if show_pilot_schools:
        plt.scatter(pilot_df['lon'], pilot_df['lat'], marker = 7, color = marker_color, transform=ccrs.PlateCarree())
        plt.savefig('output/{} (F) 8:30AM-3:30PM {} with pilot schools'.format(title, date))
    else:
        plt.savefig('output/{} (F) 8:30AM-3:30PM {}'.format(title, date), bbox_inches = 'tight')
    

# used in contouform_map
def fixed_colors(df, values, colors, 
                 replace_duplicate_high = False, remove_duplicate_high = False):
    '''input
        values: the column name to use for temperature values,
        colors: dictionary of temperature-color pairs,
        replace_duplicate_high: for summer, replaced the automatically generated color for 
        temps just above 100 with a specific color (hard coded)
        remove_duplicate_high: for winter, there are some points with temps just above 80
        in the ocean and that are averaged away in the contour, these are not relevant  to the map
        setting this to true removes the over 80 color from the colorbar

        Output is:
        a list of ea 10F temperature bin to be used, 
        a matplotlib cmap object (the colors to be used)
        a matplotlib norm object 
    '''
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
   
    # get colors from the colors dict
    for i in norms:
        use_colors.append(colors[i])
    
    # deal with duplicate colors at the high end
    if len((set(norms))) < len(norms):
        if replace_duplicate_high:
            use_colors[-1] = '#b30000'
        elif remove_duplicate_high:
            use_colors = use_colors[:-2]
            norms = norms[:-1]
   
    cmap = ListedColormap(use_colors)
    norm = BoundaryNorm(norms, cmap.N)

    return norms, cmap, norm

# used in contouform_map
def add_citation_text(ax):
    # this isn't a clean way to do this, but wrap isn't working here
    # add citation text to the bottom left
    plt.text(0.00, -0.03, 'Mapping and information based on data from Global Modeling and Assimilation Office (GMAO), Goddard Earth Sciences Data and Information', 
             ha='left', transform=ax.transAxes)
    plt.text(0.00, -0.06, 'Services Center(GES DISC). Map created by Sarah Gill, MPP. 2021', 
             ha='left', transform=ax.transAxes)

    #https://stackoverflow.com/questions/43087087/matplotlib-set-the-limits-for-text-wrapping


def run_summer():

    date = 'Summer 2019'#'Winter 2018-19'#
    data_folder = 'Data'
    filename = '{} temperature.csv'.format(date)
    use_file = os.path.join(data_folder, filename)
    df = pd.read_csv(use_file)
    pilot_df = pd.read_csv(os.path.join(data_folder, 'pilot_schools.csv'))


    contouform_map(df, 'average_hi', 'Average Daily Temperature (with Heat Index)', 
               date, colors, marker_color='blue', replace_duplicate_high = True,
               add_citation = True, set_extent = True)#, citation_text = 'Mapping and information based on data from Global Modeling and Assimilation Office (GMAO), Goddard Earth Sciences Data and Information Services Center (GES DISC).')


    contouform_map(df, 'average_max_daily_hi', 'Average Daily High (with Heat Index)', 
               date, colors, add_citation = True, set_extent = True)#, citation_text = 'Mapping and information based on data from Global Modeling and Assimilation Office (GMAO), Goddard Earth Sciences Data and Information Services Center (GES DISC).')

def run_winter():
    date = 'Winter 2018-19'
    data_folder = 'Data'
    filename = '{} temperature.csv'.format(date)
    use_file = os.path.join(data_folder, filename)
    df = pd.read_csv(use_file)
    pilot_df = pd.read_csv(os.path.join(data_folder, 'pilot_schools.csv'))


