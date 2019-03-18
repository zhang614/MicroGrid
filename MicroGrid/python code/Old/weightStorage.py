# -*- coding: cp1252 -*-
import numpy as np
import math
import random as rn
from collections import namedtuple
from loads import *
import numpy as np
from datetime import datetime
from astral import Astral

def calculateStorageCapacity(height, volume):
    # height in meters, volume in gals
    # returns the energy storage in kwh
    # EM = (1kg×9.8m/sec2×0.5H×Efficiency)/(3600Joules/Wh) = 1.36×10-3×Efficiency×H
    # http://www.energystoragenews.com/Energy%20Storage%20in%20Elevated%20Weights.htm
    # http://www.thecalculatorsite.com/conversions/substances/water.php
    return (1.36/1000.0)*height*volume*3.785

# $20/10^4gal, 1 qubic foot of water
print calculateStorageCapacity(20, 10000)

##astral = Astral()
##astral.solar_depression = 'civil'
##city = astral['Salt Lake City']
##def maxElevation(daytime):
##    maxE = -1000;
##    for hour in range(0, 23):
##        daytime = daytime.replace(hour=hour)
##        winterE = city.solar_elevation(daytime)
##        maxE = max(maxE, winterE)
##    return maxE
##
##winterSolstice = datetime(2015, 12, 21)
##summerSolstice = datetime(2015, 6, 21)
##print maxElevation(winterSolstice)
##print maxElevation(summerSolstice)
##    
##
##winterE = city.solar_elevation(winterSolstice)
##winterA = city.solar_azimuth(winterSolstice)
##
##summerE = city.solar_elevation(summerSolstice)
##
##sun = city.sun(date=winterSolstice, local=True)
##riseIndex = (sun['sunrise'].hour*60+sun['sunrise'].minute)/sampleTime
##noonIndex = (sun['noon'].hour*60+sun['noon'].minute)/sampleTime
##setIndex = (sun['sunset'].hour*60+sun['sunset'].minute)/sampleTime

