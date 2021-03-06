#Test metpy
# https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.html
import metpy.calc 
from metpy.units import units
import os
import pandas as pd
import numpy as np



os.chdir('/Users/Sarah/Documents/GitHub/US-schoolday-temperatures/Data')

df = pd.read_csv('one_day.csv')



df['windchill_(F)'] = np.where(
                                (df['2mtemperature_(F)'] <= 50) & (df['wind_speed_(mph)'] >= 3), 
                                    (metpy.calc.windchill([df['2mtemperature_(F)']]*units.degF,
                                    [df['wind_speed_(mph)']]*units.mph).magnitude[0]),
                                    df['2mtemperature_(F)'])


def relative_humidity(temp, dewpt):
    return metpy.calc.relative_humidity_from_dewpoint(
                            [temp]*units.K,
                            [dewpt]*units.K).magnitude[0]

# works but .apply might be better???
# https://www.geeksforgeeks.org/python-pass-multiple-arguments-to-map-function/
df['Relative_Humidity'] = list(map(relative_humidity, df['T2M'],df['T2MDEW']))

 # add heat index
# heat index only if 80F or higher
df['with_heatindex_(F)'] = np.where(
                                    (df['2mtemperature_(F)'] >= 80), 
                                        (metpy.calc.heat_index([df['2mtemperature_(F)']]*units.degF,
                                        [df['Relative_Humidity']]*units.dimensionless).magnitude[0]), 
                                        df['2mtemperature_(F)'])

df.to_csv('test.csv')

for i in [1,2,3]:
    print(metpy.calc.heat_index([df['2mtemperature_(F)'][i]]*units.degF,
                                    [df['Relative_Humidity'][i]]*units.dimensionless).magnitude[0])

metpy.calc.heat_index([81]*units.degF,
                                    0.07)
#
K = df['T2MDEW'][38851]
(K - 273.15)*1.8000 + 32.00

relative_humidity(df['T2M'][38851],df['T2MDEW'][38851])
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



