#School-Age Children per Temperature Region

#count of school-Age children: 2018 and 2019 ACS-5yr
#citation:
'''Steven Ruggles, Sarah Flood, Sophia Foster, Ronald Goeken, Jose Pacas, Megan Schouweiler and Matthew Sobek. IPUMS USA: Version 11.0 [dataset]. Minneapolis, MN: IPUMS, 2021. 
https://doi.org/10.18128/D010.V11.0
'''

#census boundries-need

#do spatial join to get average temp per census boudrie
# https://towardsdatascience.com/how-to-easily-join-data-by-location-in-python-spatial-join-197490ff3544

import pandas as pd
import os
import geopandas as gpd

os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures/Data')

data = open('usa_00005.dat', 'r')
data3 = data.read()

#data2 = pd.read_csv('usa_00005.dat')
#Need to do in R
'''
if (!require("ipumsr")) stop("Reading IPUMS data into R requires the ipumsr package. It can be installed using the following command: install.packages('ipumsr')")

ddi <- read_ipums_ddi("usa_00005.xml")
data <- read_ipums_micro(ddi)
'''