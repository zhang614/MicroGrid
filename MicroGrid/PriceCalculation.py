import pytz
from datetime import datetime, timedelta




def energyValue(today, energy, timeIndex=0):
    # price = 1.0 #0.1
    # zone = 'off'
    # #return (price * energy, zone)
    # hour = today.hour % 24
    # if hour % 2 == 0:
    #     zone = 'peak'
    #     price = 2.0
    # if hour >= 6 and hour <= 9 or hour >= 17 and hour <= 20:
    #     price = 2.0
    #     zone = 'peak'
    # if energy > 0:
    #     # Buy
    #     return (+1*price * energy , zone)
    # # have to Sell
    # return ( +1 * price * energy , zone)

    timeZone = pytz.timezone('US/Mountain')
    offPrice = 0.065
    peakPrice = 0.132
    midPrice = 0.094
    if today.hour <= 7:
        hourSection = 0
    elif today.hour <= 11:
        hourSection = 1
    elif today.hour <= 17:
        hourSection = 2
    elif today.hour <= 19:
        hourSection = 3
    else:
        hourSection = 4
    winterCost = [offPrice, peakPrice, midPrice, peakPrice, offPrice]
    winterZone = ['off', 'peak', 'mid', 'peak', 'off']
    summerCost = [offPrice, midPrice, peakPrice, midPrice, offPrice]
    summerZone = ['off', 'mid', 'peak', 'mid', 'off']
    # returns the cost for this much energy for one time period
    if today.strftime("%a") in ['Saturday', 'Sunday']:
        zone = 'off'
        price = offPrice
    else:
        if (today >= datetime(2018, 11, 1, 0, 0, 0, 0, timeZone) and
                today <= datetime(2019, 4, 30, 0, 0, 0, 0, timeZone)):
            # winter
            price = winterCost[hourSection]
            zone = winterZone[hourSection]
        else:
            price = summerCost[hourSection]
            zone = summerZone[hourSection]
    if energy > 0:
        # Buy
        return (+1 * price * energy, zone)
    # have to sell
    return (+1 * price * energy, zone)  # (-100000, zone)
    # (+1 * price * energy , zone)