import torch
from torch.autograd import Variable
from torch import nn
import pandas as pd
import tensorflow as tf
import torch.nn.functional as F
import os

data = pd.read_csv("FinalData2.csv")
data['HourlyDewPointTemperature'] = pd.to_numeric(data['HourlyDewPointTemperature'], errors='coerce')
data['HourlyVisibility'] = pd.to_numeric(data['HourlyVisibility'], errors='coerce')
data['HourlyDryBulbTemperature'] = pd.to_numeric(data['HourlyDryBulbTemperature'], errors='coerce')
data['SolarRadiance'] = pd.to_numeric(data['SolarRadiance'], errors='coerce')
data['PVPower'] = pd.to_numeric(data['PVPower'], errors='coerce')
# features = ['HourlyDewPointTemperature', 'HourlyVisibility', 'HourlyRelativeHumidity', 'HourlyDryBulbTemperature',
#             'HourlyWetBulbTemperature', 'SolarRadiance']
features = ['SolarRadiance']
# features=['HourlyDewPointTemperature','HourlyVisibility','HourlyRelativeHumidity','HourlyDryBulbTemperature','HourlyWetBulbTemperature']
input_tensor = torch.tensor(data[features].values).view(-1, 1)
output_tensor = torch.tensor(data["PVPower"].values).view(-1, 1)
output_tensor = torch.tensor(data["PVPower"].values).view(-1, 1)


# output_tensor=torch.tensor(data["SolarRadiance"].values)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.hiddenLayer = nn.Linear(1, 10)
        # self.deepLayer1 = nn.Linear(10, 80)
        self.predict = nn.Linear(10, 1)

    def forward(self, x):
        print(x.size())
        x = F.relu(self.hiddenLayer(x))
        # x = F.relu(self.deepLayer1(x))
        x = self.predict(x)
        return x

# instantiate model
model = Net()
optimizer = torch.optim.SGD(params=model.parameters(), lr=0.01, weight_decay=0.1)
criterion = nn.MSELoss()

model_filename = 'model'
if os.path.exists(model_filename):
    model.load_state_dict(torch.load(f=model_filename))

model = model.double()
print(model)

# import numpy as np
#
# print(input_tensor.shape)
# print(output_tensor.shape)
# input_tensor = input_tensor.numpy().ravel()
# output_tensor= output_tensor.numpy().ravel()
# coffs = np.polyfit(input_tensor, output_tensor, 3)
# print(coffs)
#
# error = np.sum((output_tensor - (np.dot(np.vander(input_tensor, 4), coffs)))**2)
# print(error)
#

# training
epoches = 200
previousloss=0
currentloss=1
while(currentloss-previousloss>0.1):
 previousloss=currentloss
 for epoch in range(epoches):
    inputs = input_tensor
    labels = output_tensor

    print(inputs.size(), labels.size())
    optimizer.zero_grad()
    output = model(inputs)
    loss = criterion(output, labels)
    loss.backward()
    optimizer.step()
    currentloss=loss
    print("Epoch : {}/{}\tLoss : {}".format(epoch, epoches, "%.2f" % loss))

    if epoch % 5 == 0:
        torch.save(model.state_dict(), model_filename)

        #Testing
        print("\n\n")
        with torch.no_grad():
            data = pd.read_csv("TestData.csv",nrows=80)
            data['HourlyDewPointTemperature'] = pd.to_numeric(data['HourlyDewPointTemperature'], errors='coerce')
            data['HourlyVisibility'] = pd.to_numeric(data['HourlyVisibility'], errors='coerce')
            data['HourlyDryBulbTemperature'] = pd.to_numeric(data['HourlyDryBulbTemperature'], errors='coerce')
            data['SolarRadiance'] = pd.to_numeric(data['SolarRadiance'], errors='coerce')
            data['PVPower'] = pd.to_numeric(data['PVPower'], errors='coerce')
            # features = ['HourlyDewPointTemperature', 'HourlyVisibility', 'HourlyRelativeHumidity', 'HourlyDryBulbTemperature',
            #             'HourlyWetBulbTemperature', 'SolarRadiance']
            features = ['SolarRadiance']
            # features=['HourlyDewPointTemperature','HourlyVisibility','HourlyRelativeHumidity','HourlyDryBulbTemperature','HourlyWetBulbTemperature']
            input_tensor = torch.tensor(data[features].values )
            output_tensor = torch.tensor(data["PVPower"].values)

            outputs = model(input_tensor)
            loss = criterion(outputs, output_tensor)
            print("Loss : ", loss)
            for  o, l in zip( outputs, output_tensor):
                print( "%.3f" % l.data.numpy(), "%.3f" % o.data.numpy())