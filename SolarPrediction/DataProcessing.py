import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from tensorflow import keras
from pandas import datetime
from astral import Astral
# import astral as ap
# import torch as t

astral =  Astral()
Latitude=41.7354862
Longitude=-111.834388
def GetSineAzimutalAngle(date):
    return np.sin(astral.solar_azimuth(dateandtime=date,latitude=Latitude,longitude=Longitude))
def GetCosAzimutalAngle(date):
    return np.cos(astral.solar_azimuth(dateandtime=date,latitude=Latitude,longitude=Longitude))
def GetSineZenithAngle(date):
    return np.sin(astral.solar_zenith(dateandtime=date,latitude=Latitude,longitude=Longitude))
def GetCosZenithAngle(date):
    return np.cos(astral.solar_zenith(dateandtime=date,latitude=Latitude,longitude=Longitude))

layers = keras.layers
# reading the file
data = pd.read_csv("Dataset2.csv", parse_dates=["DATE"])
solarData=pd.read_csv("SolarRadiance.csv",parse_dates=["Date"])
solarPower=pd.read_csv("SolarPower.csv",parse_dates=["Date"])

# print(solarPower.dtypes)
solarPower['Date']=pd.to_datetime(solarPower['Date'], format='%m/%d/%Y  %H:%M', errors='coerce')

#setting index for interpolation
solarData.set_index(['Date'],inplace=True)
data.set_index(['DATE'], inplace=True)
solarPower.set_index(['Date'],inplace=True)
# print(solarPower.dtypes)
# print(solarPower.head(30).index.tolist())
# print(data.head(30).index.tolist())
# print(solarData.head(30).index.tolist())

#Train Data
# data=data["2015-01-01":"2017-01-01"]
# solarData=solarData["2015-01-01":"2017-01-01"]
# solarPower=solarPower["2015-01-01":"2017-01-01"]

#TestData
data=data["2018-01-01":"2018-12-30"]
solarData=solarData["2018-01-01":"2018-12-30"]
solarPower=solarPower["2018-01-01":"2018-12-30"]

#Droping unneccesary columns
solarData=solarData.drop(["Ignore"],axis=1)
solarData=solarData.drop(["Final"],axis=1)
solarPower=solarPower.drop([" Home_av_pw 2"],axis=1)
data = data.dropna(thresh=4)
mapping={'CLR':0,'FEW':0.1875,'SCT':0.4375,'BKN':0.75,'OVC':1,'VV001':1}
data['HourlySkyConditions']=data['HourlySkyConditions'].str.rpartition(':',expand=False).str[0]
data['HourlySkyConditions']=data['HourlySkyConditions'].str.rpartition(' ',expand=False).str[-1]
data=data.replace({'HourlySkyConditions':mapping})
# print(data.head(10))

#converting the columns into float
data['HourlySkyConditions']=pd.to_numeric(data['HourlySkyConditions'],errors='coerce')
data['HourlyDewPointTemperature']=pd.to_numeric(data['HourlyDewPointTemperature'],errors='coerce')
data['HourlyPrecipitation']=pd.to_numeric(data['HourlyPrecipitation'],errors='coerce')
data['HourlyVisibility']=pd.to_numeric(data['HourlyVisibility'],errors='coerce')
data['HourlyDryBulbTemperature']=pd.to_numeric(data['HourlyDryBulbTemperature'],errors='coerce')
data['HourlyWindSpeed']=pd.to_numeric(data['HourlyWindSpeed'],errors='coerce')
data['HourlyAltimeterSetting']=pd.to_numeric(data['HourlyAltimeterSetting'],errors='coerce')
# data['Month']=pd.DatetimeIndex(pd['Date']).month
solarData['SolarRadiance']=pd.to_numeric(solarData['SolarRadiance'],errors='coerce')
solarPower['PVPower']=pd.to_numeric(solarPower['PVPower'],errors='coerce')



# print(solarData.dtypes)
# print(data.dtypes)
data2=pd.DataFrame()
data2['HourlyRelativeHumidity']=data.HourlyRelativeHumidity.resample('1H').mean()
data2['HourlyVisibility']=data.HourlyVisibility.resample('1H').mean()
data2['HourlyDewPointTemperature']=data.HourlyDewPointTemperature.resample('1H').mean()
data2['HourlyDryBulbTemperature']=data.HourlyDryBulbTemperature.resample('1H').mean()
data2['HourlyWetBulbTemperature']=data.HourlyWetBulbTemperature.resample('1H').mean()
data2['SolarRadiance']=solarData.SolarRadiance.resample('1H').mean()
data2['HourlySkyConditions']=data.HourlySkyConditions.resample('1H').mean()
data2['HourlyWindSpeed']=data.HourlyWindSpeed.resample('1H').mean()
data2['HourlyAltimeterSetting']=data.HourlyAltimeterSetting.resample('1H').mean()
data2['PVPower']=solarPower.PVPower.resample('1H').mean()
data2=data2.interpolate(method='linear')
print(data2.head(30))
# data['DATE']=pd.to_datetime(data['DATE'], format='%m/%d/%Y  %H:%M', errors='coerce')
data2['Date']=data2.index
data2['sineazimuthal']=data2['Date'].apply(GetSineAzimutalAngle)
data2['cosazimuthal']=data2['Date'].apply(GetCosAzimutalAngle)
data2['sineZenith']=data2['Date'].apply(GetSineZenithAngle)
data2['cosZenith']=data2['Date'].apply(GetCosZenithAngle)
data2=data2.loc[data2['PVPower']!='NaN' ]
# data2=data2.loc[data2['PVPower']>0 ]
# print(data)
# data2['Month']=pd.DatetimeIndex(data2.index).month
# data2.loc[data2['Month'] == 12, 'PoleAngle'] = 24
# data2.loc[((data2['Month'] == 1)|(data2['Month'] == 11)), 'PoleAngle'] = 32
# data2.loc[((data2['Month'] == 2)|(data2['Month'] == 10)), 'PoleAngle'] = 40
# data2.loc[((data2['Month'] == 3)|(data2['Month'] == 9)), 'PoleAngle'] = 48
# data2.loc[((data2['Month'] == 4)|(data2['Month'] == 8)), 'PoleAngle'] = 56
# data2.loc[((data2['Month'] == 5)|(data2['Month'] == 7)), 'PoleAngle'] = 64
# data2.loc[data2['Month'] == 6, 'PoleAngle'] = 72
# data2['SineAngle']=data2.eval('sin(PoleAngle)')
# data2['CosineAngle']=data2.eval('cos(PoleAngle)')
data2.to_csv("TrainDataWithNightsolarAngle3.csv")
#TrainDataWithPoleAngle


