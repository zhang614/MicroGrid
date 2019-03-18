import numpy as np
from matplotlib import pyplot as plt
from loads import batt
import arrow
import os
from pylab import *
import sys
import data

#rcParams['legend.loc'] = 'best'
#http://matplotlib.org/examples/pylab_examples/bar_stacked.html

def graphTimeSequence(eBattery,D, S, wasted, usedGrid,sampleTime,title):#, wasted, useGrid):
    global fig, ax1
    #fig, ax1 = plt.subplots()
    #plt.clf()
    dBattery = eBattery #map(lambda e: e-batt.minEnergy, eBattery)
    opacity = 0.4
    maxDisplayTime = len(D)
    ind = np.arange(len(D))
    (timeValues, timeLabels) = makeLabels(len(eBattery),sampleTime)
    # Energy
    # Two subplots, the axes array is 1-d
    f, axarr = plt.subplots(2, sharex=True)
    plt.setp(axarr,xticks=timeValues,xticklabels=timeLabels)
    #axarr[0].plot(x, y)
    #axarr[0].set_title('Sharing X axis')
    #axarr[1].scatter(x, y)
##    print toK(dBattery)
##    print toK(wToWH(usedGrid,sampleTime))
##    print toK(wToWH(wasted,sampleTime))
##    print toK(D)
##    print toK(S)
    axarr[0].set_xlabel('Time (hours)')
    axarr[0].set_ylabel('ENERGY: Watt hours (KWh)')
    axarr[0].set_title(title+' Solar Schedule')
    barBat=axarr[0].bar(ind, toK(dBattery), 1.0,
                 alpha=0.25,
                 color='g',
                 linewidth=0,
                 antialiased = True)
    barBuy=axarr[0].bar(ind, toK(wToWH(usedGrid,sampleTime)), 1.0,
                 alpha=0.25,
                 color='r',
                 linewidth=0,
                 antialiased = True)
    barSell = axarr[0].bar(ind, toK(wToWH(wasted,sampleTime)), 1.0,
                 alpha=0.25,
                 color='b',
                 linewidth=0,
                 antialiased = True)
    leg=axarr[0].legend([barBat[0], barBuy[0], barSell[0]], ['Battery', 'Buy', 'Extra'], loc = 4)
    axarr[1].set_xlabel('Time (hours)')
    leg.get_frame().set_alpha(0.5)
    axarr[1].set_ylabel('POWER: Watts (Kw)')
    barD = axarr[1].bar(ind, toK(D), 1.0,
                 alpha = 0.5,
                 color = 'black',
                 linewidth = 0,
                 antialiased = True)
    barS = axarr[1].bar(ind, toK(S), 1.0,
                 alpha = 0.5,
                 color = 'yellow',
                 linewidth = 0,
                 antialiased = True)
    leg=legend([barS[0],barD[0]],['Supply', 'Demand'], loc=2)
    leg.get_frame().set_alpha(0.5)
    # SAVE FILE
##    local = arrow.utcnow().to('US/Mountain')
##    date = local.format('YYYY-MM-DD')
    directory = ".\\" + "AAtests"
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
    # The final path to save to
    filename = "test-"+title+".png"
    savepath = os.path.join(directory, filename)
    print savepath
    if os.path.exists(savepath):
        print "file exists"
        os.remove(savepath)
    plt.savefig(savepath)
    plt.show()

def wToWH(powerArray,sampleTime):
    answer = np.zeros(len(powerArray))
    for i in range(0, len(powerArray)):
        answer[i] = data.toWH(powerArray[i],sampleTime)
    return answer

def toK(data):
    #data us alreadt a numpy array
    return data / 1000.0

def makeLabels(n, sampleTime):
    #returns a list of time values and labels
    #******************************
    #About 12 numbers needed
    #1,2,3,6,9,12,24 hours
    tickSols = [1,2,3,6,12,24]
    actualHours = n*sampleTime/60
    hoursPerTick = actualHours/12
    tickHours = tickSols[np.argmin([abs(hoursPerTick-i)/i for i in tickSols])]
    return ([i*60/sampleTime for i in range(0,actualHours,tickHours)],
            [str(i%24) for i in range(0,actualHours,tickHours)])

#print makeLabels(160, 20)
#print makeLabels(24, 60)

##
##    
##    ax2 = ax1.twinx()
##
##    ax2.bar(ind, wasted, 1.0,
##                 alpha=0.3,
##                 color='blue',
##                 linewidth=0,
##                 antialiased = True)
##    ax2.bar (ind, D, 1.0,
##             alpha=0.2,
##             color='black',
##             linewidth=0,
##             antialiased = True)
##    ax2.bar (ind, usedGrid, 1.0,
##             alpha=0.2,
##             color='red',
##             linewidth=0,
##             antialiased = True)
##    ax2.bar (ind, S, 1.0,
##             alpha=0.5,
##             color='yellow',
##             linewidth=0,
##             antialiased = True)
####    plt.plot ( range(0,len(wasted)),S,'o-',label='wasted' )
####    plt.plot ( range(0,len(useGrid)),S,'o-',label='useGrid' )
##    plt.xlabel('Time')
##    
##    ax2.set_ylabel('POWER: Supply/Demand/Surplus(Watts)')
    # SAVE FILE
##    local = arrow.utcnow().to('US/Mountain')
##    date = local.format('YYYY-MM-DD')
##    directory = "./" + date
##    # If the directory does not exist, create it
##    if not os.path.exists(directory):
##        os.makedirs(directory)
##    # The final path to save to
##    filename = "test-" + title+".png"
##    savepath = os.path.join(directory, filename)
##    plt.savefig(savepath)
