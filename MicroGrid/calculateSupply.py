import numpy as np
from math import *
import random as rn
from collections import namedtuple
# from loads import *
import numpy as np
from datetime import datetime
from astral import Astral
import scrape
from scipy.interpolate import interp1d
from collections import namedtuple
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import pandas as pd

solarData = namedtuple("sunDay", "riseIndex noonIndex setIndex")


# CHANGE TO START AT MST,
# MULTI DAY PREDICTIONS
# UNITS NEED TO BE IN ENERGY SAMPLE
# same with DEMAND
def calculateSupply(nowTime, sampleTime,maxtime, numberOfHours, solarPower):
    # sample time is in minutes
    # returns an array of estimated energy units for each time sample
    # starting at nowTime
    maxTime = maxtime
    # return [0 for i in range(0, maxTime)]
    #############################
    astral = Astral()
    astral.solar_depression = 'civil'
    city = astral['Salt Lake City']
    # array of sky clear length maxTime, 1.0 is totally clear, 0 is cloudy
    clearSky = getSkyClear(nowTime, numberOfHours, sampleTime)
    # print "clear"
    # print clearSky
    sunStrength = getSunStrength(city, nowTime, numberOfHours, sampleTime)
    # print "sun Strength"
    print (len(sunStrength))
    onePower = [sunEstimate(sunStrength[i], clearSky[i]) * solarPower for i in range(0, maxTime)]
    # print "one Power"
    # print onePower
    # supply = [calculateOneTimeEnergy(onePower[i], sampleTime, energySample) for i in range(0, maxTime)]
    # print supply
    return onePower


def sunEstimate(sunStrength, clearSky):
    # both between 0.0 -> 1.0. Add 25% for background light
    return (0.75 * clearSky + 0.25) * sunStrength


def calculateOneTimeEnergy(onePower, sampleTime, energySample):
    return int(onePower  # power for this time period
               * (sampleTime / 60.0)  # multiply by time
               * energySample)  # quantize into energy units


def getSkyClear(nowTime, numberOfHours, sampleTime):
    # uses the weather data scraped from the web
    # sky clear fraction (1= no clouds, 0 = all clouds) data sampled at sampleTime (in min)
    maxTime = numberOfHours * 60 / sampleTime
    solarData = scrape.getWeather(nowTime, numberOfHours)
    clearHourly = [solarData[i].sky for i in range(0, len(solarData))]
    # resample hourly at sample rate
    timeSamples = np.linspace(0, numberOfHours, maxTime)
    hourSamples = np.linspace(0, numberOfHours, numberOfHours)
    skyF = interp1d(hourSamples, clearHourly, kind='cubic')  # bounds_error=False, fill_value=dayData[0])
    # print "clear"
    # print clearHourly
    # print "Direct"
    # print np.array([skyF(i) for i in timeSamples])
    # print "MIN"
    # print np.array([(skyF(i).min()) for i in timeSamples])
    # print "final return "
    # print np.array([(100.0-skyF(i).min())/100.0 for i in timeSamples])
    # plt.plot(clearHourly, drawstyle="steps")
    # #plt.plot(timeSamples,skyF)
    # #plt.plot([(100.0-skyF(i).min())/100.0 for i in timeSamples], drawstyle="steps")
    # plt.show()
    return np.array([(100.0 - skyF(i).min()) / 100.0 for i in timeSamples])  # need the min to turn array(55) to 55
    # print [dayData[i*sampleTime/60] for i in range(60*24/sampleTime)]


def getSunStrength(city, nowTime, numberOfHours, sampleTime):
    oneDay = nowTime.replace(hour=0, minute=0, second=0)
    numberOfDays = int(ceil(numberOfHours / 24.0)) + 1
    sunData = []
    for i in range(numberOfDays):
        sunData.extend(getSunOneDay(city, oneDay, sampleTime))
        oneDay = oneDay + relativedelta(hours=24)
    startIndex = indexOffset(nowTime, sampleTime)
    # trim start so it begins at nowTime and ends at number of Hours
    return sunData[startIndex: startIndex + numberOfHours * 60 // sampleTime]


def getSunOneDay(city, oneDay, sampleTime):
    # returns one day of data at sample time with the sun strength
    (riseIndex, noonIndex, setIndex) = getSunIndex(city, oneDay, sampleTime)
    width = setIndex - riseIndex  # length of day
    sunLight = np.zeros(24 * 60 // sampleTime)
    for i in range(0, +width):
        sunLight[i + noonIndex - width // 2] = sin((1.0 * i / width) * pi)
    return list(sunLight)


def getSunIndex(city, oneDay, sampleTime):
    # returns the sunrise, noon and sunset times in units of sampleTime
    sun = city.sun(date=oneDay, local=True)
    riseIndex = indexOffset(sun['sunrise'], sampleTime)
    noonIndex = indexOffset(sun['noon'], sampleTime)
    setIndex = indexOffset(sun['sunset'], sampleTime)
    return (riseIndex, noonIndex, setIndex)


def indexOffset(dayTime, sampleTime):
    return (dayTime.hour * 60 + dayTime.minute) // sampleTime


def calculatedemand(SampleTime,MaxTime,NumberofHours):
    data_frame = pd.read_csv('Load_dailyhours_average.csv')


# def calculateDemand(nowTime, sampleTime, numberOfHours, home, energySample):
#     # calculates for each day+1 starting at 00, then trims
#     numberOfDays = int(ceil(numberOfHours / 24.0)) + 1
#     demandData = []
#     for i in range(numberOfDays):
#         demandData.extend(demandOneDay(sampleTime, home, energySample))
#     startIndex = indexOffset(nowTime, sampleTime)
#     # trim start so it begins at nowTime and ends at number of Hours
#     return demandData[startIndex: startIndex + numberOfHours * 60 // sampleTime]


# def demandOneDay(sampleTime, home, energySample):
#     # takes a scaling factor and the list of appliances in the home for one day
#     eachLoad = [demandOneAppliance(appliance, sampleTime) for appliance in home]
#     sumDay = [calculateOneTimeEnergy(sum(x) / 1000, sampleTime, energySample) for x in zip(*eachLoad)]
#     return sumDay


# def demandOneAppliance(appliance, sampleTime):
#     # returns a list of demands for this appliance for one day
#     unitsPerDay = 24 * 60 // sampleTime
#     # print "units per day = " + str(unitsPerDay)
#     if type(appliance) is type(constant):
#         thisDemand = makeConstant(unitsPerDay, appliance.power)
#     if type(appliance) is type(periodic):  # periodic
#         separation = int(ceil(appliance.wavelength * unitsPerDay / 24.0 / 60))
#         duration = appliance.duration * unitsPerDay // 24 // 60
#         power = appliance.power
#         thisDemand = makePeriodic(unitsPerDay, separation, duration, power)
#     if type(appliance) is type(intermitent):  # intermitent
#         startIndex = appliance.start * unitsPerDay // 24  # hour of the day
#         endIndex = appliance.end * unitsPerDay // 24
#         period = (endIndex - startIndex)
#         power = appliance.power
#         duration = appliance.duration
#         howMany = appliance.frequency * period * 24 // unitsPerDay  # per hour
#         thisDemand = makeIntermitent(unitsPerDay, startIndex, period, howMany, duration, power)
#     return thisDemand


def makeIntermitent(unitsPerDay, startIndex, period, howMany, duration, power):
    demand = [0 for col in range(unitsPerDay)]
    for count in range(0, howMany + 1):
        start = rn.randint(0, period)
        width = duration + rn.randint(-1 * duration // 2, duration // 2)
        for i in range(0, width):
            index = start + i
            if startIndex + index < unitsPerDay:
                demand[startIndex + index] += power
    return demand


def makeConstant(unitsPerDay, power):
    return [power for col in range(unitsPerDay)]


def makePeriodic(unitsPerDay, separation, duration, power):
    demand = [0 for col in range(unitsPerDay)]
    for i in range(0, unitsPerDay // separation):
        for width in range(0, duration + 1):
            index = i + separation * i + width
            if index < unitsPerDay:
                demand[index] = power
    return demand

# print(calculateDemand(5, 12, [fridge]))

# print(calculateDemand(240, 10))
##    mid = unitsPerDay/2
##    width = 14*unitsPerDay/24
##    demand = np.zeros(unitsPerDay+2)

##def chargeRate(percentFull):
##    if (percentFull < 60):
##        return 120*15 #15 amps max
##    else:
##        remaining = (100-percentFull)/40
##        return 15*(10/(remaining+10))