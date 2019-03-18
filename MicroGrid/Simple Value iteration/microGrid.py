
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from data import * #import problem description
from visualize import *

#for each time period back from the future
def computeValueFuction():
    ValueArray = np.zeros((MaxEnergy+1, MaxTime+1))
    PolicyArray = np.zeros((MaxEnergy+1, MaxTime+1))
    # reward at MaxTime is sell energy
    for e in range(0, MaxEnergy+1):
        ValueArray[e, MaxTime] = e*oneDaySell[MaxTime] 
    # work backwards in time to now (t=0)
    for t in range(MaxTime-1, -1, -1):
        #afor all energy states at time t
        for e_0 in range(0, MaxEnergy+1):
            values = np.array(MaxEnergy+1)
            # consider all possible next states at time t+1
            for e_1 in range(0, MaxEnergy+1):
                values[e_1] = reward(e_0, e_1, t) + ValueArray[e_1, t+1]
            # maximize value
            ValueArray[e_0, t] = max(values)
            # delta E optimal target
            PolicyArray[e_0, t] = values.index(ValueArray[e_0, t])
    return (ValueArray, PolicyArray)
            
def reward(e_0, e_1, t):
    # for changing energy at t to the energy at t+1
    deltaE = e_1 - e_0 # in battery is +, out is -
    # net demand - own solar energy this time period
    demand = demandProfile[t] + oneDaySolar[t]
    if deltaE - demand < 0: #discharge
        #cover demand and sell 
        thisReward = sell[t] * (abs(deltaE) + demand) 
    elif -1*demand <= deltaE and deltaE <= 0: #discharge
        #cover some of the demand, buy the rest
        thisReward = buy[t] * (abs(deltaE) + demand) 
    else: # charge
        # just buy to cover and store
        thisReward = buy[t] * (abs(deltaE) - demand)
    # pay the cost of battery stress (higher charge/discharge rate, higher cost)
    thisReward = thisReward - abs(deltaE)*0.01
    return thisReward
        
(ValueArray, PolicyArray) = computeValueFuction()