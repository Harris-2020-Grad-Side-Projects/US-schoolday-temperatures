#Test metpy
import metpy.calc 
from metpy.units import units
import os
import pandas as pd


os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures/Data')

df = pd.read_csv('20-12-28.csv')
index = 15000

df['windchill'] = ''
for index in range(len(df)):
    temp = [df['temperature_(F)'][index]]*units.degF
    wind = [df['wind_speed_(mph)'][index]]*units.mph


    df['windchill'][index] = metpy.calc.windchill(temp, wind,
                        face_level_winds = False,
                        mask_undefined = True)



print('windchil', df['with_windchill_(F)'][index],
        'temp', df['temperature_(F)'][index],
        'wind', df['wind_speed_(mph)'][index])



