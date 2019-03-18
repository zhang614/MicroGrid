import numpy as np
from matplotlib import pyplot as plt

def graphTimeSequence(eBattery,D, S, wasted, usedGrid, title):#, wasted, useGrid):
    global fig, ax1
    fig, ax1 = plt.subplots()
    #plt.clf()
    opacity = 0.4
    ind = np.arange(len(eBattery))
    plt.xlabel('Time')
    plt.ylabel('kWh')
    plt.title(title+' Solar Schedule')
    ax2 = ax1.twinx()
    ax1.bar(ind, eBattery, 1.0,
                 alpha=0.25,
                 color='g',
                 linewidth=0,
                 antialiased = True)
    ax2.bar(ind, wasted, 1.0,
                 alpha=opacity,
                 color='blue',
                 linewidth=0,
                 antialiased = True)
    ax2.bar (range(len(D)),D, 1.0,
             alpha=0.5,
             color='black',
             linewidth=0,
             antialiased = True)
    ax2.bar (range(len(usedGrid)),usedGrid, 1.0,
             alpha=0.5,
             color='red',
             linewidth=0,
             antialiased = True)
    ax2.bar (range(len(S)),S, 1.0,
             alpha=0.7,
             color='yellow',
             linewidth=0,
             antialiased = True)
##    plt.plot ( range(0,len(wasted)),S,'o-',label='wasted' )
##    plt.plot ( range(0,len(useGrid)),S,'o-',label='useGrid' )
    plt.xlabel('Time')
    ax1.set_ylabel('ENERGY: Battery(AmpH)')
    ax2.set_ylabel('POWER: Supply/Demand/Surplus(Watts)')
    plt.savefig(title+".png")
