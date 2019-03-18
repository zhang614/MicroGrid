import data
import math
import numpy as np
import display as dis
import math
import loads
import rewardFunctions as reward
from datetime import datetime, timedelta
import pytz
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

# Supply[i] is the supply of watts available 
# D[i] is the required demand in watts
SampleTime = 5  # 60 #5 #20 #60 #in minutes, connot be greater than one hour
NumberOfHours = 2 * 24  # 40 #24*2 #24*2 #can be multi day
MaxTime = NumberOfHours * 60 // SampleTime  # number of sampleTime minute intervals
Gamma = 1
CannotSell = True  # Islanded
# SUPPLY 
SolarPower = 80 * 290 / 1000.0  # in KW
# HOME LIST OF LOADS
# loads.dryerMachine,
Home = [loads.draw, loads.fridge, loads.washingMachine, loads.dryerMachine,
        loads.lightsEarly,
        loads.lightsLate, loads.fridge, loads.kettle, loads.coffeeMaker, loads.airConditioner]  # , loads.coffeeMaker,
# Battery
BatteryMaxEnergy = 20  # in KWH
EnergySample = 10  # 10 # how many divisions per KWH
MaxBattery = BatteryMaxEnergy * EnergySample  # number of quantizations for battery energy
MinBattery = int(0.0 * MaxBattery)
MaxPercentBatteryChange = .1
MaxDeltaBatt = int(MaxBattery * MaxPercentBatteryChange)


# fills state array with associated reward
def valueIteration(nowTime):
    # nowTime
    Vfunction = np.ones((MaxBattery + 1,
                         MaxTime + 1)) * -1000  # battery level at each state here state is at the given time and power in the battery
    endTime = nowTime + relativedelta(minutes=MaxTime * SampleTime)
    # terminal reward is the value of the energy in the battery at endTime
    for battIndex in range(0, MaxBattery + 1):
        (value, _) = reward.energyValue(endTime, 1 * battIndex * 1.0 / EnergySample, MaxTime)
        Vfunction[battIndex][MaxTime] = round(value, 4)
    doneError = 0.01
    while True:
        dayTime = nowTime + relativedelta(minutes=SampleTime * MaxTime)
        maxError = 0
        for timeIndex in range(MaxTime - 1, -1, -1):  # dont do the last one, go backwards
            for battIndex in range(0, MaxBattery + 1):
                value = Vfunction[battIndex][timeIndex]
                (bestReturn, _) = applyBellman(Vfunction, timeIndex, battIndex, dayTime)
                Vfunction[battIndex][timeIndex] = bestReturn
                maxError = max(maxError, abs(value - bestReturn))
            dayTime = dayTime + relativedelta(minutes=-SampleTime)
        print(("Error = " + str(maxError)))
        if maxError < doneError:
            break
        break  # Only do once
    return Vfunction


def applyBellman(Vfunction, timeIndex, battIndex, dayTime):
    bestReturn = -100000
    bestChange = 0
    # from fully discharge to fully charge Battery actions
    for changeBatt in generatePossibleCharges(battIndex, MaxBattery):
        newBattIndex = battIndex + changeBatt
        if newBattIndex < MinBattery or newBattIndex > MaxBattery:
            continue
        # supply is solar power
        # supply is always positive, demand is always negative
        # change Batt neg is withdraw, plus is add
        # netEnergy is positive then buy
        netEnergy = + Supply[timeIndex] + Demand[timeIndex] - changeBatt
        # if netEnergy < 0 and CannotSell:
        #     continue
        (value, _) = reward.energyValue(dayTime, netEnergy, timeIndex)
        nowReturn = round(value +
                          # reward.chargeDischargeCost(changeBatt, MaxDeltaBatt) +
                          # reward.chargedValue(newBattIndex, MaxBattery) +
                          Gamma * Vfunction[newBattIndex][timeIndex + 1], 4)
        if nowReturn >= bestReturn:
            bestReturn = nowReturn
            bestChange = changeBatt
    return (bestReturn, bestChange)


def generatePossibleCharges(battIndex, MaxBattery):
    # one charge rate based on battIndex, multiple discharges
    if battIndex == MaxBattery:
        charge = []
    else:
        # max charge rate is 1/4 of max discharge rate
        val = math.exp(-1 * MaxPercentBatteryChange * 0.14 * (battIndex - MinBattery))
        charge = [int(math.ceil(1 * MaxDeltaBatt * (val / (1 + val))))]
    return charge + list(range(0, -MaxDeltaBatt - 1, -1))


def computePolicy(Vfunction, battIndex, nowTime):  # beginning battery at index 0
    # return the policy for each index
    # print "POLICYv&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    policy = []
    batteryState = [battIndex]
    dayTime = nowTime
    for timeIndex in range(0, MaxTime):
        (_, battChange) = applyBellman(Vfunction, timeIndex, battIndex, dayTime)
        battIndex = battIndex + battChange
        policy.append(battChange)
        batteryState.append(battIndex)
        dayTime = dayTime + relativedelta(minutes=SampleTime)
    return (policy, batteryState)


def computeBuySell(policy, supply, demand):
    # change in battery + supply + demand (negative) + extra = 0
    buy = []
    sell = []
    for i in range(0, len(policy)):
        # supply is always positive, demand is always negative
        # change Batt neg is withdraw, plus is add
        # netEnergy is positive then buy
        # netEnergy = - Supply[timeIndex] - Demand[timeIndex] + changeBatt #from bellman
        extra = - policy[i] + supply[i] + demand[i]
        if extra > 0:
            sell.append(extra)
            buy.append(0)
        else:
            sell.append(0)
            buy.append(extra)
    return (buy, sell)


def computeCostList(buySell, dayTime):
    cost = 0
    costList = [cost]
    zoneList = ['']
    for timeIndex in range(0, MaxTime):
        (value, zone) = reward.energyValue(dayTime, buySell[timeIndex], timeIndex)
        zoneList.append(zone)
        cost = value + cost
        costList.append(cost)
        dayTime = dayTime + relativedelta(minutes=SampleTime)
    return (costList, zoneList)


# #used to draw images needed
# plt.imshow(V, interpolation="nearest",origin='lower')
#
# cbar = plt.colorbar()
# cbar.set_label('Money spent in dollars',size=18)
# plt.title('Data Results')
# plt.ylabel('Battery Charged kwh')
# plt.xlabel('Hours in twenty minute intervals')
# plt.xticks(np.arange(10)*3, ('9', '10', '11', '12am', '1','2','3','4','5','6','7'))
# ax = plt.axes()
# eBatt = 5
# policy = policy(eBatt)
# for i in range(0, TIME_SECTIONS - 1):
#     ax.arrow(i, eBatt , 1, policy[i], head_width=0.05, head_length=0.1, fc='k', ec='k')
#     eBatt = eBatt + policy[i]
# plt.show()

def optimize():
    global Supply, Demand, Vtable
    utc = datetime.today()
    timezone = pytz.timezone('US/Mountain')
    nowTime = timezone.localize(utc).replace(minute=0, second=0, microsecond=0)
    Supply = data.calculateSupply(nowTime, SampleTime, NumberOfHours, SolarPower, EnergySample)
    # print "Supply"
    # print Supply
    Demand = data.calculateDemand(nowTime, SampleTime, NumberOfHours, Home, EnergySample)
    # print "Demand"
    # print Demand
    Vtable = valueIteration(nowTime)
    # plt.plot([Vtable[0][i] for i in range(0, MaxBattery)], drawstyle = "steps")
    battIndex = MaxBattery // 2  # assume 50%
    (policy, batteryState) = computePolicy(Vtable, battIndex, nowTime)
    # print "Policy"
    # print policy
    # print "battery State"
    # print batteryState
    (buyEnergy, sellEnergy) = computeBuySell(policy, Supply, Demand)
    buySellList = [buyEnergy[i] + sellEnergy[i] for i in range(0, len(buyEnergy))]
    (costList, zoneList) = computeCostList(buySellList, nowTime)
    # for i in range(0,len(batteryState)-1):
    #     print str(i) + "    " + str(buyEnergy[i]+sellEnergy[i]+policy[i]+Supply[i]+Demand[i])
    # print "buy"
    # print buyEnergy
    # print "sell"
    # print sellEnergy
    dis.graphVfunction(Vtable, batteryState, SampleTime)
    # buyEnergy = [], sellEnergy = [], sampleTime = 60, nowDayTime = None, supply = [], demand = [], costList = [], zoneList = [], title = ""
    print((len(batteryState)))
    print (batteryState)
    print((len(buyEnergy)))
    print (buyEnergy)
    dis.graphMicroGrid(batteryState[:-1], buyEnergy=buyEnergy, sellEnergy=sellEnergy,
                       supply=Supply, demand=Demand,
                       sampleTime=SampleTime, nowDayTime=nowTime,
                       costList=costList, zoneList=zoneList)
    # print Vtable
    # printV(Vtable)
    # plt.bar(np.arange(len(policy)),
    #         [po0.25,color='b',linewidth=0,antialiased = True)
    # plt.bar(np.arange(len(buyEnergy)),
    #         [policy[i] for i in range(0, len(policy))], alpha=0.25,color='g',linewidth=0,antialiased = True)
    # plt.bar(np.arange(len(sellEnergy)),
    #         [policy[i] for i in range(0, len(policy))], alpha=0.25,color='r',linewidth=0,antialiased = True)


def printV(vFunction):
    for batt in range(MaxBattery, -1, -1):
        row = vFunction[batt, :]
        print (row)


utc = datetime.today()
timezone = pytz.timezone('US/Mountain')
nowTime = timezone.localize(utc).replace(minute=0, second=0, microsecond=0)
# supply = data.calculateSupply(nowTime, SampleTime, NumberOfHours, SolarPower, EnergySample)
# plt.plot([supply[i] for i in range(0, len(supply))], drawstyle="steps")
# demand = data.calculateDemand(nowTime, SampleTime, NumberOfHours, Home, EnergySample)
# print "demand length = " + str(len(demand))
# plt.plot([demand[i] for i in range(0, len(demand))], drawstyle="steps")
# plt.show()

# print [generatePossibleCharges(i, MaxBattery)[0] for i in range(0,MaxBattery+1)]
optimize()