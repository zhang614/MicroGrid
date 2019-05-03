import urllib.request, urllib.error, urllib.parse
import re
#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
from math import *
import matplotlib.pyplot as plt

solarData = namedtuple("SolarData", "sky temp date")
#                           " %sky cover, F, arrow"
#SLC
Site = 'http://forecast.weather.gov/MapClick.php?w0=t&w3u=1&w4=sky&w5=pop&w7=rain&AheadHour=*&Submit=Submit&FcstType=digital&textField1=41.8383&textField2=-111.8327&site=all&unit=0&dd=&bw='
#Logan
Site = 'http://forecast.weather.gov/MapClick.php?w0=t&w3u=1&w4=sky&w5=pop&w7=rain&AheadHour=*&Submit=Submit&FcstType=digital&lat=41.74290000000008&lon=-111.82256999999998&site=all&unit=0&dd=&bw='
# test
# Site = 'http://forecast.weather.gov/MapClick.php?w0=t&w3u=1&w4=sky&w5=pop&w7=rain&AheadHour=0&Submit=Submit&FcstType=digital&lat=41.74290000000008&lon=-111.82256999999998&site=all&unit=0&dd=&bw='


# GETS THE WEATHER DATA FOR CLOUD COVER OFF THE WEB
def getWeather(nowTime, numberOfHours):
    #returns numberOfHours of weather data sampled each hour
    numberOfDays = numberOfHours/24.0
    weatherData = []
    for dayIndex in range(0, int(ceil(numberOfDays)), 2): #every two days
        weatherData.extend(getWeatherOnePage(nowTime, dayIndex))
    # trim data just to what we need
    return weatherData[0:numberOfHours]

def getWeatherOnePage(nowTime, daysAhead):
    #returns 48 hours of data, starting at nowTime
    url = Site.replace('*', str(daysAhead*24))
    print(url)
    headers = {'User-Agent': 'Mozilla/5.0'} #headers
    req = urllib.request.Request(url, None, headers)
    pageString = urllib.request.urlopen(req, timeout=4).read() #added time out
    soup = BeautifulSoup(pageString, "lxml")
    #print soup.prettify()
    table = soup.findAll("table", width=800)[2] #data table on page
    # top half and bottom half of the table
    return getWeatherTable(table, 2, 3, 4, nowTime + relativedelta(hours = 24 * daysAhead))  + \
            getWeatherTable(table, 9,10,11, nowTime + relativedelta(hours = 24 * (daysAhead + 1)))
            #

def getWeatherTable(table, hourID, tempID, skyID, nowTime):
    hourRow = table.findAll('tr')[hourID] #[2]
    tempRow = table.findAll('tr')[tempID] #[3]
    skyRow = table.findAll('tr')[skyID] #[4]
    # get the colums
    skyColumns = skyRow.findAll('td')
    #print skyColumns
    tempColumns = tempRow.findAll('td')
    hourColumns = hourRow.findAll('td')
    # loop through each column and extract data
    solarList = []
    lastHour = 100
    addDay = False
    print(nowTime)
    for i in range(1,len(skyColumns)): #start with 1
        hour = int(hourColumns[i].b.text)
        if lastHour == 23 and hour == 0: #roll over
            addDay = True
        dateTime = nowTime.replace(hour = hour)
        if addDay:
            dateTime = dateTime + relativedelta(hours = 24)
        #print dateTime
        solarList.append(solarData(int(skyColumns[i].b.text), int(tempColumns[i].b.text), dateTime))
        lastHour = hour
    return solarList

#test
# utc = datetime.today()
# timezone = pytz.timezone('US/Mountain')
# nowTime = timezone.localize(utc)#.replace(minute = 0, second = 0, microsecond = 0)
# howManyHours = 24*6
# data = getWeather(nowTime, howManyHours)
# for i in range(0, len(data)):
#     print(data[i].date.strftime('%b_%d_%H')+" " + str(data[i].temp)+' '+str(data[i].sky))
#
# plt.plot([data[i].sky for i in range(0, len(data))], drawstyle="steps")
# plt.show()
#
# print "Number of hours = " + str(len(data))