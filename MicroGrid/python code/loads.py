from collections import namedtuple

sampleTime = 5

storageBattery = namedtuple("Battery", "voltage maxAmpsIn maxAmpsOut maxEnergy minEnergy noloadEnergy trickle")
#                           "voltage AmpH/H AmpH/H AmpH AmpH AmpH AmpH/H"

batteryV = 48
batteryAH = 300  # Ah
batteryWH = batteryAH * 48

#                     "voltage  maxAmpsIn    maxAmpsOut")
batt = storageBattery(batteryV, int(20), int(100),  #
                      # maxEnergy minEnergy    noloadEnergy         trickle
                      batteryWH, batteryWH / 2, int(batteryWH * 0.6), int(batteryWH * 0.05))


def chargeRate(batteryE):
    # Input is WH Energy
    # positive
    # must be in units watts
    full = (batteryE - batt.minEnergy) * 1.0 / (batt.maxEnergy - batt.minEnergy)
    return int(batt.voltage * (1.0 - full) * batt.maxAmpsIn)


# max((1-full)* batt.maxAmpsIn, batt.trickle)


def drawRate(batteryE):
    # return Negative
    # must be in units of watts
    if batteryE < batt.minEnergy:
        return 0
    full = (batteryE - batt.minEnergy) * 1.0 / (batt.maxEnergy - batt.minEnergy)
    return int(-1 * batt.voltage * full * batt.maxAmpsOut)


# convert
# Battery characteristics
def toWH(power):
    # power to energy for one time step
    return power * (sampleTime / 60.0)


def toW(energy):
    # energy to power for one time step
    return int(energy / (sampleTime / 60.0))


# time units are minutes, duration, wavelength,
# start end are in hours
periodicLoad = namedtuple("Pload", "power duration wavelength")
# frequency is how many per hour
intermitentLoad = namedtuple("Iload", "power duration frequency start end")
# simple constant load
constantLoad = namedtuple("Cload", "power")
# The newly created type can be used like this:
constant = constantLoad(0)
periodic = periodicLoad(0, 0, 0)
intermitent = intermitentLoad(0, 0, 0, 0, 0)
# duration is in minutes, wavelength is in minutes

# HOME LOADS POSSIBLE
draw = constantLoad(-1000)
fridge = periodicLoad(-1000, 10, 60)
airConditioner = intermitentLoad(-5000, 5, 1, 12, 16)
coffeeMaker = periodicLoad(-60, 2, 25)
kettle = intermitentLoad(-1000, 5, 3, 6, 8)
lightsEarly = intermitentLoad(-200, 3, 3, 6, 9)
lightsLate = intermitentLoad(-100, 3, 2, 17, 22)
washingMachine = intermitentLoad(-1000, 10, 2, 11, 13)
dryerMachine = intermitentLoad(-1000, 20, 2, 12, 14)

# Or you can use named arguments:
# m = MyStruct(field1 = "foo", field2 = "bar", field3 = "baz")

##for i in range(0,300):
##    watt = chargeRate(i) #drawRate(i)
##    aH = toAmpH(watt)
##    print(str(i) + "  " + str(watt) + "    " + str(aH))
##

# print(chargeRate(250))
# print(drawRate(250))


