#School-Age Children per Temperature Region

#count of school-Age children: 2018 and 2019 ACS-5yr
#citation:
'''Steven Ruggles, Sarah Flood, Sophia Foster, Ronald Goeken, Jose Pacas, Megan Schouweiler and Matthew Sobek. IPUMS USA: Version 11.0 [dataset]. Minneapolis, MN: IPUMS, 2021. 
https://doi.org/10.18128/D010.V11.0
'''

#census boundries-need, or conty boundries needed

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

os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures')
path = os.path.join(os.getcwd(), 'Data')
#links to the data: -good news, ea state is same format with statefip at end! -for CA -06.csv
CA_url = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/asrh/cc-est2019-agesex-06.csv'

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

def read_data(path, filename):
    if filename.endswith('.csv'):
        df = pd.read_csv(os.path.join(path, filename))
    elif filename.endswith('.xls'):
        df = pd.read_excel(os.path.join(path, filename))
    else:
        return 'unexpected file type in read_data'
    return df
