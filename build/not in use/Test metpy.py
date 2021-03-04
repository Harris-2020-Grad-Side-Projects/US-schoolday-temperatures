#Test metpy
# https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.html
import metpy.calc 
from metpy.units import units
import os
import pandas as pd



os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures/Data')

df = pd.read_csv('one_day.csv')



df['windchill'] = ''
for index in range(len(df)):
    temp = [df['2mtemperature_(F)'][index]]*units.degF
    wind = [df['wind_speed_(mph)'][index]]*units.mph


    df['windchill'][index] = metpy.calc.windchill(temp, wind,
                        face_level_winds = False,
                        mask_undefined = True).magnitude[0]

df.to_csv('test.csv')

index = 15000
temp = [df['2mtemperature_(F)'][index]]*units.degF
wind = [df['wind_speed_(mph)'][index]]*units.mph
Dtemp = [df['T2MDEW'][index]]*units.K

RH = metpy.calc.relative_humidity_from_dewpoint(temp, Dtemp)

metpy.calc.apparent_temperature(temp, RH, wind)

x = metpy.calc.windchill(temp, wind,
                        face_level_winds = False,
                        mask_undefined = True)
x.magnitude[0]
print('windchil', df['with_windchill_(F)'][index],
        'temp', df['temperature_(F)'][index],
        'wind', df['wind_speed_(mph)'][index])



