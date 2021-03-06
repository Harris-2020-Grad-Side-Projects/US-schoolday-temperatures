'''
Data from:
https://disc.gsfc.nasa.gov/datasets/M2T1NXSLV_5.12.4/summary 
Citation:
Global Modeling and Assimilation Office (GMAO) (2015), MERRA-2 tavg1_2d_slv_Nx: 2d,1-Hourly,
Time-Averaged,Single-Level,Assimilation,Single-Level Diagnostics V5.12.4, Greenbelt, MD, USA, 
Goddard Earth Sciences Data and Information Services Center (GES DISC), Accessed: [2-19-2021], 
10.5067/VJAFPLI1CSIV

Dataset: MERRA-2 tavg1_2d_slv_Nx: 2d,1-Hourly,Time-Averaged,Single-Level,Assimilation,Single-Level Diagnostics V5.12.4
Download Method: Get File Subsets using the GES DISC Subsetter
Date Range: 2018-12-21 to 2019-03-19 #for Winter
Region: -125.068, 24.258, -66.533, 50.273 (Search and Crop)
Time of Day: 11:30 to 23:30
Variables:
T2M = 2-meter air temperature
T2MDEW = dew point temperature at 2 m
TS = surface skin temperature
U10M = 10-meter eastward wind
V10M = 10-meter northward wind
Format: netCDF
    
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
os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures/Data')
data_folder = 'Winter-new'
DATE = 'Winter 2018-19' # for output filename

data = os.listdir(data_folder) #object to pass in the filenames

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
    print(date) # debug -see which file is being run -> verify working
    
    # read in netcdf data
    # https://stackoverflow.com/questions/14035148/import-netcdf-file-to-pandas-dataframe
    nc_data = xr.open_dataset(f)
    df = nc_data.to_dataframe()
    df = df.reset_index()
    
    # quick check for temperature entering errors/typos
    assert df['T2M'].min() > 216.5 # a bit warmer than -70F (record low in US excluding Alaska)
    assert df['T2M'].max() < 330 # a bit colder than 134F (recod high in US)
    assert df['T2MDEW'].min() > 216.5 # a bit warmer than -70F (record low in US excluding Alaska)
    assert df['T2MDEW'].max() < 330 # a bit colder than 134F (recod high in US)

    return df


def get_schoolhours(filename, df, time_zone_lons, time_delta):
    '''input: pandas df from ns_to_df with variables 'TS', '...'
    lon boundries for the selected timezone and the time differnece from UTC
    
    output: pandas df with values for 8:30AM-3:30PM local time for one timezone
    '''
    # get the date from the filename (needed for time subset bc the time col has date and time)
    date = filename[-15:-11]+"-"+filename[-11:-9]+"-"+filename[-9:-7]
    # subset to one time zone
    time_zone_df = df[(df["lon"] >= time_zone_lons[0]) & (df["lon"] < time_zone_lons[1])]
    
    # add local time 
    # throws a warning (both ways shown here)
    #time_zone_df['local_time'] = time_zone_df['time'] - datetime.timedelta(hours=time_delta)
    time_zone_df['local_time'] = time_zone_df['time'].apply(lambda x: x - datetime.timedelta(hours=time_delta))
    
    
    #subset to school-hrs only (8:30AM-3:30PM)
    school_str = pd.to_datetime('{} 8:30:00'.format(date))
    school_end = pd.to_datetime('{} 15:30:00'.format(date)) 

    time_zone_df = time_zone_df[(time_zone_df["local_time"] >= school_str) & 
                                (time_zone_df["local_time"] <= school_end)]
    
    # spot-check
    assert time_zone_df.iloc[12]['local_time'] == pd.to_datetime('{} 12:30:00'.format(date))

    return time_zone_df

def relative_humidity(temp, dewpt):
    '''input columns temps in Kelvin
    '''
    return metpy.calc.relative_humidity_from_dewpoint(
                            [temp]*units.K,
                            [dewpt]*units.K).magnitude[0]

def add_alt_temps(df):
    '''
    adds wind speed, wind chill, temperature in F and hrs below freezing
    '''
    
    # add wind speed
    # https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20calculate%20and%20plot%20wind%20speed%20using%20MERRA-2%20wind%20component%20data%20using%20Python#!
    df['wind_speed_(mph)'] = np.sqrt(df['U10M']**2 + df['V10M']**2)*(2.236942)
    
    # add temp in F
    #df['temperature_(F)'] = (df['TS'] - 273.15)*1.8000 + 32.00
    df['2mtemperature_(F)'] = (df['T2M'] - 273.15)*1.8000 + 32.00
    # add wind chill (F) 
    # windchill only if temperature is 50F or below and wind is 3mph or faster
    '''
    df['with_windchill_(F)'] = np.where(
                                    (df['2mtemperature_(F)']<= 50) & (df['wind_speed_(mph)']>=3), 
                                    (35.74 
                                     + 0.6215*df['2mtemperature_(F)'] 
                                     - 35.75*df['wind_speed_(mph)']**0.16
                                     + 0.4275*df['2mtemperature_(F)']*df['wind_speed_(mph)']**0.16),
                                    df['2mtemperature_(F)'])
    '''
    df['with_windchill_(F)'] = np.where(
                                (df['2mtemperature_(F)'] <= 50) & (df['wind_speed_(mph)'] >= 3), 
                                    (metpy.calc.windchill([df['2mtemperature_(F)']]*units.degF,
                                    [df['wind_speed_(mph)']]*units.mph).magnitude[0]),
                                    df['2mtemperature_(F)'])

    
    # https://www.geeksforgeeks.org/python-pass-multiple-arguments-to-map-function/
    #df['Relative_Humidity'] = list(map(relative_humidity, df['T2M'],df['T2MDEW']))
    # https://stackoverflow.com/questions/28457149/how-to-map-a-function-using-multiple-columns-in-pandas
    df['Relative_Humidity'] = df.apply(lambda x: relative_humidity(x['T2M'], x['T2MDEW']), axis = 1)

    # add heat index
    # heat index only if 80F or higher
    df['with_heatindex_(F)'] = np.where(
                                        (df['2mtemperature_(F)'] >= 80), 
                                            (metpy.calc.heat_index([df['2mtemperature_(F)']]*units.degF,
                                            [df['Relative_Humidity']]*units.dimensionless).magnitude[0]), 
                                            df['2mtemperature_(F)'])

    # add dummy for hr below freezing
    #df['below_freezing'] = df['TS'].apply(lambda x: 1 if x <= 273.15 else 0)
    # df['below_freezing'] = df['below_freezing'].astype(int)
    
    return df

# Notes -not yet integrated at all
def heat_index(df):
    # python fns! https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.html
    #looks like I can do RH to HI or Dewpoint to HI (Dewpoint is availible)
    # RH -> HI python https://github.com/beamerblvd/weatherlink-python/blob/master/weatherlink/utils.py 
    # add temp in C
    df['temperature_(C)'] = (df['TS'] - 273.15)

    # add dewpoint in C
    df['TDEW_C'] = (df['T2MDEW'] - 273.15)
    
    # add relative humidity RH
    # multiple equations!
    # https://earthscience.stackexchange.com/questions/16570/how-to-calculate-relative-humidity-from-temperature-dew-point-and-pressure
    
    #paper on it https://mathscinotes.com/wp-content/uploads/2016/03/87878main_H-937.pdf
    # https://www.ajdesigner.com/phphumidity/dewpoint_equation_relative_humidity.php

    # or -loose estimation
    #-(Td - T)*5+100 = RH

    #equation from https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
    #multiple adjustments -not yet shown here!
    '''
    The equation used by the NWS to estimate heat index was developed by George Winterling in 1978, and is meant to be valid for temperatures of 80°F or higher, and relative humidity of 40% or more.
    https://www.calculator.net/heat-index-calculator.html

    ...
    HI = -42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH - .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH + .00085282*T*RH*RH - .00000199*T*T*RH*RH
    where T is temperature in degrees F and RH is relative humidity in percent.

    dataset has QV2M 2-meter specific humidity kg kg-1
    and has
    T2MDEW = dew point temperature at 2 m
    T2MWET = wet bulb temperature at 2 m
    '''
    #dewpoint to RH
    # K -> C
    # actual vapor presure = 6.11 * 10(7.5*T2MDEW(C)/(237.3+T2MDEW(C))) 
    #divided by
    # standard vapor presure = 6.11 * 10(7.5*TS(C)/(237.3+TS(C)))
    


    df['with_heatindex_(F)'] = np.where(df['temperature_(F)'] >= 80,
                                        (-42.379
                                         + 2.04901523*df['temperature_(F)'] 
                                         + 10.14333127*RH 
                                         - .22475541*df['temperature_(F)']*RH 
                                         - .00683783*df['temperature_(F)']*df['temperature_(F)'] 
                                         - .05481717*RH*RH 
                                         + .00122874*df['temperature_(F)']*df['temperature_(F)']*RH 
                                         + .00085282*df['temperature_(F)']*RH*RH 
                                         - .00000199*df['temperature_(F)']*df['temperature_(F)']*RH*RH),
                                        df['temperature_(F)'])


def aggrogate(df):
    
    # aggrogate by location (get daily average temp, daily min and count of hrs belwo freezing)
    # https://www.statology.org/pandas-groupby-aggregate-multiple-columns/

    #return time_zone_df # debug
       
    grouped = df.groupby(['lat', 'lon']).agg({'2mtemperature_(F)': ['mean', 'min'], 
                                              'with_windchill_(F)': ['mean', 'min'],
                                              'with_heatindex_(F)': ['mean', 'max']})#,
                                                          #'below_freezing': 'sum'})
    
    grouped.columns = ['average_temp', 'min_daily_temp', 
                       'average_temp_with_windchill', 'min_daily_temp_with_windchill',
                       'average_temp_with_hi', 'max_daily_temp_with_hi']#,
                       #'hrs_below_freezing']
    
    final = grouped.reset_index()
    
    # add  dummy for if the day dropped below freezing at any time(hr)
    #final['day_below_freezing'] = final['hrs_below_freezing'].apply(lambda x: 1 if x >= 1 else 0)
    #final['day_below_freezing'] = final['day_below_freezing'].astype(int)
    #print(tz_final.shape)
    
    return final


def get_one_day(filename):
    '''
    takes an ns file, converts to pandas df (using ns_to_df)
    breaks into 4 dfs, one for each timezone, using global variables for lon boundries and 
    time delta from UTC
    adds variables using (add_alt_temps)
    aggrogates to a df for one day
    '''
    df = ns_to_df(filename)

    pst = get_schoolhours(filename, df, pacific_lon, time_deltas['pacific'])
    mst = get_schoolhours(filename, df, mountain_lon, time_deltas['mountain'])
    cst = get_schoolhours(filename, df, central_lon, time_deltas['central'])
    est = get_schoolhours(filename, df, eastern_lon, time_deltas['eastern'])
    
    conc_df = pd.concat([pst, mst, cst, est], ignore_index=True)
    
    final_df = aggrogate(add_alt_temps(conc_df))
    
    return final_df

'''
filename = data[0]
df = ns_to_df(filename)
pst = get_schoolhours(filename, df, pacific_lon, time_deltas['pacific'])
mst = get_schoolhours(filename, df, mountain_lon, time_deltas['mountain'])
cst = get_schoolhours(filename, df, central_lon, time_deltas['central'])
est = get_schoolhours(filename, df, eastern_lon, time_deltas['eastern'])
conc_df = pd.concat([pst, mst, cst, est], ignore_index=True)
df1 = add_alt_temps(conc_df)      
df1.to_csv('one_day.csv')
'''

def agg_month():
    '''
    Aggrogates the entire set of files in a folder -global varaible "data"
    '''
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
                                                        'min_daily_temp_with_windchill': ['mean', 'min'],
                                                        'average_temp_with_hi':['mean'],
                                                         'max_daily_temp_with_hi':['mean']})#,
                                                        #'hrs_below_freezing': ['mean','sum']})#,
                                                        #'day_below_freezing': 'sum'})

    #month_grouped.head() #debug
    month_grouped.columns = ['average_temp', 
                            'average_min_daily_temp', 'min_min_daily_temp',
                            'average_windchill',
                            'average_min_daily_windchill', 'min_min_daily_windchill',
                            'average_hi', 'average_max_daily_hi']#,
                            #'avg_hrs_below_fr', 'total_hr_below_fr']
    
    month_final = month_grouped.reset_index()

    month_final.to_csv('{} temperature.csv'.format(DATE))
 

if __name__ == "__main__":
    agg_month()

