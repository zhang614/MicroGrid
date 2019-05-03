import microgrid_ValueIteration as MV
import data
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import seaborn as sns
profit=[]
shortprofit=[]
for solarcapacity in range(100,101,5):
    shortprofit=[]
    utc = datetime.today()
    timezone = pytz.timezone('US/Mountain')
    nowTime = timezone.localize(utc).replace(hour=6,minute=0, second=0, microsecond=0)

    # data.calculatesupplyanddemand(nowTime=nowTime,MaxSolar=solarcapacity)
    for batterycapacity in range(30,31,5):
        final=MV.optimizer(sampletime=15,batterypanalty=0.01,numberOfhours=2*24,gamma=1,maxsolar=solarcapacity,maxload=30,batterymaxenergy=batterycapacity,energysample=10)
        final=round(final,2)
        shortprofit.append(final)
        print(final)
    profit.append(shortprofit)

profitlist=[]
for i in range(len(profit)-1,-1,-1):
    profitlist.append(profit[i])
name = 'graph.png'
plt.savefig(name)
plt.clf()
plt.figure(figsize=(10,8))
ax=sns.heatmap(profitlist,linewidths=0.5,cmap="Reds",annot=True)
ax.set_yticklabels([50,45,40,35,30,25,20])
ax.set_xticklabels([0,5,10,15,20])
plt.xlabel('Battery Capacity in KW')
plt.ylabel('Solar Capacity in KW')
plt.title('Cost based on solar and battery capacity')
plt.yticks(rotation=70)
xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()

plt.savefig(name)
plt.clf()