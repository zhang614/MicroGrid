from keras.models import model_from_json

import numpy
import matplotlib.pyplot as plt
from pandas import read_csv
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import seaborn as sns
# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=3):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return numpy.array(dataX), numpy.array(dataY)
# fix random seed for reproducibility
numpy.random.seed(7)
# load the dataset
dataframe = read_csv('Load_dailyhours_average.csv', usecols=[4], engine='python')
dataset = dataframe.values
dataset = dataset.astype('float32')
# normalize the dataset
scaler = MinMaxScaler(feature_range=(0, 1))
dataset = scaler.fit_transform(dataset)
# split into train and test sets
train_size = int(len(dataset) * 0.67)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
# reshape into X=t and Y=t+1
look_back = 1
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)
# reshape input to be [samples, time steps, features]
trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))


json_file = open('C:\Prediction3\.idea\model_average_week_3.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("C:\Prediction3\.idea\model_average_week_3.h5")

trainPredict = loaded_model.predict(trainX)
testPredict = loaded_model.predict(testX)
# invert predictions
#print(trainPredict)
trainPredict = scaler.inverse_transform(trainPredict)
trainY = scaler.inverse_transform([trainY])
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform([testY])
# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))
# shift train predictions for plotting
trainPredictPlot = numpy.empty_like(dataset)
trainPredictPlot[:, :] = numpy.nan
trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict
# shift test predictions for plotting
testPredictPlot = numpy.empty_like(dataset)
testPredictPlot[:, :] = numpy.nan
testPredictPlot[len(trainPredict)+(look_back*2)+1:len(dataset)-1, :] = testPredict

predicted_values = trainPredictPlot
for i in range(0,len(predicted_values)):
    predicted_values[i]=trainPredictPlot[i]
    if numpy.isnan(trainPredictPlot[i]):
        predicted_values[i]=testPredictPlot[i]
for i in range(0,len(predicted_values)):
    print(predicted_values[i])

bins= numpy.linspace(-10, 10, 20)
data = numpy.digitize(scaler.inverse_transform(dataset), bins)
predicted = numpy.digitize(predicted_values, bins)
data_2=numpy.zeros((len(bins)+1,len(bins)+1))
for i in range (0,len(predicted)):
    data_2[data[i][0]][predicted[i][0]]=data_2[data[i][0]][predicted[i][0]]+1

ax = sns.heatmap(data_2,cmap="coolwarm",xticklabels=True, yticklabels=True)
ax.invert_yaxis()
plt.title("Heatmap showing actual vs Predicted values on Hourly sampled data")
plt.xlabel("---->predicted values(1 unit = 2 Kilowatts)")
plt.ylabel("---->Actual values (1 unit = 2 Kilowatts)")
plt.show()





