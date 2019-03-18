import numpy as np
from matplotlib import pyplot as plt
from loads import batt
import arrow
import os

def graphTimeSequence(eBattery,D, S, wasted, usedGrid, title):#, wasted, useGrid):
    global fig, ax1
    fig, ax1 = plt.subplots()
    #plt.clf()
    dBattery = map(lambda e: e-batt.minEnergy, eBattery)
    opacity = 0.4
    maxDisplayTime = len(D)
    ind = np.arange(len(D))
    plt.xlabel('Time')
    plt.ylabel('kWh')
    plt.title(title+' Solar Schedule')
    ax2 = ax1.twinx()
    ax1.bar(ind, dBattery, 1.0,
                 alpha=0.25,
                 color='g',
                 linewidth=0,
                 antialiased = True)
    ax2.bar(ind, wasted, 1.0,
                 alpha=0.3,
                 color='blue',
                 linewidth=0,
                 antialiased = True)
    ax2.bar (ind, D, 1.0,
             alpha=0.2,
             color='black',
             linewidth=0,
             antialiased = True)
    ax2.bar (ind, usedGrid, 1.0,
             alpha=0.2,
             color='red',
             linewidth=0,
             antialiased = True)
    ax2.bar (ind, S, 1.0,
             alpha=0.5,
             color='yellow',
             linewidth=0,
             antialiased = True)
##    plt.plot ( range(0,len(wasted)),S,'o-',label='wasted' )
##    plt.plot ( range(0,len(useGrid)),S,'o-',label='useGrid' )
    plt.xlabel('Time')
    ax1.set_ylabel('ENERGY: Battery(AmpH)')
    ax2.set_ylabel('POWER: Supply/Demand/Surplus(Watts)')
    # SAVE FILE
    local = arrow.utcnow().to('US/Mountain')
    date = local.format('YYYY-MM-DD')
    directory = "./" + date
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    # The final path to save to
    filename = title+".png"
    savepath = os.path.join(directory, filename)
    plt.savefig(savepath)
