import gym
import gym_microgrid
import pandas as pd
import matplotlib.pyplot as plt
import display as dis
import data
import pytz
import PriceCalculation as pc
from datetime import datetime, timedelta
import numpy as np
import math
import load
from dateutil.relativedelta import relativedelta
env = gym.make('MicroGrid-v0')
# SolarPower = 80 * 290 / 1000.0
#solar and demand data


def initialization(sampletime=15,batterypanalty=0.01,numberOfhours=1*24,gamma=1,maxsolar=40,maxload=30,batterymaxenergy=20,energysample=10):
    global MaxTime,SampleTime,BatteryPanalty,Gamma,MaxSolar,MaxLoad,BatteryMaxEnergy,EnergySample,HourSample,MaxBattery,MinBattery,MaxPercentBatteryChange,MaxDeltaBatt
    BatteryPanalty = batterypanalty

    # time calculation
    SampleTime = sampletime  # 60 #5 #20 #60 #in minutes, connot be greater than one hour
    NumberOfHours = numberOfhours  # 40 #24*2 #24*2 #can be multi day
    MaxTime = NumberOfHours * 60 // SampleTime  # number of sampleTime minute intervals
    Gamma = gamma
    MaxSolar = maxsolar
    MaxLoad = maxload
    # Battery
    BatteryMaxEnergy = batterymaxenergy  # in KWH
    EnergySample = energysample  # 10 # how many divisions per KWH
    HourSample = 60 / SampleTime
    MaxBattery = BatteryMaxEnergy * EnergySample  # number of quantizations for battery energy
    MinBattery = int(0.0 * MaxBattery)
    MaxPercentBatteryChange = 1
    MaxDeltaBatt = int(MaxBattery * MaxPercentBatteryChange)

    env.render(SampleTime=SampleTime, BatteryMaxEnergy=BatteryMaxEnergy, NumberOfHours=NumberOfHours,
               EnergySample=EnergySample, BatteryPanalty=BatteryPanalty)


#
# def actioncalculation(batteryIndex,time):
#     d=demand[time]
#     s=solar[time]
#     a=[]
#     # print(d)
#     totalpowor=batteryIndex+s-d
#
#     for i in range(-totalpowor,MaxPower-totalpowor):
#         a.append(i)
#     return a
#
#
# def realactioncalculation(batteryIndex,time):
#     d = demand[time]
#     s = solar[time]
#     a=[]
#     totalpowor = batteryIndex + s - d
#     totalsell=int(chargedroprate*MaxPower)
#     totalbuy=int(chargingrate*MaxPower)
#     if (totalpowor<=MaxPower) and (totalpowor>=0):
#         if totalpowor - totalsell > 0:
#             for i in range(-totalsell, 0):
#                 a.append(i)
#         else:
#             for i in range(-totalpowor, 0):
#                 a.append(i)
#         if totalbuy + totalpowor > MaxPower:
#             for i in range(0, MaxPower - totalpowor + 1):
#                 a.append(i)
#         else:
#             for i in range(0, totalbuy + 1):
#                 a.append(i)
#     elif totalpowor<0:
#         for i in range(-totalpowor,totalbuy):
#             a.append(i)
#
#     else:
#         if totalpowor - totalsell > 0:
#             for i in range(-totalsell, MaxPower-totalpowor):
#                 a.append(i)
#         else:
#             for i in range(-totalpowor, MaxPower-totalpowor):
#                 a.append(i)
#
#     return a

# #valueIteration
# gama=1.0
# v=[[0 for i in range(MaxTime)] for j in range(MaxPower+1)]
# for i in range(0,MaxPower+1):
#     for j in range(0,96):
#         v[i][j]=-10000
#
#
# state = env.reset()
#
#
# for i in range(0, MaxPower + 1):
#
#         v[i][MaxTime-1] = round(i*priceofelectricity[MaxTime-1], 4)
#
#
# for time in range(MaxTime-1,-1,-1):
#     for batteryIndex in range(0,MaxPower+1):
#         env.close(batteryIndex, time)
#         action = realactioncalculation(batteryIndex, time)
#
#         bestValue = -1000
#         for j in range(0, len(action)):
#             # print(action[j])
#             nextstate, reward, done, info = env.step(action[j])
#             # print(nextstate,action[j])
#             newBatteryindex, newtime = nextstate
#             # print(batteryIndex,time,newBatteryindex,newtime,action[j])
#             value = reward + gama * v[int(newBatteryindex)][int(newtime)]
#             if value >= bestValue:
#                 bestValue = value
#                 nBatteryIndex = newBatteryindex
#                 nTime = newtime
#                 a = action[j]
#                 nreward = reward
#                 # gym.state=state
#         v[batteryIndex][time] = bestValue
#
#         # state[0] = nBatteryIndex
#         # state[1] = nTime
#         # if nreward>0:
#         #     print(nreward)
#         # print(a)
#     # print(state)
# # print(v)



def valueIteration(nowTime):
    # nowTime

    Vfunction = np.ones((MaxBattery + 1,
                         MaxTime + 1)) * -1000  # battery level at each state here state is at the given time and power in the battery
    endTime = nowTime + relativedelta(minutes=MaxTime * SampleTime)
    # terminal reward is the value of the energy in the battery at endTime
    for battIndex in range(0, MaxBattery + 1):
        # env.close(battIndex,MaxTime-1)
        value = (1 * battIndex * 1.0 / EnergySample)*priceofelectricity[MaxTime-1]
        # nextstep, reward, doen, info = env.step(0)
        Vfunction[battIndex][MaxTime] = round(value, 4)
    doneError = 0.01
    while True:
        dayTime = nowTime + relativedelta(minutes=SampleTime * MaxTime)
        maxError = 0
        for timeIndex in range(MaxTime - 1, -1, -1):  # dont do the last one, go backwards
            for battIndex in range(0, MaxBattery + 1):
                value = Vfunction[battIndex][timeIndex]
                env.close(battIndex,timeIndex)
                (bestReturn, _) = applyBellman(Vfunction, timeIndex, battIndex, dayTime)
                Vfunction[battIndex][timeIndex] = bestReturn
                maxError = max(maxError, abs(value - bestReturn))
            dayTime = dayTime + relativedelta(minutes=-SampleTime)
        # print(("Error = " + str(maxError)))
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
        nextstep,reward,doen,info=env.step(changeBatt)
        # netEnergy = + Supply[timeIndex] + Demand[timeIndex] - changeBatt

        # if netEnergy < 0 and CannotSell:
        #     continue
        # (value, _) = pc.energyValue(dayTime, netEnergy, timeIndex)
        nowReturn = round(reward +
                          # reward.chargeDischargeCost(changeBatt, MaxDeltaBatt) +
                          # reward.chargedValue(newBattIndex, MaxBattery) +
                          Gamma * Vfunction[newBattIndex][timeIndex + 1], 4)
        if nowReturn >= bestReturn:
            bestReturn = nowReturn
            bestChange = changeBatt
    return (bestReturn, bestChange)




def generatePossibleCharges(battIndex, MaxBattery):
    # one charge rate based on battIndex, multiple discharges
    # if battIndex == MaxBattery:
    #     charge = []
    # else:
    #     # max charge rate is 1/4 of max discharge rate
    #     val = math.exp(-1 * MaxPercentBatteryChange * 0.14 * (battIndex - MinBattery))
    #     charge = [int(math.ceil(1 * MaxDeltaBatt * (val / (1 + val))))]
    # return charge + list(range(0, -MaxDeltaBatt - 1, -1))
    return list(range(-MaxDeltaBatt,MaxDeltaBatt+1))






def computePolicy(Vfunction, battIndex, nowTime):  # beginning battery at index 0
    # return the policy for each index
    # print "POLICYv&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    policy = []

    batteryState = [battIndex]
    dayTime = nowTime
    for timeIndex in range(0, MaxTime):
        env.close(battIndex, timeIndex)
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
        extra = - policy[i] + supply[i] + demand[i] # because we convert 20KWh to 200 batteryIndex
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
        # (value, zone) = pc.energyValue(dayTime, buySell[timeIndex], timeIndex)
        value=buySell[timeIndex]*priceofelectricity[timeIndex]/EnergySample
        zoneList.append(Zone[timeIndex])
        cost = value + cost
        costList.append(cost)
        dayTime = dayTime + relativedelta(minutes=SampleTime)
    return (costList, zoneList)


# state = env.reset()
# batteryIndexforday=[]
# index=[]
# actionforday=[]
# batteryIndex,_=state
# env.close(batteryIndex,0)
# r=0
# re=[]
# for i in range(0,MaxTime):
#     index.append(i)
#     bestValue=-1000000
#
#
#     action = realactioncalculation(batteryIndex, i)
#
#
#     # print(action)
#     for j in range(0, len(action)):
#         # print(action[j])
#         nextstate, reward, done, info = env.step(action[j])
#         # print(batteryIndex,action[j],i)
#         newBatteryindex, newtime = nextstate
#         # print(batteryIndex,time,newBatteryindex,newtime,action[j])
#         value = reward + gama * v[int(newBatteryindex)][int(newtime)]
#         if value > bestValue:
#             bestValue = value
#             nBatteryIndex = newBatteryindex
#             nTime = newtime
#             a = action[j]
#             nreward = reward
#             # gym.state=state
#
#     r+=nreward
#     re.append(r)
#     print(batteryIndex,a,i)
#     batteryIndexforday.append(batteryIndex)
#     actionforday.append(a)
#     batteryIndex=nBatteryIndex
#     env.close(nBatteryIndex, i+1)

# for i in range(0,len(demand)):
#     demand[i]=-demand[i]
#
# f, (ax1, ax2,ax3, ax4) = plt.subplots(4, 1, sharex='col', sharey='row')
#
# ax2.bar(index,batteryIndexforday)
#
# ax3.bar(index,actionforday)
#
# barS=ax1.bar(index,solar)
#
# barD=ax1.bar(index,demand)
# ax1.set_ylabel('KW hour')
# barB=ax2.set_ylabel('KW hour')
# ax3.set_ylabel('KW hour')
# ax4.set_ylabel('dollar')
# ax4.set_xlabel('time')
# ax4.plot(index,re)
#
# ax1.set_title('In/Out Power')
# ax1.legend([barS[0], barD[0]], ['Supply', 'Demand'], loc=1)
#
# ax2.set_title('Battery Status')
# ax3.set_title('Action Taken')
# ax4.set_title('Operating Cost')
# # ax2.legend([barB[0]], ['Battery Index'], loc=1)
# plt.show()
# # print(actioncalculation(100,0))


def optimizer(sampletime=15,batterypanalty=0.01,numberOfhours=1*24,gamma=1,maxsolar=40,maxload=30,batterymaxenergy=20,energysample=10):
    global Supply, Demand, Vtable,priceofelectricity,Zone
    utc = datetime.today()
    timezone = pytz.timezone('US/Mountain')
    nowTime = timezone.localize(utc).replace(minute=0, second=0, microsecond=0)
    initialization(sampletime=sampletime,batterypanalty=batterypanalty,numberOfhours=numberOfhours,gamma=gamma,maxsolar=maxsolar,maxload=maxload,batterymaxenergy=batterymaxenergy,energysample=energysample)
    data.calculatesupplyanddemand(nowTime=nowTime, MaxTime=MaxTime, sampleTime=SampleTime,MaxSolar=MaxSolar,MaxLoad=MaxLoad)


    Supply,Demand,priceofelectricity,Zone= load.supply_lodecalculation(EnergySample=EnergySample,HourSample=HourSample)



    Vtable = valueIteration(nowTime)

    battIndex = MaxBattery//4

    (policy, batteryState) = computePolicy(Vtable, battIndex, nowTime)

    (buyEnergy, sellEnergy) = computeBuySell(policy, Supply, Demand)

    buySellList = [buyEnergy[i] + sellEnergy[i] for i in range(0, len(buyEnergy))]

    (costList, zoneList) = computeCostList(buySellList, nowTime)
    buyAction = []
    sellAction = []
    for i in range(0, len(policy)):
        if policy[i] > 0:
            buyAction.append(policy[i])
            sellAction.append(0)
        else:
            sellAction.append(policy[i])
            buyAction.append(0)




    # dis.graphVfunction(Vtable, batteryState, SampleTime)

    # print((len(batteryState)))
    # print (batteryState)
    # print((len(buyEnergy)))
    # print (buyEnergy)
    # print(Vtable)
    dis.graphMicroGrid(batteryState[:-1], buyEnergy=buyEnergy, sellEnergy=sellEnergy,
                       supply=Supply, demand=Demand,
                       sampleTime=SampleTime, nowDayTime=nowTime,
                       costList=costList, zoneList=zoneList, buyactionList=buyAction, sellactionList=sellAction,
                       )

    return costList[len(costList) - 1]


            # print Vtable
    # printV(Vtable)
    # plt.bar(np.arange(len(policy)),
    #         [po0.25,color='b',linewidth=0,antialiased = True)
    # plt.bar(np.arange(len(buyEnergy)),
    #         [policy[i] for i in range(0, len(policy))], alpha=0.25,color='g',linewidth=0,antialiased = True)
    # plt.bar(np.arange(len(sellEnergy)),
    #         [policy[i] for i in range(0, len(policy))], alpha=0.25,color='r',linewidth=0,antialiased = True)


# optimizer()
