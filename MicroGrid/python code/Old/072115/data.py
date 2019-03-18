import numpy as np
import math
import random as rn
from collections import namedtuple
from loads import *


batteryVoltage = 120

def calculateSupply(unitsPerDay, maxPower):
    mid = unitsPerDay/2
    width = 14*unitsPerDay/24
    supply = [0 for col in range(unitsPerDay+1)]
    for i in range(0, +width):
        supply[i+mid-width/2] = math.floor(maxPower*math.sin((1.0*i/width)*3.1415))
    return supply

#print(calculateSupply(240,100))


def calculateDemand(unitsPerDay):
    home = [lightsEarly,fridge, coffeeMaker, lightsLate]
    eachLoad = map(lambda appliance: demand(appliance, unitsPerDay), home)
    return [sum(x) for x in zip(*eachLoad)]


def demand(appliance, unitsPerDay):
    #returns a list of demands over time
    if type(appliance) is type(periodic): #periodic
        separation = appliance.wavelength*unitsPerDay/24/60
        duration = appliance.duration*unitsPerDay/24/60
        power = appliance.power
        return makePeriodic(unitsPerDay, separation, duration, power)
    if type(appliance) is type(intermitent): #intermitent
        startIndex = appliance.start*unitsPerDay/24 #hour of the day
        endIndex = appliance.end*unitsPerDay/24
        period = (endIndex-startIndex)
        power = appliance.power
        duration = appliance.duration
        howMany = appliance.frequency*period*24/unitsPerDay #per hour
        return makeIntermitent(unitsPerDay, startIndex, period, howMany, duration, power)

def makeIntermitent(unitsPerDay, startIndex, period, howMany, duration, power):
    demand = [0 for col in range(unitsPerDay)]
    for count in range(0,howMany+1):
        start = rn.randint(0,period)
        width = duration + rn.randint(-1*duration/2, duration/2)
        for i in range(0,width):
            index = start+i
            if index < unitsPerDay:
               demand[startIndex+index]+= power
    return demand
        
def makePeriodic(unitsPerDay, separation, duration, power):
    demand = [0 for col in range(unitsPerDay)]
    for i in range(0, unitsPerDay/separation):
        for width in range(0,duration+1):
            index = i+separation*i+width
            if index < unitsPerDay:
               demand[index]= power
    return demand

unitsPerDay = 240
#print(calculateDemand(unitsPerDay))


#print(calculateDemand(240, 10))
##    mid = unitsPerDay/2
##    width = 14*unitsPerDay/24
##    demand = np.zeros(unitsPerDay+2)

##def chargeRate(percentFull):
##    if (percentFull < 60):
##        return 120*15 #15 amps max
##    else:
##        remaining = (100-percentFull)/40
##        return 15*(10/(remaining+10))
        
