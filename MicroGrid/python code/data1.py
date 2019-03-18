import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch
import json
import datetime
from itertools import takewhile
import math
import collections

MONTH = 11
YEAR = 2016
FILENAME = 'LocationHistory.json'
ADDRESS = '649 E 800 N Logan UT'
# used to find the home location
# geolocator = Nominatim(user_agent="specify_your_app_name_here")
# HOMELOCATION = geolocator.geocode(ADDRESS,timeout=10)
HOMELAT = 41.7465082331669

with open(FILENAME, 'r') as fh:
    raw = json.loads(fh.read())
ld = pd.DataFrame(raw['locations'])
del raw
ld['latitudeE7'] = ld['latitudeE7'] / float(1e7)
ld['longitudeE7'] = ld['longitudeE7'] / float(1e7)
ld['timestampMs'] = ld['timestampMs'].map(lambda x: float(x) / 1000)  # to seconds
ld['datetime'] = ld.timestampMs.map(datetime.datetime.fromtimestamp)
ld.rename(columns={'latitudeE7': 'latitude', 'longitudeE7': 'longitude', 'timestampMs': 'timestamp'}, inplace=True)
ld = ld[ld.accuracy < 1000]  # Ignore locations with accuracy estimates over 1000m
ld.reset_index(drop=True, inplace=True)


# plots the data of charge times for the mont of october
def plotDatcharge(ld):
    x = []
    y = []
    for i in range(1, 30):
        y.append(i)
        point = timeRange(i, i + 1, ld)
        x.append(chargeToats(point) * 100)
    plt.bar(y, x, align='center')
    plt.title('Estimated possible charging time per day')
    plt.ylabel('time available for charging by percent of day')
    plt.xlabel('Days October 2016')
    plt.show()


# plots the data of kwh used for the month of october
def plotDataKwh(ld):
    x = []
    y = []
    for i in range(1, 30):
        y.append(i)
        point = timeRange(i, i + 1, ld)
        x.append(calcEnergy(point))

    plt.bar(y, x, align='center')
    plt.title('Estimated kwh per day')
    plt.ylabel('kwh used per day')
    plt.xlabel('Days October 2016')
    plt.show()


# returns an array of the days you are interested in
def timeRange(x, y, ld):
    ld = ld[ld.datetime > datetime.datetime(YEAR, MONTH, x)]
    ld = ld[ld.datetime < datetime.datetime(YEAR, MONTH, y)]
    return ld


degrees_to_radians = np.pi / 180.0
ld['phi'] = (90.0 - ld.latitude) * degrees_to_radians
ld['theta'] = (ld.longitude) * degrees_to_radians

ld['distance'] = np.arccos(
    np.sin(ld.phi) * np.sin(ld.phi.shift(-1)) * np.cos(ld.theta - ld.theta.shift(-1)) +
    np.cos(ld.phi) * np.cos(ld.phi.shift(-1))) * 6378.100  # radius of earth in km

ld['speed'] = ld.distance / (ld.timestamp - ld.timestamp.shift(-1)) * 3600  # km/hr


def timeAtHome(ld):
    chargeable = ld[ld.speed < 5]
    chargeable = chargeable[chargeable.latitude == chargeable.latitude.shift(-1)]
    chargeable = chargeable[chargeable.longitude == chargeable.longitude.shift(-1)]
    # home=chargeable[abs(chargeable.latitude-HOMELOCATION.latitude)<3]
    home = chargeable[abs(chargeable.latitude - HOMELAT) < 3]
    return home


# returns a precentage of the time you could charge at home
def chargeToats(ld):
    toats = 1
    for y in ld['datetime']:
        toats += 1
    energyUsed = 0.0
    ld = timeAtHome(ld)
    for y in ld['datetime']:
        energyUsed = energyUsed + 1
    energyUsed = (energyUsed)
    return energyUsed / toats


# Uses the distence of trips in a day to calculate the overall energy requirements
def calcEnergy(ld):
    energyUsed = 0.0

    ld = ld[ld.distance > 0]
    ld = ld[ld.speed > 0]
    for y in ld['distance']:
        energyUsed = energyUsed + y
    energyUsed = (energyUsed * .621371) / 3
    return energyUsed


def storeUse():
    z = []
    i = 14
    point = timeRange(i, i + 1, ld)
    z.append((calcEnergy(point)))
    return (z)


# stores the charge of the previuse day
def storePrevCharge():
    w = []
    for x in range(1, 24):
        a = x - 1
        ldi = ld[ld.datetime < datetime.datetime(YEAR, MONTH, 14, x)]
        ldi = ldi[ldi.datetime > datetime.datetime(YEAR, MONTH, 14, a)]
        r = chargeToats(ldi)
        w.append(r)
        w.append(r)
        w.append(r)
    w.append(0)
    w.append(0)
    w.append(0)
    return (w)


# creates an array of times you are home in the night
def storecharge():
    w = []
    for x in range(1, 24):
        a = x - 1
        ldi = ld[ld.datetime < datetime.datetime(YEAR, MONTH, 15, x)]
        ldi = ldi[ldi.datetime > datetime.datetime(YEAR, MONTH, 15, a)]
        r = chargeToats(ldi)
        w.append(r)
        w.append(r)
        w.append(r)
    w.append(0)
    w.append(0)
    w.append(0)
    return (w)


# finds the time you got home at the end of the day to start charging
def findPrevTime(x):
    for i in range(51, 71):
        if (x[i] == 0):
            return i + 6
    return -1


# finds the time in the mourning you leave at
def findTime(x):
    for i in range(15, 72):
        if (x[i] == 0):
            return i + 6
    return -1
