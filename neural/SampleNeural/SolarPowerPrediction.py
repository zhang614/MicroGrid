import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from tensorflow import keras
from pandas import datetime
import torch as t


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

data=data["2017-01-01":"2017-03-01"]
solarData=solarData["2017-01-01":"2017-03-01"]
solarPower=solarPower["2017-01-01":"2017-03-01"]

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
data2['PVPower']=solarPower.PVPower.resample('1H').mean()
interpolated=data2.interpolate(method='linear')
interpolated.to_csv("TestData.csv")
print(interpolated.head(30))


# data=data.drop(data.columns[0],axis=1)
# data=data.drop(data.columns[11],axis=1)
# data=data.drop(data.columns[11],axis=1)
# print(data)
# # data=data[pd.notnull(data['DATE'])]
# # data=data[pd.notnull(data['HourlyDewPointTemperature'])]
# # data=data[pd.notnull(data['HourlyPrecipitation'])]
# # data=data[pd.notnull(data['HourlyRelativeHumidity'])]
# # data=data[pd.notnull(data['HourlySkyConditions'])]
# # data=data[pd.notnull(data['HourlyVisibility'])]
#
# train_size=int(len(data)*0.8)
# #Train features
# # date_Train=data['Date'][:train_size]
# hour_Train=data['Hour'][:train_size]
# cloudCoverage_Train=data['Cloud coverage'][:train_size]
# visibility_Train=data['Visibility'][:train_size]
# # visibility_Train=preprocessing.normalize(visibility_Train,norm='l2')
# # print(visibility_Train,"visibility_Train")
# temperature_Train=data['Temperature'][:train_size]
# dewPoint_Train=data['Dew point'][:train_size]
# relativeHumidity_Train=data['Relative humidity'][:train_size]
#
# # Train labels
# labels_Train=data['Solar energy'][:train_size]
#
# #Test features
# # date_Test=data['Date'][train_size:]
# hour_Test=data['Hour'][train_size:]
# cloudCoverage_Test=data['Cloud coverage'][train_size:]
# visibility_Test=data['Visibility'][train_size:]
# temperature_Test=data['Temperature'][train_size:]
# dewPoint_Test=data['Dew point'][train_size:]
# relativeHumidity_Test=data['Relative humidity'][train_size:]
#
# # Test labels
# labels_Test=data['Solar energy'][train_size:]
#
# #preprosessing the inputs
#
# #building the model
# #I think this is input layer
# inputs_hour= layers.Input(shape=(1,))
# inputs_cloud=layers.Input(shape=(1,))
# inputs_visibility=layers.Input(shape=(1,))
# inputs_temperature=layers.Input(shape=(1,))
# inputs_dewpoint=layers.Input(shape=(1,))
# inputs_humidity=layers.Input(shape=(1,))
# mergedLayer=layers.concatenate([inputs_hour,inputs_cloud,inputs_visibility,inputs_temperature,inputs_dewpoint,inputs_humidity])
# mergedLayer = layers.Dense(256, activation='relu')(mergedLayer)
# predictions=layers.Dense(1)(mergedLayer)
# wide_model=keras.Model(inputs=[inputs_hour,inputs_cloud,inputs_visibility,inputs_temperature,inputs_dewpoint,inputs_humidity],outputs=predictions)
# wide_model.compile(loss='mse',optimizer='adam',metrics=['accuracy'])
# print(wide_model.summary())
# print(inputs_hour,"Atleast no compile error")
# #47824
#
#
# #build model regression model
# #convert 2 to 3
# #skycoverage
# #check about normalization
