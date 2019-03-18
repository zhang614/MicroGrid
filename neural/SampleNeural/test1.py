import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch
import numpy as np

learning_rate = 0.001
num_epochs = 2901
weight_decay = 0.2  # L2 regularization parameter

# If you have the option of GPU and CPU, else no use
device = ('cuda:0' if torch.cuda.is_available() else 'cpu:0')


def generate_data(N, sigma):
    """ Generate data with given number of points N and sigma """
    noise = np.random.normal(0, sigma, N)
    X = np.random.uniform(0, 3, N)

    # More work required to make it work on this. Works decently.
    Y = X ** 2 + 1 + noise # Compute y from x

    # Works better on this
    # Y = X * 2 + 1 + noise  # Compute y from x

    return X, Y


class RegNet(nn.Module):
    def __init__(self):
        super(RegNet, self).__init__()
        self.fc1 = nn.Linear(1, 30)
        self.fc2 = nn.Linear(30, 1)

    def forward(self, x):
        """ Feed forward the input """
        x = x.view(-1, 1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# Instantiate the model, define optimizer and MSE loss
model = RegNet()
optimizer = optim.SGD(params=model.parameters(), lr=learning_rate, weight_decay=weight_decay)
criterion = nn.MSELoss()

for epoch in range(num_epochs):
    inputs, labels = generate_data(N=1, sigma=0)
    inputs = torch.tensor(inputs).reshape(-1, 1).float()
    labels = torch.tensor(labels).reshape(-1, 1).float()
    outputs = model(inputs)

    model.zero_grad()
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()

    if epoch % 400 == 0:
        print("Epoch : {}/{}\tLoss : {}".format(epoch, num_epochs, "%.2f" % loss))

# Testing the accuracy of the model
with torch.no_grad():
    inputs, labels = generate_data(N=100, sigma=0)
    inputs = torch.tensor(inputs).float()
    labels = torch.tensor(labels).float()
    print(inputs.size(), labels.size())

    outputs = model(inputs)

    loss = criterion(outputs, labels)

    print("Loss : ", loss)
    for i, o, l in zip(inputs, outputs, labels):
        print("%.2f" % i.data.numpy(), "%.3f" % l.data.numpy(), "%.3f" % o.data.numpy())