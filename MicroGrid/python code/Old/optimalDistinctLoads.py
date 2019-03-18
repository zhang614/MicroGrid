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

# S[i] is the supply of watts available from solar
# D[i] is the required demand in watts
# 0<i<n, where n = 24*60/5 (5 min intervals)
sampleTime = 20                       # in minutes, connot be greater than one hour
startHour = 0                         # hour in day when start analysis 
numberOfHours = 2*24               # hours can be multi day
maxTime = numberOfHours*60/sampleTime # number of sampleTime minute intervals
# SUPPLY DEMAND
S = data.calculateSupply(sampleTime, startHour, numberOfHours, 6*310)

#HOME LIST OF LOADS
#loads.dryerMachine,
home = [loads.washingMachine, loads.dryerMachine, loads.lightsEarly,
        loads.lightsLate, loads.fridge, loads.kettle, loads.coffeeMaker] #, loads.airConditioner] #, loads.coffeeMaker,
home = [loads.dryerMachine,loads.draw,loads.lightsEarly, loads.lightsLate, loads.fridge]#, loads.kettle, loads.coffeeMaker, loads.draw]#loads.lightsEarly, loads.lightsLate]#, loads.washingMachine] #, loads.draw]
D = data.calculateDemand(sampleTime, startHour, numberOfHours, home)
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
    #return based on how much energy is in the battery
    if batteryE < batteryTarget:
        return batteryTarget - batteryE
    else: return batteryTarget - batteryE

#optimal solutions
eBattery = []#array of energy in the battery
usedSolar = [] #array of solar energy used (in bat or load)
usedGrid = [] #array of grid power used
sellEnergy = [] #array of sellEnergy power

#cache
cache = []# a 2D array of solutions, -1 means dont know
batteryAction = [] # policy: action with battery
# initial call is t=0, batteryE is the initial energy in battery
def runOptimal(batteryE):
    # Current energy in the battery
    global cache, batteryAction, usedGrid, batteryTarget, cacheDivide, discount
    batteryTarget = batt.noloadEnergy #batteryE
    # a 2D array of solutions, -1 means dont know
    cacheDivide = 10 #reduce the resolution of the KWH axis
    discount = 0.99 #future rewards are discounted
    cache = -1*np.ones((maxTime+1, batt.maxEnergy/cacheDivide+1))
    # for each state, + into bat or - from bat
    batteryAction = np.zeros((maxTime+1, batt.maxEnergy/cacheDivide+1))
    # Do the optimization
    best = Optimal(0, batteryE, batteryE < batt.noloadEnergy)
    # fills in the battery action policy and dependent variables
    traceback(batteryE)
    dis.graphTimeSequence(eBattery, D, S, sellEnergy, usedGrid,sampleTime,str(batteryE) +'_Optimal')#, sellEnergy, usedGrid)
    return best

def Optimal(t, batteryE, chargeOnly=False):
    #print(str(t) + "   " + str(batteryE))
    #energy is in kwh 
    global cache, cacheDivide
    global minEnergy
    global maxTime, batteryTarget
    if t > maxTime: #terminate
        return -1*batteryE #terminalGoalScore(batteryE, batteryTarget) #math.fabs
    batteryKey = int(batteryE/cacheDivide)
    hour = t*60/sampleTime%24
    if cache[t, batteryKey] != -1: #already have solution
        #print("OUT cache["+str(t)+","+str(batteryKey)+"]=" + str(cache[t, batteryKey]))
        return cache[t, batteryKey]
    netPower = int(S[t] + D[t])
    if netPower == 0:
        batteryAction[t, batteryKey] = 0
        cache[t, batteryKey] = discount*Optimal(t+1, batteryE, chargeOnly)
        return cache[t, batteryKey]
    # current solar exceeds demand, put some into battery
    if netPower > 0:
        #print "More solar"
        netEnergy = data.toWH(netPower,sampleTime)
        maxBattPower = data.toW(batt.maxEnergy - batteryE,sampleTime)
        # what is the max I can put in the battery?
        maxInBatteryP = min(min(netPower,loads.chargeRate(batteryE)),maxBattPower)
        maxInBatteryE = data.toWH(maxInBatteryP,sampleTime)
        wastedPower = netPower-maxInBatteryP #postive is no good
        #print wastedPower
        reward =  wastedPower + discount*Optimal(t+1, batteryE+maxInBatteryE, chargeOnly)
        cache[t, batteryKey] = reward
        batteryAction[t, batteryKey] = maxInBatteryE
        return cache[t, batteryKey]
    # current solar is not enough
    else: #netPower < or = 0
        #pull energy from the BATTERY and/or GRID
        bestSolution = 99999999 #best solution Grid is bad
        availableInBattery = data.toW(batteryE-batt.minEnergy,sampleTime)
        maxOutBattery = int(max(max(netPower, loads.drawRate(batteryE)),-1*availableInBattery)) #max of negatives
        # smallest number (one nearest to 0)
        #print "maxbat="+str(maxOutBattery)
        bestBattery = 0 #best battery action
        #print("max out bat="+str(maxOutBattery))
        for changeBattery in range(max(netPower,maxOutBattery), 0): #count up from netpower (negative) to 0
            #changeBattery is negative to pull out
            if not (changeBattery % cacheDivide) == 0:
                continue
##            if batteryE+data.toWH(changeBattery) < batt.minEnergy:
##                continue
            gridPower = -1*netPower + changeBattery #is negative
            # grid power is bad
##            if t==0:
##                print("gridPower="+str(gridPower)+" changeBattery="+str(changeBattery))
            restOfSolution = discount*Optimal(t+1, batteryE+data.toWH(changeBattery,sampleTime), chargeOnly)
#            print "t="+str(t)+" recieved back="+str(restOfSolution)
            solution = data.toWH(gridPower,sampleTime) + restOfSolution
##            print("t="+str(t)+", returned Score="+str(grid))
##            # if draw rate is less than power, will fail to service
##            if netPower < loads.drawRate(batteryE): #both negative
##                fail = -1*netPower + loads.drawRate(batteryE)
##            else: fail = 0
            #print(grid)
            #print(minGrid)
            if solution < bestSolution:
##                if t==0:
##                    print("new min="+str(grid)+" changeBattery="+str(changeBattery))
                bestSolution = solution
                bestBattery = data.toWH(changeBattery,sampleTime)
        cache[t, batteryKey] = bestSolution
##        print("best Bat="+str(bestBattery))
##        print("IN cache["+str(t)+","+str(batteryKey)+"]=" + str(cache[t, batteryKey]))
        batteryAction[t, batteryKey] = bestBattery
##        print(str(t) + "   " + str(minGrid) + "   " + str(bestBattery))
        return bestSolution

def traceback(batteryE):
    # takes the initial battery energy and traces through the solution cache
    global eBattery, usedSolar, usedGrid, sellEnergy
    eBattery = np.zeros(maxTime+1) #array of energy in the battery
    usedSolar = np.zeros(maxTime+1) #array of solar energy used (in bat or load)
    usedGrid = np.zeros(maxTime+1) #array of grid power used
    sellEnergy = np.zeros(maxTime+1) #array of sellEnergy solar energy
    scanSolutions(0, batteryE)
    scanBattery(0, batteryE)
    

def scanSolutions(time, batteryE):
    #solution arrays are indexed at resolution determined by cacheDivide
    global eBattery, usedSolar, usedGrid, sellEnergy
    print batteryE
    if time <= maxTime:
        batteryKey = int(batteryE/cacheDivide)
        eBattery[time] = batteryE
        batE = batteryAction[time, batteryKey] #action for battery in float AH
        # bat <0 draw, bat > 0 charge
        netPower = S[time] + D[time] #+ more solar
        if netPower > 0: #more solar
            sellEnergy[time] = data.toW(batE,sampleTime)-netPower 
            usedSolar[time] = batE
            usedGrid[time] = 0
        else:
            usedSolar[time] = S[time]
            usedGrid[time] = netPower-data.toW(batE,sampleTime)
        #print(str(time) + "   " + str(usedGrid[time]) + "   " + str(bat))
        scanSolutions(time+1, batteryE + batE)

def scanBattery(time, batteryE):
    #solution arrays are indexed at resolution determined by cacheDivide
    global eBattery, usedSolar, usedGrid, sellEnergy 
    if time <= maxTime:
        batteryKey = int(batteryE/cacheDivide)
        eBattery[time] = batteryE
        batE = batteryAction[time, batteryKey] #action for battery in float AH
        print "bat action="+str(batE)
        scanBattery(time+1, batteryE + batE)

        
##for i in range(0, batt.maxEnergy+1):
##    charge = loads.chargeRate(i)
##    print(i)
##    print i+data.toWH(charge)
##    
for example in [int(batt.maxEnergy*.4)]: #range(batteryAhMin,batteryAh+1-batteryAh/6,batteryAh/20):
    wasteAI= runOptimal(example)
    #wasteGreedy = runGreedy(i)
    
    AIText = " "
##    if wasteGreedy >= 100000:
##        GreedyText = "(Bad Batt)"
##        wasteGreedy = wasteGreedy - 100000
##    else: GreedyText = " "
    if wasteAI > 100000: 
        AIText += "(Bad Batt)"
    else: AIText = " "
    print("bat="+str(example)+ " AI=" +AIText + str(wasteAI))# +"   Greedy="+GreedyText+str(wasteGreedy)
    print(eBattery)

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

    ##
##def runGreedy(batteryE):
##    global eBattery, sellEnergy, usedGrid
##    eBattery = np.zeros(maxTime+1) #array of energy in the battery
##    sellEnergy = np.zeros(maxTime+1)
##    usedGrid = np.zeros(maxTime+1)
##    best = Greedy(0,batteryE, batteryE < batt.noloadEnergy)
##    dis.graphTimeSequence(eBattery, D, S, sellEnergy, usedGrid, str(batteryE) +'_Greedy')#, sellEnergy, usedGrid)
##    return best


##def Greedy(t, batteryE, chargeOnly = False):
##    global sellEnergy
##    #print("t="+str(t)+" bat="+str(batteryE))
##    #fixed policy, service the loads with solar and battery,
##    #if extra solar, then put in battery
##    if t >= maxTime: #terminate
##        return 0 #terminalGoalScore(batteryE, batteryTarget)
##    eBattery[t] = batteryE
##    netPower = S[t] + D[t]
##    # ONLY CHARGE BATTERY
##    if chargeOnly and (batteryE < batt.noloadEnergy): # can only charge the battery
##        #change battery is in watts, convert to AmpH to put in battery, data.toWH(
##        changeBattery =  loads.chargeRate(batteryE) #min(S[t], loads.chargeRate(batteryE))
##        if changeBattery < S[t]: #waste
##            waste = changeBattery - netPower
##            usedGrid[t] = 0
##        else:
##            waste = 0
##            usedGrid[t] = (D[t] - changeBattery) + S[t] #negative
##        sellEnergy[t] = waste
##        return waste + Greedy(t+1, batteryE+data.toWH(changeBattery), chargeOnly)
##    if chargeOnly:
##        chargeOnly = False
##    # BATTERY RUN DOWN
##    if batteryE <= batt.minEnergy: #over drawn
##        #print("Greedy ran the battery down")
##        return Greedy(t, batteryE, True)
##    # NEED BATTERY
##    if netPower < 0: #need the battery
##        changeBattery = max(netPower, loads.drawRate(batteryE))        
##        usedGrid[t] = netPower + -1*changeBattery #both are negative
##        return Greedy(t+1, batteryE+data.toWH(changeBattery), chargeOnly)
##    # if draw rate is less than power, will fail to service
####    if netPower < loads.drawRate(batteryE): #both negative
####        fail = -1*netPower + loads.drawRate(batteryE)
####    else: fail = 0
##    #EXTRA SOLAR
##    changeBattery =  min(netPower, loads.chargeRate(batteryE))
##    usedGrid[t] = 0
##    if changeBattery < netPower: #waste
##        waste = changeBattery - netPower
##        sellEnergy[t] = waste
##    else:
##        waste = 0
##    #print(t)
##    #print(changeBattery)
##    return waste + Greedy(t+1, batteryE+data.toWH(changeBattery), chargeOnly)

