import pandas as pd
import numpy as np
from numpy import cumsum
#file = input('Choose the file to run through the CT Transpirator')
#df = pd.read_csv(file,header = 0)
file = 'C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\Australia_CT_15min_unfiltered.csv'
df = pd.read_csv('C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\Australia_CT_15min_unfiltered.csv')
# dfr = pd.read_csv('C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\Cobran_Carrathool_2018_19_clean_weather.csv_RefET.csv')
# dfet = pd.read_csv('C:\\Users\\Andrew\\Desktop\\Australia 2019 CT Transpirator data\\Cobran_Carrathool_2018_19_clean_weather.csvGDU.csv')


#Convert Date column to pandas datetime format
df['Date'] = pd.to_datetime(df['Date'])

#Create a DOY column
df['DOY'] = df['Date'].dt.dayofyear

#Create a time column
df['DOY_Time'] = df['Date'].dt.time

#Create Date Time from Data
df2 = pd.DataFrame()
df2['Date_Time'] = pd.date_range(start = min(df['Date']), end = max(df['Date']), freq = '15min')
df['Date_Time'] = df2['Date_Time']
print(df['Date_Time'])
