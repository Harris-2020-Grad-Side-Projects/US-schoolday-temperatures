'''
Data from:
https://disc.gsfc.nasa.gov/datasets/M2T1NXSLV_5.12.4/summary 

Dataset: MERRA-2 tavg1_2d_slv_Nx: 2d,1-Hourly,Time-Averaged,Single-Level,Assimilation,Single-Level Diagnostics V5.12.4
Download Method: Get File Subsets using the GES DISC Subsetter
Date Range: 2018-12-21 to 2019-03-19 #For "Winter"
Region: -125.244, 24.961, -67.061, 49.395 (Search and Crop)
Time of Day: 11:30 to 23:30
Variables:
TS = surface skin temperature
U2M = 2-meter eastward wind
V2M = 2-meter northward wind
Format: netCDF

TS (temperature) is a list of lists of lists
outer: 13 lists one for each time
next: 50 lists one for each lat
inner: 95 temperatures one for each lon
     
Current code converts to pandas df, breaks into time zones, subsets to school hours only and aggregates
Code also calculates windspeed, uses this to calculate windchill, and adds this variable 

Output is a dataset with aggrogated temperature data for each lat-lon coordinate 
from the hours of 8:30AM-3:30PM in each US timezone
'''

import pandas as pd
import xarray as xr
import datetime
import os
import numpy as np

pd.set_option('mode.chained_assignment', None) # ignore the SettingWithCopy Warning (add column for local time in parse_temperature())



####Global Variables
os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures/')
data_folder = 'Data/MERRA2_Winter18-19'
DATE = 'Winter 2018-19'


data = os.listdir(data_folder) #object to pass in the filenames

# thinking I'll restructure this to be a df with ea time zone as a row and cols:
# lon_west_boundry, lon_east_boundry, utc_time_delta
# lat lon for each timezone
pacific_lon = [-125, -114] #ish
mountain_lon = [-114, -102] #ish
central_lon = [-102, -85.5] #ish
eastern_lon = [-85.5, -65] #ish
time_deltas = {'pacific': 8, 'mountain':7, 'central':6, 'eastern':5}

def ns_to_df(filename):
    '''input: ns file from MERRA2 (satelite data)
    output: pandas df
    '''
    f = os.path.join(data_folder, filename)
    date = f[-15:-11]+"-"+f[-11:-9]+"-"+f[-9:-7]
    print(date) # debug
    
    # read in netcdf data
    # https://stackoverflow.com/questions/14035148/import-netcdf-file-to-pandas-dataframe
    nc_data = xr.open_dataset(f)
    df = nc_data.to_dataframe()
    df = df.reset_index()
    
    # quick check for errors
    assert df['TS'].min() > 216.5 # a bit warmer than -70F (record low in US excluding Alaska)
    assert df['TS'].max() < 330 # a bit colder than 134F (recod high in US)
    
    return df


def get_schoolhours(filename, df, time_zone_lons, time_delta):
    '''input: pandas df from ns_to_df with variables 'TS', '...'
    lon boundries for the selected timezone and the time differnece from UTC
    
    output: pandas df with values for 8:30AM-3:30PM local time for one timezone
    '''
    date = filename[-15:-11]+"-"+filename[-11:-9]+"-"+filename[-9:-7]
    # subset to one time zone
    time_zone_df = df[(df["lon"]>= time_zone_lons[0]) & (df["lon"]< time_zone_lons[1])]
    
    # add local time 
    # throws a warning (both ways shown here)
    #time_zone_df['local_time'] = time_zone_df['time'] - datetime.timedelta(hours=time_delta)
    time_zone_df['local_time'] = time_zone_df['time'].apply(lambda x: x - datetime.timedelta(hours=time_delta))
    
    
    #subset to school-hrs only (8:30AM-3:30PM)
    school_str = pd.to_datetime('{} 8:30:00'.format(date))
    school_end = pd.to_datetime('{} 15:30:00'.format(date)) 

    time_zone_df = time_zone_df[(time_zone_df["local_time"]>= school_str) & 
                                (time_zone_df["local_time"]<= school_end)]
    
    # check
    assert time_zone_df.iloc[12]['local_time'] == pd.to_datetime('{} 12:30:00'.format(date))

    return time_zone_df

def something(df):
    
    # add wind speed
    # https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20calculate%20and%20plot%20wind%20speed%20using%20MERRA-2%20wind%20component%20data%20using%20Python#!
    df['wind_speed_(mph)'] = np.sqrt(df['U2M']**2+df['V2M']**2)*(2.236942)
    
    # add temp in F
    df['temperature_(F)'] = (df['TS'] - 273.15)* 1.8000 + 32.00
    
    # add wind chill (F) 
    # windchill only if temperature is 50F or below and wind is 3mph or faster
    df['with_windchill_(F)'] = np.where(
                                    (df['temperature_(F)']<= 50) & (df['wind_speed_(mph)']>=3), 
                                    (35.74 
                                        + 0.6215*df['temperature_(F)'] 
                                        - 35.75*df['wind_speed_(mph)']**0.16
                                        + 0.4275*df['temperature_(F)']*df['wind_speed_(mph)']**0.16),
                                    df['temperature_(F)'])
    
    # add dummy for hr below freezing
    # df['below_freezing'] = df['TS'].apply(lambda x: 1 if x <= 273.15 else 0)
    # df['below_freezing'] = df['below_freezing'].astype(int)
    
    return df
    

def aggrogate(df):
    
    # aggrogate by location (get daily average temp, daily min and count of hrs belwo freezing)
    # https://www.statology.org/pandas-groupby-aggregate-multiple-columns/

    #return time_zone_df # debug
       
    grouped = df.groupby(['lat', 'lon']).agg({'temperature_(F)': ['mean', 'min'], 
                                              'with_windchill_(F)': ['mean', 'min']})
                                                         # 'below_freezing': 'sum'})
    
    grouped.columns = ['average_temp', 'min_daily_temp', 
                       'average_temp_with_windchill', 'min_daily_temp_with_windchill']
                       #'hrs_below_freezing']
    
    final = grouped.reset_index()
    
    # add  dummy for if the day dropped below freezing at any time(hr)
    #final['day_below_freezing'] = final['hrs_below_freezing'].apply(lambda x: 1 if x >= 1 else 0)
    #final['day_below_freezing'] = final['day_below_freezing'].astype(int)
    #print(tz_final.shape)
    
    return final


# will want a way to run these more sucinctly
def get_one_day(filename):
    df = ns_to_df(filename)

    pst = get_schoolhours(filename, df, pacific_lon, time_deltas['pacific'])
    mst = get_schoolhours(filename, df, mountain_lon, time_deltas['mountain'])
    cst = get_schoolhours(filename, df, central_lon, time_deltas['central'])
    est = get_schoolhours(filename, df, eastern_lon, time_deltas['eastern'])
    
    conc_df = pd.concat([pst, mst, cst, est], ignore_index=True)
    
    final_df = aggrogate(something(conc_df))
    
    return final_df

def agg_month():
    month_df = pd.DataFrame(columns=['lat', 'lon', 'average_temp', 'min_daily_temp', 
                                    'average_temp_with_windchill', 'min_daily_temp_with_windchill'])
                            
    for f in data:
        if f.endswith('.nc'):
            conc_df = get_one_day(f)
            month_df = pd.concat([month_df, conc_df], ignore_index=True)

    #month_df.shape #debug

    month_grouped = month_df.groupby(['lat', 'lon']).agg({'average_temp': 'mean',
                                                        'min_daily_temp': ['mean', 'min'],
                                                        'average_temp_with_windchill': 'mean',
                                                        'min_daily_temp_with_windchill': ['mean', 'min']})
                                                        #'hrs_below_freezing': ['mean','sum'],
                                                        #'day_below_freezing': 'sum'})

    #month_grouped.head() #debug
    month_grouped.columns = ['average_temp', 
                            'average_min_daily_temp', 'min_min_daily_temp',
                            'average_windchill',
                            'average_min_daily_windchill', 'min_min_daily_windchill']
    
    month_final = month_grouped.reset_index()

    month_final.to_csv('Data/{} temp and wind.csv'.format(DATE))

if __name__ == "__main__":
    agg_month()

