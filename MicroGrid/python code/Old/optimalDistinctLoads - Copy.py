import data
import math
import numpy as np
import display as dis
import math
import loads
import arrow
global eBattery, usedSolar, usedGrid, sellEnergy, batteryAction

# time/price electricity
# https://www.nvenergy.com/home/paymentbilling/timeofuse.cfm

# S[i] is the supply of watts available
# D[i] is the required demand in watts
# 0<i<n, where n = 24*60/5 (5 min intervals)
sampleTime = 5 #in minutes, connot be greater than one hour
numberOfHours = 24 #can be multi day
maxTime = numberOfHours*60/sampleTime             # number of sampleTime minute intervals
# SUPPLY DEMAND
S = data.calculateSupply(sampleTime, numberOfHours, 9*310)

#HOME LIST OF LOADS
#loads.dryerMachine,
home = [loads.washingMachine, loads.dryerMachine, loads.lightsEarly, loads.lightsLate, loads.fridge, loads.kettle, loads.coffeeMaker] #, loads.airConditioner] #, loads.coffeeMaker,
home = [loads.fridge, loads.lightsEarly, loads.lightsLate] #, loads.draw]
D = data.calculateDemand(sampleTime, numberOfHours, home)
# BATTERY
"Battery", "voltage maxAmpsIn maxAmpsOut maxEnergy minEnergy noloadEnergy"
batt = loads.batt

##batteryAh = 1000                    # full
##batteryAhMin = batteryAh/2          # when empty
##batteryAhChargeOnly = 6*batteryAh/10 # must only charge if less than

### ENERGY
##maxEnergy = batteryAh * 60/sampleTime # in Watt * units of time interval
##minEnergy = 0 #maxEnergy / 2                 # battery must not get lower than this
##batteryTarget = batteryAhChargeOnly #battery charge level at the end

def terminalGoalScore(batteryE, batteryTarget):
    #return 0
    if batteryE < batteryTarget:
        return 100000000
    else: return 0

#optimal solutions
eBattery = []#array of energy in the battery
usedSolar = [] #array of solar energy used (in bat or load)
usedGrid = [] #array of grid power used
sellEnergy = [] #array of sellEnergy power

#cache
cache = []# a 2D array of solutions, -1 means dont know
batteryAction = []
# minimizes sellEnergy solar energy
# initial call is t=0, batteryE is the initial energy in battery
def runOptimal(batteryE):
    # Current energy in the battery
    global cache, batteryAction, usedGrid, batteryTarget, cacheDivide
    batteryTarget = batt.noloadEnergy #batteryE
    # a 2D array of solutions, -1 means dont know
    cacheDivide = 100 #reduce the resolution of the KWH axis
    cache = -1*np.ones((maxTime+1, batt.maxEnergy/cacheDivide+1))
    # for each state, + into bat or - from bat
    batteryAction = np.zeros((maxTime+1, batt.maxEnergy/cacheDivide+1))
    # 
    best = Optimal(0, batteryE, batteryE < batt.noloadEnergy)
    # fills in the battery action policy and dependent variables
    traceback(batteryE)
    dis.graphTimeSequence(eBattery, D, S, sellEnergy, usedGrid, str(batteryE) +'_Optimal')#, sellEnergy, usedGrid)
    return best

def runGreedy(batteryE):
    global eBattery, sellEnergy, usedGrid
    eBattery = np.zeros(maxTime+1) #array of energy in the battery
    sellEnergy = np.zeros(maxTime+1)
    usedGrid = np.zeros(maxTime+1)
    best = Greedy(0,batteryE, batteryE < batt.noloadEnergy)
    dis.graphTimeSequence(eBattery, D, S, sellEnergy, usedGrid, str(batteryE) +'_Greedy')#, sellEnergy, usedGrid)
    return best


def Greedy(t, batteryE, chargeOnly = False):
    global sellEnergy
    #print("t="+str(t)+" bat="+str(batteryE))
    #fixed policy, service the loads with solar and battery,
    #if extra solar, then put in battery
    if t >= maxTime: #terminate
        return 0 #terminalGoalScore(batteryE, batteryTarget)
    eBattery[t] = batteryE
    netPower = S[t] + D[t]
    # ONLY CHARGE BATTERY
    if chargeOnly and (batteryE < batt.noloadEnergy): # can only charge the battery
        #change battery is in watts, convert to AmpH to put in battery, data.toWH(
        changeBattery =  loads.chargeRate(batteryE) #min(S[t], loads.chargeRate(batteryE))
        if changeBattery < S[t]: #waste
            waste = changeBattery - netPower
            usedGrid[t] = 0
        else:
            waste = 0
            usedGrid[t] = (D[t] - changeBattery) + S[t] #negative
        sellEnergy[t] = waste
        return waste + Greedy(t+1, batteryE+data.toWH(changeBattery), chargeOnly)
    if chargeOnly:
        chargeOnly = False
    # BATTERY RUN DOWN
    if batteryE <= batt.minEnergy: #over drawn
        #print("Greedy ran the battery down")
        return Greedy(t, batteryE, True)
    # NEED BATTERY
    if netPower < 0: #need the battery
        changeBattery = max(netPower, loads.drawRate(batteryE))        
        usedGrid[t] = netPower + -1*changeBattery #both are negative
        return Greedy(t+1, batteryE+data.toWH(changeBattery), chargeOnly)
    # if draw rate is less than power, will fail to service
##    if netPower < loads.drawRate(batteryE): #both negative
##        fail = -1*netPower + loads.drawRate(batteryE)
##    else: fail = 0
    #EXTRA SOLAR
    changeBattery =  min(netPower, loads.chargeRate(batteryE))
    usedGrid[t] = 0
    if changeBattery < netPower: #waste
        waste = changeBattery - netPower
        sellEnergy[t] = waste
    else:
        waste = 0
    #print(t)
    #print(changeBattery)
    return waste + Greedy(t+1, batteryE+data.toWH(changeBattery), chargeOnly)

def Optimal(t, batteryE, chargeOnly=False):
    #print(str(t) + "   " + str(chargeOnly))
    global cache, cacheDivide
    global minEnergy
    global maxTime, batteryTarget
    if batteryE < batt.minEnergy: #over drawn
        #print("under")
        return +100000000 #so solution never taken
    if batteryE > batt.maxEnergy: #attempt to over fill
        #print("over")
        return +100000000
    if t > maxTime: #terminate
        #is there a target end energy to have in the battery?
        # below is positive (like waste)
        return 0 #terminalGoalScore(batteryE, batteryTarget) #math.fabs
    batteryKey = int(batteryE/cacheDivide)
    if cache[t, batteryKey] != -1: #already have solution
        #print("OUT cache["+str(t)+","+str(batteryKey)+"]=" + str(cache[t, batteryKey]))
        return cache[t, batteryKey]
    netPower = S[t] + D[t]
    # current solar exceeds demand, put some into battery
    if netPower > 0:
        minWaste = 90000000
        # only consider solar energy into battery
        bestBattery=0
        # all calculations are in watts
        for changeBattery in range(0, 1+int(min(netPower, loads.chargeRate(batteryE)))):
            # In battery from 0 to min of available solar, max can put in battery
            remainingSolar = netPower-changeBattery
            if remainingSolar < 0:
                continue
            #DEBUG remainingSolar
            #remainingSolar = 0
            if data.toWH(changeBattery) + batteryE > batt.maxEnergy:
                # cannot use all the solar! low demand and full battery
                waste = netPower + Optimal(t+1, batteryE, chargeOnly) #battery stays the same
            else:
                waste = remainingSolar + Optimal(t+1, batteryE + data.toWH(changeBattery), chargeOnly)
            if waste < minWaste:
                minWaste = waste
                bestBattery = data.toWH(changeBattery) #float
        cache[t, batteryKey] = minWaste
        #print("IN cache["+str(t)+","+str(batteryKey)+"]=" + str(cache[t, batteryKey]))
        batteryAction[t, batteryKey] = bestBattery
        #print(str(t) + "   " + str(bestBattery))
        return minWaste
    # current solar is not enough
    else:
        #pull energy from the BATTERY and/or GRID
        minGrid = 1111111000
        if t==0:
            print("net power="+str(netPower))
        # - change is pull, + change is charge the bat
        # drawRate negative is pull from battery, positive is charge
        maxInBattery = int(loads.chargeRate(batteryE))
        # can cover the load from solar + additional battery
        # all calculations in Watts
        # biggest negative number
        maxOutBattery = int(max(netPower, loads.drawRate(batteryE))) #max of negatives
        # smallest number (one nearest to 0)
        bestBattery = 0 #best battery action
        #print("max out bat="+str(maxOutBattery))
        for changeBattery in range(maxOutBattery, maxInBattery+1):
            #changeBattery is negative to pull out
            gridPower = -1*netPower + changeBattery
            # grid power is bad
##            if t==0:
##                print("gridPower="+str(gridPower)+" changeBattery="+str(changeBattery))
            grid = gridPower + Optimal(t+1, batteryE + data.toWH(changeBattery), chargeOnly)
##            # if draw rate is less than power, will fail to service
##            if netPower < loads.drawRate(batteryE): #both negative
##                fail = -1*netPower + loads.drawRate(batteryE)
##            else: fail = 0
            #print(grid)
            #print(minGrid)
            if grid < minGrid:
##                if t==0:
##                    print("new min="+str(grid)+" changeBattery="+str(changeBattery))
                minGrid = grid
                bestBattery = data.toWH(changeBattery)
        cache[t, batteryKey] = minGrid
##        print("best Bat="+str(bestBattery))
##        print("IN cache["+str(t)+","+str(batteryKey)+"]=" + str(cache[t, batteryKey]))
        batteryAction[t, batteryKey] = bestBattery
        #print(str(t) + "   " + str(minGrid) + "   " + str(bestBattery))
        return minGrid

def traceback(batteryE):
    # takes the initial battery energy and traces through the solution cache
    global eBattery, usedSolar, usedGrid, sellEnergy
    eBattery = np.zeros(maxTime+1) #array of energy in the battery
    usedSolar = np.zeros(maxTime+1) #array of solar energy used (in bat or load)
    usedGrid = np.zeros(maxTime+1) #array of grid power used
    sellEnergy = np.zeros(maxTime+1) #array of sellEnergy solar energy
    scanSolutions(0, batteryE)
    

def scanSolutions(time, batteryE):
    #solution arrays are indexed at resolution determined by cacheDivide
    global eBattery, usedSolar, usedGrid, sellEnergy 
    if time <= maxTime:
        batteryKey = int(batteryE/cacheDivide)
        eBattery[time] = batteryE
        batE = batteryAction[time, batteryKey] #action for battery in float AH
        # bat <0 draw, bat > 0 charge
        netPower = S[time] + D[time] #+ more solar
        if netPower > 0: #more solar
            sellEnergy[time] = data.toW(batE) - netPower 
            usedSolar[time] = S[time] - sellEnergy[time]
            usedGrid[time] = 0
        else:
            usedSolar[time] = S[time]
            usedGrid[time] = netPower-data.toW(batE)
        #print(str(time) + "   " + str(usedGrid[time]) + "   " + str(bat))
        scanSolutions(time+1, batteryE + batE)

##for i in range(0, batt.maxEnergy+1):
##    charge = loads.chargeRate(i)
##    print(i)
##    print i+data.toWH(charge)
##    
for i in [int(batt.maxEnergy*.6)]: #range(batteryAhMin,batteryAh+1-batteryAh/6,batteryAh/20):
    wasteAI= runOptimal(i)
    #wasteGreedy = runGreedy(i)
    
##    AIText = " "
##    if wasteGreedy >= 100000:
##        GreedyText = "(Bad Batt)"
##        wasteGreedy = wasteGreedy - 100000
##    else: GreedyText = " "
##    if wasteAI > 100000: 
##        AIText += "(Bad Batt)"
##    else: AIText = " "
##    print("bat="+str(i)+ " AI=" +AIText + str(wasteAI)+"   Greedy="+GreedyText+str(wasteGreedy))
    #print(eBattery)

##run(60)
##print(D)
##print(S)
##print(eBattery)
##print(sellEnergy)
##print(usedSolar)
##print(usedGrid)

#runGreedy(60)
##batteryE = 650
##print("Greedy = "+str(runGreedy(650)))
##dis.graphTimeSequence(eBattery, D, S, sellEnergy, str(batteryE) +'_Greedy')
##
##print("Optimal = "+str(runOptimal(650)))
##dis.graphTimeSequence(eBattery, D, S, sellEnergy, str(batteryE) +'_Optimal')

#print(sellEnergy)
##print(D)
##print(S)
##print(eBattery)
#print(sellEnergy)
##print(usedSolar)
##print(usedGrid)
