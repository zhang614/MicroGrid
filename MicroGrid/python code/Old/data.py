import numpy as np
import math
import random as rn
from collections import namedtuple
from loads import *
import numpy as np
import datetime
from astral import Astral
import scrape
from scipy.interpolate import interp1d

#time of use charges, based on a 24 hour clock
#http://www.pge.com/en/mybusiness/rates/tvp/toupricing.page?WT.mc_id=Vanity_TOU
TOU = ([0.2 for i in range(0,9)] + #early morning cheap
       [0.25 for i in range(9,12)]+ #late morning
       [0.3 for i in range(12,18)]+ #peak times
       [0.2 for i in range(18,24)]) #cheap
# https://www.nvenergy.com/home/paymentbilling/timeofuse.cfm
TOU = ([0.06 for i in range(0,13)] +
       [0.36 for i in range(13,19)] + #peak
       [0.06 for i in range(19,24)])

def calculateSupply(sampleTime, startHour, numberOfHours, maxPower):
    #sample time is in minutes
    # returns an array of estimated watts for each time sample during the day, starting at midnight
    # can be multiple day
    maxTime = math.ceil((numberOfHours+startHour)*60/sampleTime)
    minTime = math.floor(startHour*60/sampleTime)
    dayTime = 24 * 60/sampleTime #how many samples in a day
    nowDay = datetime.datetime.utcnow()
    solarData = oneDaySun(nowDay, dayTime, sampleTime, maxPower)
    for day in range(numberOfHours/24): #any extra days?
        nowDay = nowDay + datetime.timedelta(days=1) ###NEXT DAY
        oneSolarData = oneDaySun(nowDay, dayTime, sampleTime, maxPower)
        solarData = np.concatenate([solarData,oneSolarData])
    #finally cut the front off
    return np.array(solarData[minTime:maxTime+1])

def oneDaySun(today, dayTime, sampleTime, maxPower):
#returns a list of estimated solar energy to be collected today
    (riseIndex, noonIndex, setIndex) = getSunIndexes(today, sampleTime)
    width = setIndex - riseIndex #length of day
    sunLight = np.array([0 for col in range(dayTime+1)])
    for i in range(0, +width):
        sunLight[i+noonIndex-width/2] = math.floor(maxPower*math.sin((1.0*i/width)*3.1415))
    skyClear = getSkyClear(sampleTime)
    solarLight = sunLight*skyClear
    return solarLight

def calculateSupplyOLD(sampleTime, startHour, numberOfHours, maxPower):
    #sample time is in minutes
    # returns an array of estimated watts for each time sample during the day, starting at midnight
    maxTime = math.ceil((numberOfHours+startHour)*60/sampleTime)
    minTime = math.floor(startHour*60/sampleTime)
    dayTime = 24 * 60/sampleTime
    (riseIndex, noonIndex, setIndex) = getSunIndexes(datetime.utcnow(), sampleTime)
    width = setIndex - riseIndex #length of day
    sunLight = np.array([0 for col in range(dayTime+1)])
    for i in range(0, +width):
        sunLight[i+noonIndex-width/2] = math.floor(maxPower*math.sin((1.0*i/width)*3.1415))
    skyClear = getSkyClear(sampleTime)
    solarLight = sunLight*skyClear
    return np.array(solarLight[minTime:maxTime+1])

def getSkyClear(sampleTime):
    # returns one day of sky clear fraction (1= no clouds, 0 = all clouds) data sampled at sampleTime (in min)
    # currently gives the earliest full day of data taken from scrap.py data
    solarData = scrape.getWeather()
    for i in range(len(solarData)):
        if solarData[i].date.hour == 0: #midnight, start of a new day
            dayData = [solarData[j].sky for j in range(i, i+24)]
            break
    timeSamples = np.linspace(0,24, 1+24*60/sampleTime)
    hourSamples = np.linspace(0,24, 24)
    skyF = interp1d(hourSamples, dayData, kind='cubic') #bounds_error=False, fill_value=dayData[0])
    #return np.array([(100.0-skyF(i).min())/100.0 for i in timeSamples]) #need the min to turn array(55) to 55
    return np.array([(100.0)/100.0 for i in timeSamples]) #need the min to turn array(55) to 55
    #print [dayData[i*sampleTime/60] for i in range(60*24/sampleTime)]

def getSunIndexes(date, sampleTime):
    #returns the sunrise, noon and sunset times in units of sampleTime
    astral = Astral()
    astral.solar_depression = 'civil'
    city = astral['Salt Lake City']
    sun = city.sun(date=date, local=True)
    riseIndex = (sun['sunrise'].hour*60+sun['sunrise'].minute)/sampleTime
    noonIndex = (sun['noon'].hour*60+sun['noon'].minute)/sampleTime
    setIndex = (sun['sunset'].hour*60+sun['sunset'].minute)/sampleTime
    return (riseIndex, noonIndex, setIndex)

#print(calculateSupply(5, 24, 1000))

#loops through each appliance in the home and returns a sequence of possible power demands for this house
def calculateDemand(sampleTime, startHour, numberOfHours, home):
    #takes a scaling factor and the list of appliances in the home
    eachLoad = map(lambda appliance: demand(appliance, sampleTime, startHour, numberOfHours), home)
    return np.array([sum(x) for x in zip(*eachLoad)])

#takes a load and returns a time series of power consumption for this load
def demand(appliance, sampleTime, startHour, numberOfHours):
    #returns a list of power demands over time
    maxTime = (numberOfHours+startHour)*60/sampleTime
    minTime = startHour*60/sampleTime
    unitsPerDay = 24*60/sampleTime

    thisDemand = oneDayDemand(appliance, unitsPerDay)
    for day in range(numberOfHours/24): #any extra days?
        oneDemand = oneDayDemand(appliance, unitsPerDay)
        thisDemand = np.concatenate([thisDemand,oneDemand])
    #finally cut the front off
    return np.array(thisDemand[minTime:maxTime+1])

def oneDayDemand(appliance, unitsPerDay):
    #returns the demand for the appliance for one day
    if type(appliance) is type(constant):
        thisDemand = makeConstant(unitsPerDay, appliance.power)
    if type(appliance) is type(periodic): #periodic
        separation = appliance.wavelength*unitsPerDay/24/60
        duration = appliance.duration*unitsPerDay/24/60
        power = appliance.power
        thisDemand =  makePeriodic(unitsPerDay, separation, duration, power)
    if type(appliance) is type(intermitent): #intermitent
        startIndex = appliance.start*unitsPerDay/24 #hour of the day
        endIndex = appliance.end*unitsPerDay/24
        period = (endIndex-startIndex)
        power = appliance.power
        duration = appliance.duration
        howMany = appliance.frequency*period*24/unitsPerDay #per hour
        thisDemand =  makeIntermitent(unitsPerDay, startIndex, period, howMany, duration, power)
    return thisDemand

#returns a time series of power consumption for this load
def makeIntermitent(unitsPerDay, startIndex, period, howMany, duration, power):
    demand = [0 for col in range(unitsPerDay+1)]
    for count in range(0,howMany+1):
        start = rn.randint(0,period)
        width = duration + rn.randint(-1*duration/10, duration/10)
        for i in range(0,width):
            index = start+i
            if index < unitsPerDay:
               demand[startIndex+index]+= power
    return demand

def makeConstant(unitsPerDay, power):
    return [power for col in range(unitsPerDay+1)]
    
        
def makePeriodic(unitsPerDay, separation, duration, power):
    demand = [0 for col in range(unitsPerDay+1)]
    for i in range(0, unitsPerDay/separation):
        for width in range(0,duration+1):
            index = i+separation*i+width
            if index < unitsPerDay:
               demand[index]= power
    return demand

def toWH(power,sampleTime):
    # power to energy for one time step
    return power*(sampleTime/60.0)

def toW(energy,sampleTime):
    # energy to power for one time step
    return int(energy/(sampleTime/60.0))

###calculateSupply(sampleTime, startHour, numberOfHours, maxPower)
##print calculateSupply(20, 6, 20, 1000)
##
##print calculateSupply(20, 0, 20+24, 1000)
##
##print calculateSupply(20, 0, 20+2*24, 1000)

#calculateDemand(sampleTime, startHour, numberOfHours, home):
home=[draw,lightsEarly, lightsLate, fridge]
print calculateDemand(20, 6, 24, home)
print calculateDemand(20, 0, 48, home)

#print(calculateDemand(5, 12, [fridge]))

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

print demand(airConditioner, 24,7,1)
#print demand(coffeeMaker, 5, 2)
