import matplotlib.pyplot as plt
BatteryPanalty=0.01
HourSample=4
BatteryPanaltyList=[]
index=[]
for batterypercent in range(0,101):
    index.append(batterypercent)
    if batterypercent < 20:

        BatteryPercentagePanalty = -1*(batterypercent * -BatteryPanalty / 20 + BatteryPanalty) / HourSample
        # BatteryPercentagePanalty=100
        # print(BatteryPercentagePanalty)
    elif batterypercent > 80:
        BatteryPercentagePanalty = -1*(BatteryPanalty * batterypercent / 20 - 80 *BatteryPanalty / 20) / HourSample
        # BatteryPercentagePanalty=100
        # print(BatteryPercentagePanalty)
    else:
        BatteryPercentagePanalty = 0

    BatteryPanaltyList.append(BatteryPercentagePanalty)

plt.plot(index,BatteryPanaltyList)
plt.xlabel('Battery Percentage',fontsize=16)
plt.ylabel('Penalty in dollar',fontsize=16)
plt.title('Holding cost reward',fontsize=16)
plt.show()