import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping
import  matplotlib.pyplot
from matplotlib import pyplot as plt
import keras.backend as K
from sklearn.metrics import mean_squared_error
from math import sqrt
import seaborn as sns
from ann_visualizer.visualize import ann_viz
from keras import optimizers
from keras.models import model_from_json



layers=keras.layers
# data=pd.read_csv("TrainDataWithsolarAngle.csv")
data=pd.read_csv("TrainDataWithNightsolarAngle.csv")
data['SolarRadiance'] = pd.to_numeric(data['SolarRadiance'], errors='coerce')
data['PVPower'] = pd.to_numeric(data['PVPower'], errors='coerce')

#input
data.set_index(['DATE'], inplace=True)
#condidering only day data
# data=data.loc[data['SolarRadiance']>10 ]
data=data.loc[data['PVPower']>1 ]
# print(data.head(30))
solarRadiance_Train=data[['SolarRadiance','HourlyRelativeHumidity',
                         'HourlySkyConditions','HourlyVisibility',
                         'HourlyDryBulbTemperature','sineazimuthal','cosazimuthal','sineZenith','cosZenith'
                          ,'HourlyDewPointTemperature']].values
# 'sineazimuthal','cosazimuthal','sineZenith','cosZenith'
#'SineAngle', 'CosineAngle'
#output

PVPOwer_Train=data[['PVPower']]

# print(solarRadiance_Train,"solarRadiance_Train")
#model
model=Sequential()
n_columns=solarRadiance_Train.shape[1]
#add model layers
model.add(Dense(10, activation='relu', input_shape=(n_columns,)))
model.add(Dense(20, activation='relu'))
model.add(Dense(40, activation='relu'))
model.add(Dense(1))
sgd = optimizers.adam(lr=0.001)
model.compile(loss='mean_squared_error',optimizer=sgd,metrics=['accuracy'])

# ann_viz(model, title="Solar prediction neural network")
print(model.summary())

early_stopping_monitor = EarlyStopping(patience=3)
history=model.fit(
    solarRadiance_Train, PVPOwer_Train,
    epochs=200, callbacks=[early_stopping_monitor])
# , callbacks=[early_stopping_monitor]
#saving the model
model_json = model.to_json()
with open("PredictionModel.json", "w") as json_file:
    json_file.write(model_json)
model.save_weights("PredictionModelModel.h5")
#fetching the model
# json_file = open('PredictionModel.json', 'r')
# loaded_model_json = json_file.read()
# json_file.close()
# model = model_from_json(loaded_model_json)
# model.load_weights("PredictionModelModel.h5")

#Test
# testdata = pd.read_csv("TestDataWithsolarAngle.csv")
testdata = pd.read_csv("TestDataWithNightsolarAngle.csv")
testdata['SolarRadiance'] = pd.to_numeric(testdata['SolarRadiance'], errors='coerce')
testdata['PVPower'] = pd.to_numeric(testdata['PVPower'], errors='coerce')
DateArray=pd.to_datetime(testdata['DATE']).dt.time
#considering only day data
# testdata=testdata.loc[testdata['SolarRadiance']>10 ]
testdata=testdata.loc[testdata['PVPower']>1 ]
# print(testdata.head(200))
solarRadiance_Test=testdata[['SolarRadiance','HourlyRelativeHumidity',
               'HourlySkyConditions','HourlyVisibility',
               'HourlyDryBulbTemperature','sineazimuthal','cosazimuthal','sineZenith','cosZenith'
                             ,'HourlyDewPointTemperature']].values
# ,'sineazimuthal','cosazimuthal','sineZenith','cosZenith'
PVPOwer_Test=testdata[['PVPower']].values
PVPOwer_Test=np.float64(PVPOwer_Test)
predicted = model.predict(solarRadiance_Test)
predicted=np.float64(predicted)
SSE = np.sum(np.absolute(predicted - PVPOwer_Test))
rms = sqrt(mean_squared_error(PVPOwer_Test, predicted))
print("Mean Absolute error = ", SSE/predicted.size)
print("rms = ", rms)

def myfunc(row):
    if (row > 200):
      return row

originalValuesPlot=plt.subplot(211)
# print(type(PVPOwer_Test))
# PVPOwer_Test=np.array([myfunc(row) for row in PVPOwer_Test])

originalValuesPlot.plot(PVPOwer_Test,color="blue")
originalValuesPlot.set_title("original Values")
plt.xlabel("--->Number of Hours")
plt.ylabel("--->PV Power in kW")
# predictedValues=np.array([myfunc(row) for row in predictedValues])
predictedValues=plt.subplot(212)
predictedValues.plot(predicted,color="orange")
predictedValues.set_title("predicte"
                          "dValues")
plt.xlabel("--->Number of Hours")
plt.ylabel("--->PV Power in kW")
plt.show()

plt.scatter(PVPOwer_Test,predicted,s=4)
plt.xlabel("Actual Power in kW")
plt.ylabel("Predited Power in Kw")
plt.title("Actual Vs Predicted Solar Power")
plt.show()
#58583.00632052
#
# DateArray=i for i in DateArray
print(PVPOwer_Test.size,'PVPOwer_Test',predicted.size,'predicted')
plt.plot(PVPOwer_Test,color="blue",label="Actual")
# plt.xlabel("--->Number of Hours")
plt.ylabel("PV Power in kW")
plt.xlabel("Time of the day")
plt.title("Plotting actual and predicted solar power")
plt.plot(predicted,color="orange",label="Predicted")
ax=plt.gca()
# print(DateArray,"DateArray")
data=[]
for i in predicted:
    data.append(int(i[0]))
print(type(data[0]))
# ax.set_ylim([200,1000])
# ax.set_xlim([10,50])
plt.legend(loc=1)
plt.show()

# plt.figure(figsize=(60, 60))
bins= np.linspace(0, 2000,6)
print(bins)
print(max(PVPOwer_Test.flatten()))
PVPOwer_Test = np.digitize(PVPOwer_Test, bins)
print(PVPOwer_Test.flatten())
predicted = np.digitize(predicted, bins)
data=np.zeros((len(bins),len(bins)))
print(data)
print(len(predicted))
total=0
for i in range (0,len(predicted)):
    if(data[PVPOwer_Test[i][0]-1][predicted[i][0]-1]<1000):
        data[PVPOwer_Test[i][0]-1][predicted[i][0]-1]=data[PVPOwer_Test[i][0]-1][predicted[i][0]-1]+1
        total=total+(1 if predicted[i][0]-1==PVPOwer_Test[i][0]-1 else 0)
print(total,"total")

# print(str(data.shape))
# plt.figure(figsize=(150, 150))
ax = sns.heatmap(data,cmap="coolwarm")
ax.invert_yaxis()
ax.set_yticklabels([400,800,1200,1600,2000,2400])
ax.set_xticklabels([400,800,1200,1600,2000,2400])
# xmin, xmax = plt.xlim()
# ymin, ymax = plt.ylim()
plt.xlabel("---->predicted values")
plt.ylabel("---->Actual values")
plt.savefig("test")
# 643 total--without AZcount only when equal
# 710        total--withAZcount only when equal 2901 for 6 1316 for 11