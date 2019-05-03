import pandas as pd

def supply_lodecalculation(DataFile='predict.csv',EnergySample=10,HourSample=4):
    df = pd.read_csv('predict.csv')
    Supply = df['Solar'].values

    Demand = df['Demand'].values
    for i in range(0, len(Supply)):
        Supply[i] = Supply[i] * EnergySample / HourSample
        Demand[i] = Demand[i] * EnergySample / HourSample

    for i in range(0, len(Demand)):
        Demand[i] = -Demand[i]
    priceofelectricity = df['Price'].values
    Zone = df['Zone'].values

    return Supply, Demand, priceofelectricity,Zone