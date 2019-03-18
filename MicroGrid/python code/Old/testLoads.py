import data
import loads

# D[i] is the required demand in watts
# 0<i<n, where n = 24*60/5 (5 min intervals)
sampleTime = 5 #in minutes, connot be greater than one hour
numberOfHours = 24 #can be multi day
maxTime = numberOfHours*60/sampleTime             # number of sampleTime minute intervals

#HOME LIST OF LOADS
#loads.dryerMachine,
#list of loads in the home
home = [loads.washingMachine, loads.dryerMachine, loads.lightsEarly, loads.lightsLate, loads.fridge, loads.kettle, loads.coffeeMaker] #, loads.airConditioner] #, loads.coffeeMaker,
home = [loads.fridge, loads.lightsEarly, loads.lightsLate] #, loads.draw]
D = data.calculateDemand(sampleTime, numberOfHours, home)

print D
