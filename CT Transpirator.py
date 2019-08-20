import pandas as pd
import numpy as np
from numpy import cumsum
#file = input('Choose the file to run through the CT Transpirator')
#df = pd.read_csv(file,header = 0)
file = 'C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\CT_Data_Aus.csv'
df = pd.read_csv('C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\CT_Data_Aus.csv')
dfr = pd.read_csv('C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\Cobran_Carrathool_2018_19_clean_weather.csv_RefET.csv')
dfet = pd.read_csv('C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\Cobran_Carrathool_2018_19_clean_weather.csvGDU.csv')

#Convert Date column to pandas datetime format
df['Date'] = pd.to_datetime(df['Date'])

#Create a DOY column
df['DOY'] = df['Date'].dt.dayofyear

#Create a time column
df['DOY_Time'] = df['Date'].dt.time

#Isolate the canopy temperature columns and create a new DataFrame
df2 = df.iloc[:,8:17]

###Force datatype on the columns to numeric as they are all numbers
df2 = df2.apply(pd.to_numeric,errors='coerce')

###Apply calculations for canopy temperature transpiration model
df2['counter'] = range(len(df2))
df2['Day_index'] = df2['counter']*(1/96)+60
df2['Net_Irradiance'] = dfr['Rn_W/m2']
#df2['Net_Irradiance'] = dfr['radn.W/m2']

###Canopy Volume in grams calculation from Hiz's Australia data
df2['Canopy_Vol_g'] = -0.0132*(df2['Day_index']**3) + 3.4792*(df2['Day_index']**2) -231.2*(df2['Day_index']) + 4456.1

###Set max value for the grams of fresh weights to 4200 max
x = list()
for idx, row in df2.iterrows():
    if row['Canopy_Vol_g']>=4200:
        row['Canopy_Vol_g'] = 4200

###Set lower end of grams of fresh weight after reaching maximum
    elif idx > 6200 and row['Canopy_Vol_g'] <= 3500:
        row['Canopy_Vol_g'] = 3500
    x.append(row['Canopy_Vol_g'])
df3 = pd.DataFrame(x)

###Set the column of Canopy Vol g to correct growth
df2['Canopy_Vol_g'] = df3[0:]
dfct = pd.DataFrame([df.columns[df.columns.to_series().str.contains('CT')]])
dfct.columns = dfct.iloc[0]
xx = list(dfct.columns)
dfct = df[xx]
dfct1 = dfct.diff()
df2['Canopy_Fraction'] = df2['Canopy_Vol_g']/df2['Canopy_Vol_g'].max()
df2['15_min_Flux_J'] = (df2['Net_Irradiance']*900)*df2['Canopy_Fraction']
df2['Joules_of_Rn_in_degC'] = (df2['15_min_Flux_J']/4.186)/df2['Canopy_Vol_g']

###Net degrees C into the system###
dfct2 = df2['Joules_of_Rn_in_degC'].values[:, None] - dfct1

###Joules missing in the system###
dfct2 = df2['Canopy_Vol_g'].values[:, None] * (dfct2*4.186)

###Grams of H2o / 15min###
dfct3 = pd.DataFrame(np.where(df2['Net_Irradiance'].values[:, None] > 0, dfct2 * (4.08*10**-4),0),columns = xx)
dfct3['DOY'] = df['DOY']

###Divide grams of H2o per day by 1000 to mm/m2/day or mm/day###
data = dfct3.groupby(['DOY']).sum() / 1000
data['Ref_ET'] = dfet['Daily Ref ET mm/h']
data.to_csv(file + 'mm_m2_day.csv')










########################################Exploratory SHIZZLE###############################################
ww = dfct*1.14
ww1 = ww.diff()

###Net degrees C into the system###
ww2 = df2['Joules_of_Rn_in_degC'].values[:, None] - ww1

###Joules missing in the system###
ww2 = df2['Canopy_Vol_g'].values[:, None] * (ww2*4.186)

###Grams of H2o / 15min###
ww3 = pd.DataFrame(np.where(df2['Net_Irradiance'].values[:, None] > 0, ww2 * (4.08*10**-4),0),columns = xx)
ww3['DOY'] = df['DOY']

###Divide grams of H2o per day by 1000 to mm/m2/day or mm/day###
wwdata = ww3.groupby(['DOY']).sum() / 1000
wwdata['Ref_ET'] = dfet['Daily Ref ET mm/h']
wwdata.to_csv(file + 'Well_Watered_Adjusted_mm_m2_day.csv')
