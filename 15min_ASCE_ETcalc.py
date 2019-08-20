import numpy as np
import pandas as pd
import math

#file = input('Choose a csv weather file with wind/RH/AirTemp/IncShortWaveRad:')
file = 'C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\Cobran_Carrathool_2018_19_clean_weather.csv'
df = pd.read_csv(file, header=0)

# Altitude for Lubbock Texas in meters #
altitude = float(992.4)

# Assumed Albedo #
albedo = float(0.23)

# Stefan Boltzman Constant
sbc = 2.042 * (10**-10)

# Latent heat of vaporization (MJ/kg)
lhv = 2.45

# Atmosperic pressure (kPa)
df['Atmosperic_Pressure'] = 101.3*((293-0.0065*altitude)/293)**5.26

# Psychometric Constant (kPA/C)
df['Psychometric_Constant'] = 0.000665*df['Atmosperic_Pressure']

# Air temperature in C
df['Tair_C'] = df['avgt.C']

# Air Temperature in K
df['Tair_K'] = df['Tair_C'] + 273.2

# Slope (svp vs air temp)(kPa/C)
df['Slope'] = (2503 * np.exp(17.27*df['Tair_C']/(df['Tair_C']+237.3))/(df['Tair_C']+237.3)**2)

# Saturated Vapor Pressure (kPa)
df['Saturated_Vapor_Pressure'] = 0.61078*np.exp((17.269*df['Tair_C'])/(237.3+df['Tair_C']))

# Actual Vapor Pressure (kPa)
df['Actual_Vapor_Pressure'] = (df['RH.2m.%']/100)*df['Saturated_Vapor_Pressure']

# Vapor Pressure Deficit (kPa)
df['Vapor_pressure_deficit'] = df['Saturated_Vapor_Pressure']-df['Actual_Vapor_Pressure']

# Net Shortwave Irradiance (W/m2)
df['Net_Shortwave_Irradiance'] = (1-albedo)*df['radn.W/m2']

# Net Shortwave Irradiance (MJ/(m2*h))
df['Net_Shortwave_Irradiance_MJ'] = df['Net_Shortwave_Irradiance']*(900/1000000)

# Net Outgoing Long Wave Irradiance (MJ/(m2*h))
df['Net Outgoing Long Wave Irradiance (MJ/(m2*h))'] = 0.8*sbc*(0.34-0.14*np.sqrt(df['Actual_Vapor_Pressure']))*df['Tair_K']**4

# Net Outgoing Long Wave Irradiance (W/m2)
df['Net Outgoing Long Wave Irradiance (W/m2)'] = (df['Net Outgoing Long Wave Irradiance (MJ/(m2*h))']/900)*1000000

# Net Irradiance in (W/m2) Rn
df['Rn_W/m2'] = df['Net_Shortwave_Irradiance'] - df['Net Outgoing Long Wave Irradiance (W/m2)']

# Net Irradiance in (MJ/(m2*h)) Rn
df['Rn_(MJ/(m2*h))'] = df['Net_Shortwave_Irradiance_MJ'] - df['Net Outgoing Long Wave Irradiance (MJ/(m2*h))']

# Soil Heat Flux Density (W/m2)
df['Soil Heat Flux Density (W/m2)'] = 0.5 * df['Rn_W/m2']

# Soil Heat Flux Density (MJ/(m2*h))
df['Soil Heat Flux Density (MJ/(m2*h))'] = df['Soil Heat Flux Density (W/m2)']*(900/1000000)

# numerator constant for hourly
# df['Numerator Constant'] = 37
# ##numerator constant for 15-min###
df['Numerator Constant'] = 9.25
# #### Numerator constant for Daily Data #####
# df['Numerator Constant'] = 900

# Denominator Constant 0.96 for night and 0.24 for day for hourly rates
# df['Denominator Constant'] = np.where(df['radn.W/m2'] >0, 0.24, 0.96)
# ##Denominator Constant 0.24 for night and 0.06 for day for 15-min rates###
df['Denominator Constant'] = np.where(df['radn.W/m2'] >0, 0.24, 0.96)

# #### Denominator Constant 0.34 constant for Daily Data #####
# df['Denominator Constant'] = 0.34

# Reference ET Calculations mm/h (short crop)
df['Reference ET mm/h'] = (0.408 * df['Slope'] * (df['Rn_(MJ/(m2*h))'] - df['Soil Heat Flux Density (MJ/(m2*h))']) + df['Psychometric_Constant'] * (df['Numerator Constant'] / (df['Tair_C'] + 273)) * df['meanU.2m.m/s'] * df['Vapor_pressure_deficit'])\
                          / ( df['Slope'] + df['Psychometric_Constant'] * ( 1 + (df['Denominator Constant'] * df['meanU.2m.m/s'])))

# Reference ET Calculations MJ/(m2*h) (short crop)
df['Reference ET (MJ/(m2*h))'] = df['Reference ET mm/h']*2.45

# Sensible Heat
df['Sensible Heat (MJ/(m2*h))'] = (df['Soil Heat Flux Density (MJ/(m2*h))']+df['Rn_(MJ/(m2*h))'])-df['Reference ET (MJ/(m2*h))']

# Energy Balance
df['Energy Balance'] = df['Soil Heat Flux Density (MJ/(m2*h))'] + df['Rn_(MJ/(m2*h))'] - df['Reference ET (MJ/(m2*h))'] - df['Sensible Heat (MJ/(m2*h))']
print(df[60:70])

# df2 = df[['DOY','TimeNo24','year','Rn_W/m2','Rn_(MJ/(m2*h))','Reference ET mm/h','Reference ET (MJ/(m2*h))']].copy()
df2 = df[['DOY','year','Rn_W/m2','Rn_(MJ/(m2*h))','Reference ET mm/h','Reference ET (MJ/(m2*h))']].copy()


data = ((df.groupby(['DOY'])['avgt.C'].mean())) - 15.5 if df['year'][1] >= 2016 else ((df.groupby(['DOY'])['maxt.C'].max() + df.groupby(['DOY'])['mint.C'].min()) / 2) - 15.5


df3 = pd.DataFrame(data=list(data),columns= ['GDU_calc'])
df3['GDU_calc'] = np.where(df3['GDU_calc'] < 0, 0, df3['GDU_calc'])
df3['DOY'] = range(1, len(df3)+1)
df['Filter_Ref'] = np.where(df['Reference ET mm/h'] < 0, 0, df['Reference ET mm/h'])
df3['Daily Ref ET mm/h'] = df.groupby(['DOY'])['Filter_Ref'].sum()

# df3['Daily Ref ET mm/h Sum'] = df.groupby(['DOY'])['Filter_Ref'].sum()
# df3['Daily Ref ET mm/day'] = df3['Daily Ref ET mm/h'] * 96

df.to_csv(file + '_RefET.csv')
df2.to_csv(file + 'Rn_RefET.csv')
df3.to_csv(file + 'GDU.csv')