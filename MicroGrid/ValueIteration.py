MaxBattery=100
MaxTime=192
SampleTime=15
import PriceCalculation as pc

def valueIteration(nowTime):
    # nowTime
    Vfunction = np.ones((MaxBattery + 1,
                         MaxTime + 1)) * -1000  # battery level at each state here state is at the given time and power in the battery
    endTime = nowTime + relativedelta(minutes=MaxTime * SampleTime)
    # terminal reward is the value of the energy in the battery at endTime
    for battIndex in range(0, MaxBattery + 1):
        (value, _) = pc.energyValue(endTime, 1 * battIndex * 1.0 / EnergySample, MaxTime)
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