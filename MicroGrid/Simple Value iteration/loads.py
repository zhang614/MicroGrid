from collections import namedtuple

storageBattery = namedtuple("Battery", "voltage maxAmpsIn maxAmpsOut maxEnergy minEnergy noloadEnergy trickle")
#                           "voltage AmpH/H AmpH/H AmpH AmpH AmpH AmpH/H"

batteryV = 48
batteryAH = 400 #Ah
batteryWH = batteryAH * batteryV

#                     "voltage  maxAmpsIn    maxAmpsOut")
batt = storageBattery(batteryV, int(100),    int(300), #
                      #maxEnergy minEnergy    noloadEnergy         trickle
                      batteryWH, batteryWH*.3, int(batteryWH*0), int(batteryWH*0.05))

def chargeRate(batteryE):
    # Input is WH Energy
    # positive
    # must be in units watts
    # MODEL, RATE REDUCES AS A FUNCTION OF CHARGE
    #full = (batteryE-batt.minEnergy)*1.0/(batt.maxEnergy-batt.minEnergy)
    #return int(batt.voltage * (1.0-full)* batt.maxAmpsIn)
    # MODEL: CONSTANT
    return int(batt.voltage * batt.maxAmpsIn)


def drawRate(batteryE):
    # return Negative
    # must be in units of watts
    if batteryE < batt.minEnergy:
        return 0
    # MODEL, RATE REDUCES AS A FUNCTION OF CHARGE
    #full = (batteryE-batt.minEnergy)*1.0/(batt.maxEnergy-batt.minEnergy)
    #return int(-1*batt.voltage * full * batt.maxAmpsOut)
    return -1*int(batt.voltage * batt.maxAmpsOut)

# convert
#Battery characteristics

                         
#time units are minutes, duration, wavelength,
#start end are in hours
periodicLoad = namedtuple("Pload", "power duration wavelength")
# frequency is how many per hour
intermitentLoad = namedtuple("Iload", "power duration frequency start end")
# simple constant load
constantLoad = namedtuple("Cload", "power")
#The newly created type can be used like this:
constant = constantLoad(0)
periodic = periodicLoad(0,0,0)
intermitent = intermitentLoad(0,0,0,0,0)
# duration is in minutes, wavelength is in minutes

#HOME LOADS POSSIBLE
draw = constantLoad(-10)
fridge = periodicLoad(-100, 3, 120)
airConditioner = intermitentLoad(-500, 3, 100, 13, 18)
coffeeMaker = periodicLoad(-50, 2, 60)
kettle = intermitentLoad(-200, 5, 20, 6, 8)
lightsEarly = intermitentLoad(-50, 3, 10, 6, 9)
lightsLate = intermitentLoad(-50, 3, 2, 17, 22)
washingMachine = intermitentLoad(-100, 60, 18, 12, 17)
dryerMachine = intermitentLoad(-100, 20, 10, 12, 14)

#Or you can use named arguments:
#m = MyStruct(field1 = "foo", field2 = "bar", field3 = "baz")

##for i in range(0,300):
##    watt = chargeRate(i) #drawRate(i)
##    aH = toAmpH(watt)
##    print(str(i) + "  " + str(watt) + "    " + str(aH))
##
    
#print(chargeRate(250))
#print(drawRate(250))


