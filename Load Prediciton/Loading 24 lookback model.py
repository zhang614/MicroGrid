from keras.models import model_from_json

# LSTM for international airline passengers problem with regression framing
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
def create_dataset(dataset, look_back=24):
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
look_back = 24
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)
# reshape input to be [samples, time steps, features]
trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
print(trainX)


json_file = open('C:\Prediction3\.idea\model_average_week_withlookback_24.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("C:\Prediction3\.idea\model_average_week_withlookback_24.h5")

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
#plot baseline and predictions

# plt.title('Prediction comparison')
# plt.ylabel('Power In Watts')
# ids = [x for x in range(len(scaler.inverse_transform(dataset)))]
# plt.scatter(ids,scaler.inverse_transform(dataset),s=3)
# plt.xlabel("Time in hours")
# ids2 = [x for x in range(len(trainPredictPlot))]
# ids3 = [x+ids[-1] for x in range(len(testPredictPlot))]
# plt.scatter(ids2,trainPredictPlot,s=3)
# plt.scatter(ids2,testPredictPlot,s=3)
# plt.legend([scaler.inverse_transform(dataset),trainPredictPlot,testPredictPlot],
#            ['Actual Values', 'Training Predicted Values', 'Test Predicted Values'],
#            scatterpoints=1,
#            loc=1,
#            ncol=3,
#            fontsize=8)
# plt.show()

#predictedvalues =numpy.nan

#for x in trainPredictPlot:
#    if (x == "nan"):
#        print("nothing")
#    else:
#        predictedvalues.append(x)
#
#for x in testPredictPlot:
#    if (x == "nan"):
#        print("nothing")
#    else:
#        predictedvalues.append(x)

#for x in trainPredictPlot:
#    predictedvalues.append(x)
#
#print(predictedvalues)
#

plt.title("Hourly Sampled Data Prediction with Weekdays as an input feature")
#plt.title('Actual vs Predicited')
plt.ylabel('Predcited')
plt.xlabel("Actual")
plt.scatter(scaler.inverse_transform(dataset),trainPredictPlot, label = "Train", s=4)
plt.scatter(scaler.inverse_transform(dataset),testPredictPlot , label = "Test", s=4)
plt.show()

# print heatmap

# bins= numpy.linspace(-10, 10, 21)
# print(bins)
# data = numpy.digitize(scaler.inverse_transform(dataset), bins)
# print(data,"actual")
# predicted = numpy.digitize(testPredictPlot, bins)
# print(predicted,"predicted")
# data_2=numpy.zeros((len(bins)+1,len(bins)+1))
# #print(data_2)
# print(data[0][0],"predicted[i].value")
# for i in range (0,len(predicted)):
#     data_2[data[i][0]][predicted[i][0]]=data_2[data[i][0]][predicted[i][0]]+1
#
# print(data_2)
#
# # print(str(data.shape))
# # plt.figure(figsize=(150, 150))
# ax = sns.heatmap(data_2,cmap="YlGnBu",xticklabels=True, yticklabels=True,linewidth=0.5)
# # ax.set_yticklabels(bins)
# # ax.set_xticklabels(bins)
# # xmin, xmax = plt.xlim()
# # ymin, ymax = plt.ylim()
# plt.xlabel("---->predicted values")
#
# plt.ylabel("---->Actual values")
# #plt.show()
# #plt.savefig("with night ")





