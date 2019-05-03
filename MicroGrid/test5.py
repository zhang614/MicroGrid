import pandas as pd
import calculateSupply
df=pd.read_csv('SolarData.csv')
solarvalues=df['Solar'].values


def solarprediction(nowTime, sampleTime,MaxTime, NumberofHours, MaxSolar):
    solar = []
    minutes=0
    print(nowTime, sampleTime,MaxTime, NumberofHours, MaxSolar)
    hour=0
    for i in range(0, MaxTime):
        x = solarvalues[hour]

        if x > 259:

            x = (x *MaxSolar)/ 2400

        else:
            x = 0
        print(x)
        solar.append(x)

        minutes=minutes+sampleTime
        hour=minutes//60
    return solar
