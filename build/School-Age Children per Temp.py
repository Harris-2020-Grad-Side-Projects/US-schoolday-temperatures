#School-Age Children per Temperature Region

#count of school-Age children: 2018 and 2019 ACS-5yr
#citation:
'''Steven Ruggles, Sarah Flood, Sophia Foster, Ronald Goeken, Jose Pacas, Megan Schouweiler and Matthew Sobek. IPUMS USA: Version 11.0 [dataset]. Minneapolis, MN: IPUMS, 2021. 
https://doi.org/10.18128/D010.V11.0
'''

#census boundries-need, or conty boundries needed
#CA counties from https://catalog.data.gov/dataset/tiger-line-shapefile-2016-state-california-current-county-subdivision-state-based

'''
Instead do per county
https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-detail.html 
Annual County and Resident Population Estimates by Selected Age Groups and Sex: April 1, 2010 to July 1, 2019 (CC-EST2019-AGESEX)

Let's call School-Age 5-17 (18 is in the 18-24 age range so no dice)
'''

#do spatial join to get average temp per census boudrie (or per county)
# https://towardsdatascience.com/how-to-easily-join-data-by-location-in-python-spatial-join-197490ff3544

import os
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures/Data')
#path = os.path.join(os.getcwd(), 'Data')
#links to the data: -good news, ea state is same format with statefip at end! -for CA -06.csv
CA_url = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/asrh/cc-est2019-agesex-06.csv'
filename = 'CA_pop.csv'

date = 'Jan 2019'
temp_filename = '{} temp and wind.csv'.format(date)


def build_url(statefip):
    url = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/asrh/cc-est2019-agesex-{}.csv'.format(statefip)
    return url


def download_data(url, filename):
    '''url is data location
    filename is name you choose to save as
    '''
    response = requests.get(url)
    if url.endswith('.csv'):
        open_as = 'w'
        output = response.text
    elif url.endswith('.xls'):
        open_as = 'wb'
        output = response.content
    else:
        return 'unexpected file type in download_data'
    
    with open(filename, open_as) as ofile:
        ofile.write(output)

download_data(CA_url, filename)
df = pd.read_csv(filename)


df.columns
df_age = df[['STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'YEAR', 
            'POPESTIMATE','AGE513_TOT', 'AGE1417_TOT']]
# keep just
# 11 = 7/1/2018 population estimate and 12 = 7/1/2019 population estimate
#df_age_19 = df_age[(df_age['YEAR'] == 11) | (df_age['YEAR'] == 12)]
#lets just do 19 for now
df_age_19 = df_age[df_age['YEAR'] == 12]

#add leading 0s to match county col COUNTYFP
df_age_19['COUNTY'] = df_age_19['COUNTY'].astype(str)
df_age_19['COUNTY'] = df_age_19['COUNTY'].apply(lambda x: x.zfill(3))
df_age_19['COUNTY'].head()

counties = gpd.read_file('tl_2016_06_cousub/tl_2016_06_cousub.shp')

counties.crs
# {'init': 'epsg:4269'}
counties.columns
counties['COUNTYFP'].head()

county_age = counties.merge(df_age_19, left_on = 'COUNTYFP', right_on = 'COUNTY', how = 'outer')

county_age.head()
county_age.crs

temp_df = pd.read_csv(temp_filename)
temp_gdf = gpd.GeoDataFrame(temp_df, 
                            geometry=gpd.points_from_xy(temp_df['lon'], temp_df['lat']),
                            crs = {'init': 'epsg:4269'})

sjoined = gpd.sjoin(temp_gdf, county_age, op='within')
sjoined.head()

test_grouped = sjoined.groupby('COUNTYFP').mean()
test_grouped = test_grouped[temp_df.columns[3:8]]
#test_grouped = test_grouped.drop(columns = ['Unnamed: 0', 'lat', 'lon'])
test_grouped.reset_index(inplace = True)


final_df = county_age.merge(test_grouped, on = 'COUNTYFP', how = 'outer')


#deal with missing counties!
#1)get centroid for county
#2)use point that has shortest euclydian distnace to centroid
    #scipy.spatial.distance.euclidean() -that's between arrays
    #can alsu just use math
#https://www.techtrekking.com/how-to-calculate-euclidean-and-manhattan-distance-by-using-python/
x1 = [1,1]
x2 = [2,9]
eudistance =math.sqrt(math.pow(x1[0]-x2[0],2) + math.pow(x1[1]-x2[1],2) )
print("eudistance Using math ", eudistance)

# nope, its waaaaaaay easier!
# https://stackoverflow.com/questions/63722124/get-distance-between-two-points-in-geopandas
temp_gdf['geometry'][0].distance(temp_gdf['geometry'][1])


#Alternatively: Get new temperature reagions -contorform
# get centroid of county, and do centroind within to det temperature for county

#quick check
fig, ax = plt.subplots(figsize=(8,6))
#contenental_states.plot(ax=ax, color = 'none', edgecolor='black')
final_df.plot(ax=ax, column = 'average_windchill')
sjoined.plot(ax=ax, alpha = 0.7)
plt.show()


