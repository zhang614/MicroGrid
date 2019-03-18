#import D,S from data
import math
import numpy as np
global eBattery, usedSolar, usedGrid, wasted

# S[i] is the supply of watts available
# D[i] is the required demand
# 0<i<n, where n = 24*60/5 (5 min intervals)

batteryAh = 100
minuteInterval = 60
maxTime = 24*60/minuteInterval             # number of minute intervals
maxEnergy = batteryAh * 60/minuteInterval # in Watt * units of time interval
minEnergy = maxEnergy / 2                 # battery must not get lower than this
batteryTarget = 50 #battery charge level at the end

#Setup problem to solve

##S = [0]*(maxTime+2) #supply is positive
##S[0] = 5
##S[10]=8
##D = [0]*(maxTime+2) #demand is negative
##D[0] = -6
##D[5] = -3
##D[20]= -8

#loads and Supply need to extend to maxTime+2 because we want the terminal time
D= np.r_[[0]*8,[-10]*6,[0]*8,[-3]*4]
S= np.r_[[5]*3,[0]*2,[0]*9,[3]*6,[2]*5,[10]*1]
#Battery characteristics
def chargeRate(batteryE):
    #100Ah is 10A
    return min(batteryAh-batteryE, batteryAh/1)

def drawRate(batteryE):
    #100Ah is 20A
    return -1*min(batteryE, batteryAh/1)

def terminalGoalScore(batteryE, batteryTarget):
    return (batteryE - batteryTarget) #math.fabs

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
def run(batteryE):
    global cache, batteryAction
    # a 2D array of solutions, -1 means dont know
    cache = -1*np.ones((maxTime+2,maxEnergy+1))
    # for each state, + into bat or - from bat
    batteryAction = np.zeros((maxTime+2,maxEnergy+1))
    best = Optimal(0, batteryE)
    traceback(batteryE)
    return best

def runGreedy(batteryE):
    global eBattery
    eBattery = np.zeros(maxTime+2) #array of energy in the battery
    return Greedy(0,batteryE)


def Greedy(t, batteryE):
    #print("t="+str(t)+" bat="+str(batteryE))
    eBattery[t] = batteryE
    #fixed policy, service the loads with solar and battery,
    #if extra solar, then put in battery
    if batteryE < minEnergy: #over drawn
        #print("Greedy ran the battery down")
        return +1000 #so solution never taken
    if t > maxTime: #terminate
        return terminalGoalScore(batteryE, batteryTarget)
    netPower = S[t] + D[t]
    if netPower < 0: #need the battery
        return Greedy(t+1, batteryE+max(netPower, drawRate(batteryE)))
    # if draw rate is less than power, will fail to service
    if netPower < drawRate(batteryE): #both negative
        fail = -1*netPower + drawRate(batteryE)
    else: fail = 0
    #extra solar beyond charging up the batteries
    inBattery =  min(netPower, chargeRate(batteryE))
    if inBattery < netPower: #waste
        waste = netPower - inBattery
    else:
        waste = 0
    return waste  + Greedy(t+1, batteryE+inBattery)

def Optimal(t, batteryE):
    #print(str(t) + "   " + str(batteryE))
    global cache
    global minEnergy
    global maxTime, batteryTarget
    if batteryE < minEnergy: #over drawn
        return +1000 #so solution never taken
    if t > maxTime: #terminate
        #is there a target end energy to have in the battery?
        # below is positive (like waste)
        return terminalGoalScore(batteryE, batteryTarget) #math.fabs
    if cache[t, batteryE] != -1: #already have solution
        return cache[t, batteryE]
    # current solar exceeds demand, put some into battery
    if S[t]+D[t]>0:
        minWaste = 1000
        # only consider solar energy into battery
        bestBattery=0
        for changeBattery in range(0, 1+min(S[t], chargeRate(batteryE))):
            remainingSolar = S[t]-changeBattery
            if remainingSolar + D[t] > 0:
                # cannot use the solar! low demand and full battery
                waste = (remainingSolar + D[t]) + Optimal(t+1, batteryE + changeBattery)
            else:
                waste = Optimal(t+1, batteryE + changeBattery)
            if waste < minWaste:
                minWaste = waste
                bestBattery = changeBattery
        cache[t, batteryE] = minWaste
        batteryAction[t, batteryE] = bestBattery
        return minWaste
    # current solar is not enough
    else:
        #pull or push energy from/to the battery 
        minWaste = 1000
        # - change is pull, + change is charge the bat
        # drawRate negative is pull from battery, positive is charge
        maxInBattery = min(S[t], chargeRate(batteryE))
        # can cover the load from solar + additional battery
        netPower = D[t]+S[t]
        maxOutBattery = max(netPower, drawRate(batteryE)) #max of negatives
        bestBattery = 0
        for changeBattery in range(maxOutBattery, 1+maxInBattery):
            waste = Optimal(t+1, batteryE + changeBattery)
            # if draw rate is less than power, will fail to service
            if netPower < drawRate(batteryE): #both negative
                fail = -1*netPower + drawRate(batteryE)
            else: fail = 0
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
    if time <= maxTime+1:
        eBattery[time] = batteryE
        bat = batteryAction[time, batteryE] #action for battery
        diff = S[time] + D[time] #+ more solar
        if diff > 0: #more solar
            wasted[time] = diff - bat
            usedSolar[time] = S[time] - wasted[time]
        else:
            usedSolar[time] = S[time]
            usedGrid[time] = -1*D[time] + bat - S[time]
        scanSolutions(time+1, batteryE+bat)

for i in range(minEnergy,maxEnergy+1):
    wasteAI= run(i)
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

run(20)
print(D)
print(S)
print(eBattery)
print(wasted)
print(usedSolar)
print(usedGrid)
