import data
import math
import numpy as np
import display as dis
import math
global eBattery, usedSolar, usedGrid, wasted

# S[i] is the supply of watts available
# D[i] is the required demand
# 0<i<n, where n = 24*60/5 (5 min intervals)
sampleTime = 5 #in minutes, connot be greater than one hour
maxTime = 24*60/sampleTime             # number of minute intervals
# SUPPLY DEMAND
S = data.calculateSupply(maxTime, 15)
D = data.calculateDemand(maxTime)
# BATTERY
batteryAh = 1000                    # full
batteryAhMin = batteryAh/2          # when empty
batteryAhChargeOnly = 2*batteryAh/3 # must only charge

# ENERGY
maxEnergy = batteryAh * 60/sampleTime # in Watt * units of time interval
minEnergy = 0 #maxEnergy / 2                 # battery must not get lower than this
batteryTarget = 60 #battery charge level at the end

#Battery characteristics
def chargeRate(batteryE):
    #100Ah is 10A
    return min(batteryAh-batteryE, batteryAh/10)

def drawRate(batteryE):
    #100Ah is 20A
    # cannot go below batteryAhMin
    remaining = batteryE - batteryAhMin
    if remaining < 0:
        return 0
    else:
        return -1*min(batteryE, min(batteryAh/5, remaining))

def terminalGoalScore(batteryE, batteryTarget):
    #return 0
    if batteryE < batteryTarget:
        return 100000000
    else: return 0

#optimal solutions
eBattery = []#array of energy in the battery
usedSolar = [] #array of solar energy used (in bat or load)
usedGrid = [] #array of grid power used
wasted = [] #array of wasted power

#cache
cache = []# a 2D array of solutions, -1 means dont know
batteryAction = []
# minimizes wasted solar energy
# initial call is t=0, batteryE is the initial energy in battery
def runOptimal(batteryE):
    global cache, batteryAction, usedGrid, batteryTarget
    batteryTarget = batteryE
    # a 2D array of solutions, -1 means dont know
    cache = -1*np.ones((maxTime+2,maxEnergy+1))
    # for each state, + into bat or - from bat
    batteryAction = np.zeros((maxTime+2,maxEnergy+1))
    best = Optimal(0, batteryE)
    traceback(batteryE)
    dis.graphTimeSequence(eBattery, D, S, wasted, usedGrid, str(batteryE) +'_Optimal')#, wasted, usedGrid)
    return best

def runGreedy(batteryE):
    global eBattery, wasted, usedGrid
    eBattery = np.zeros(maxTime) #array of energy in the battery
    wasted = np.zeros(maxTime)
    usedGrid = np.zeros(maxTime)
    best = Greedy(0,batteryE)
    dis.graphTimeSequence(eBattery, D, S, wasted, usedGrid, str(batteryE) +'_Greedy')#, wasted, usedGrid)
    return best


def Greedy(t, batteryE, chargeOnly = False):
    global wasted
    #print("t="+str(t)+" bat="+str(batteryE))
    #fixed policy, service the loads with solar and battery,
    #if extra solar, then put in battery
    if t >= maxTime: #terminate
        return 0 #terminalGoalScore(batteryE, batteryTarget)
    eBattery[t] = batteryE
    netPower = S[t] + D[t]
    # ONLY CHARGE BATTERY
    if chargeOnly and (batteryE < batteryAhChargeOnly): # can only charge the battery
        changeBattery =  min(S[t], chargeRate(batteryE))
        if changeBattery < S[t]: #waste
            waste = changeBattery - netPower
        else: waste = 0
        wasted[t] = waste
        usedGrid[t] = D[t]
        return waste + Greedy(t+1, batteryE+changeBattery)
    if chargeOnly:
        chargeOnly = False
    # BATTERY RUN DOWN
    if batteryE <= batteryAhMin: #over drawn
        #print("Greedy ran the battery down")
        chargeOnly = True
        return Greedy(t+1, batteryE, chargeOnly)
    # NEED BATTERY
    if netPower < 0: #need the battery
        changeBattery = max(netPower, drawRate(batteryE))        
        usedGrid[t] = netPower + -1*changeBattery #both are negative
        return Greedy(t+1, batteryE+changeBattery, chargeOnly)
    # if draw rate is less than power, will fail to service
##    if netPower < drawRate(batteryE): #both negative
##        fail = -1*netPower + drawRate(batteryE)
##    else: fail = 0
    #EXTRA SOLAR
    changeBattery =  min(netPower, chargeRate(batteryE))
    usedGrid[t] = 0
    if changeBattery < netPower: #waste
        waste = changeBattery - netPower
        wasted[t] = waste
    else:
        waste = 0
    return waste + Greedy(t+1, batteryE+changeBattery, chargeOnly)

def Optimal(t, batteryE):
    #print(str(t) + "   " + str(batteryE))
    global cache, batteryAh
    global minEnergy
    global maxTime, batteryTarget
    if batteryE < batteryAhMin: #over drawn
        return +100000000 #so solution never taken
    if t >= maxTime: #terminate
        #is there a target end energy to have in the battery?
        # below is positive (like waste)
        return terminalGoalScore(batteryE, batteryTarget) #math.fabs
    if cache[t, batteryE] != -1: #already have solution
        return cache[t, batteryE]
    netPower = S[t] + D[t]
    # current solar exceeds demand, put some into battery
    if netPower > 0:
        minWaste = 10000000
        # only consider solar energy into battery
        bestBattery=0
        for changeBattery in range(0, 1+int(min(netPower, chargeRate(batteryE)))):
            remainingSolar = netPower-changeBattery
            if remainingSolar < 0:
                continue
            if changeBattery + batteryE > batteryAh:
                # cannot use all the solar! low demand and full battery
                waste = remainingSolar + Optimal(t+1, batteryE) #battery stays the same
            else:
                waste = remainingSolar + Optimal(t+1, batteryE + changeBattery)
            if waste < minWaste:
                minWaste = waste
                bestBattery = changeBattery
        cache[t, batteryE] = minWaste
        batteryAction[t, batteryE] = bestBattery
        #print(batteryAction)
        return minWaste
    # current solar is not enough
    else:
        #pull energy from the battery 
        minWaste = 1000000
        # - change is pull, + change is charge the bat
        # drawRate negative is pull from battery, positive is charge
        maxInBattery = 0 #int(min(S[t], chargeRate(batteryE)))
        # can cover the load from solar + additional battery
        netPower = D[t]+S[t]
        maxOutBattery = int(max(netPower, drawRate(batteryE))) #max of negatives
        bestBattery = 0
        for changeBattery in range(maxOutBattery, 1):
            availablePower = S[t]+ -1*changeBattery #changeBattery is negative to pull out
            #print(changeBattery, availablePower)
            if availablePower+D[t] >0: #dont need this much
                continue
            gridPower = -1*(availablePower + D[t])
            # grid power is bad
            waste = gridPower + Optimal(t+1, batteryE + changeBattery)
##            # if draw rate is less than power, will fail to service
##            if netPower < drawRate(batteryE): #both negative
##                fail = -1*netPower + drawRate(batteryE)
##            else: fail = 0
            if waste < minWaste:
                minWaste = waste
                bestBattery = changeBattery

        cache[t, batteryE] = minWaste
        batteryAction[t, batteryE] = bestBattery
        return minWaste

def traceback(batteryE):
    # takes the initial battery energy and traces through the solution cache
    global eBattery, usedSolar, usedGrid, wasted
    eBattery = np.zeros(maxTime+2) #array of energy in the battery
    usedSolar = np.zeros(maxTime+2) #array of solar energy used (in bat or load)
    usedGrid = np.zeros(maxTime+2) #array of grid power used
    wasted = np.zeros(maxTime+2) #array of wasted solar energy
    scanSolutions(0, batteryE)
    

def scanSolutions(time, batteryE):
    global eBattery, usedSolar, usedGrid, wasted 
    if time < maxTime:
        eBattery[time] = batteryE
        bat = batteryAction[time, batteryE] #action for battery
        diff = S[time] + D[time] #+ more solar
        if diff > 0: #more solar
            wasted[time] = bat - diff 
            usedSolar[time] = S[time] - wasted[time]
            usedGrid[time] = 0
        else:
            usedSolar[time] = S[time]
            usedGrid[time] = D[time] - bat + S[time]
        scanSolutions(time+1, batteryE+bat)

for i in range(batteryAhMin,batteryAh+1-batteryAh/6,batteryAh/20):
    wasteAI= runOptimal(i)
    wasteGreedy = runGreedy(i)
    
    AIText = " "
    if wasteGreedy >= 1000:
        GreedyText = "(Bad Batt)"
        wasteGreedy = wasteGreedy - 1000
    else: GreedyText = " "
    if wasteAI > 1000: 
        AIText += "(Bad Batt)"
    else: AIText = " "
    print("bat="+str(i)+ " AI=" +AIText + str(wasteAI)+"   Greedy="+GreedyText+str(wasteGreedy))
    #print(eBattery)

##run(60)
##print(D)
##print(S)
##print(eBattery)
##print(wasted)
##print(usedSolar)
##print(usedGrid)

#runGreedy(60)
##batteryE = 650
##print("Greedy = "+str(runGreedy(650)))
##dis.graphTimeSequence(eBattery, D, S, wasted, str(batteryE) +'_Greedy')
##
##print("Optimal = "+str(runOptimal(650)))
##dis.graphTimeSequence(eBattery, D, S, wasted, str(batteryE) +'_Optimal')

#print(wasted)
##print(D)
##print(S)
##print(eBattery)
#print(wasted)
##print(usedSolar)
##print(usedGrid)
