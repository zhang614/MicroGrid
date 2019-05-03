import numpy as np
from matplotlib import pyplot as plt
# from loads import batt
import os
from pylab import *
import sys
import data
from matplotlib import cm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


# rcParams['legend.loc'] = 'best'
# http://matplotlib.org/examples/pylab_examples/bar_stacked.html

def graphVfunction(vFunction, batteryState, sampleTime):
    print (vFunction)
    plt.imshow(vFunction, interpolation="none", origin='lower', alpha=0.5, aspect=1.5, cmap=cm.jet)
    cbar = plt.colorbar()
    cbar.set_label('Cumulative Value', size=12)
    plt.title('ValueFunction')
    plt.ylabel('Battery Charged kwh')
    plt.xlabel('Hours in ' + str(sampleTime) + " minute intervals")
    # plt.xticks(np.arange(10)*3, ('9', '10', '11', '12am', '1','2','3','4','5','6','7'))
    ax = plt.axes()
    eBatt = 0
    for i in range(0, len(batteryState) - 1):
        ax.arrow(i, batteryState[i], 1, batteryState[i + 1] - batteryState[i], width=0.05, length_includes_head=True,
                 head_length=0.1, color='black')  # fc='k', ec='k')
        eBatt = eBatt + batteryState[i]
    plt.show()


def getTimeAxisInfo(nowDayTime, sampleTime, maxTime):
    # returns the place where the x axis ticks should be on the hour
    dayTime = nowDayTime
    positions = []
    labels = []
    for timeIndex in range(0, maxTime):
        if dayTime.minute == 0:
            positions.append(timeIndex)
            labels.append(dayTime.hour)
        dayTime = dayTime + relativedelta(minutes=sampleTime)
    return (positions, labels)


def graphMicroGrid(batteryState, buyEnergy=[], sellEnergy=[], sampleTime=60, nowDayTime=None,
                   supply=[], demand=[], costList=[], zoneList=[], title="",buyactionList=[],sellactionList=[]):  # , wasted, useGrid):
    global fig, ax1
    fontSize = 14
    # fig, ax1 = plt.subplots()
    # plt.clf()
    maxTime = len(batteryState)
    timeIterations = np.arange(maxTime)

    # Energy
    # Two subplots, the axes array is 1-d

    f, axarr = plt.subplots(5, sharex=True, figsize=(15, 15))
    # f.tight_layout()
    f.subplots_adjust(hspace=0.22)
    # TOP inputs supply and demand
    barD = axarr[0].bar(timeIterations, demand, 1.0,
                        alpha=0.8,
                        color='gray',
                        linewidth=0,
                        antialiased=True)
    barS = axarr[0].bar(timeIterations, supply, 1.0,
                        alpha=0.8,
                        color='orange',
                        linewidth=0,
                        antialiased=True)
    # axarr[0].set_xlabel('Time')
    axarr[0].set_ylabel('Energy Units')
    axarr[0].set_title(title + ' In/Out Power', fontsize=fontSize)
    axarr[0].legend([barS[0], barD[0]], ['Supply', 'Demand'], loc=1)
    axarr[0].grid(axis='both', color='black', linestyle='-', linewidth=1, alpha=0.5)
    # MIDDLE battery state
    axarr[1].set_ylabel('Energy Units')
    axarr[1].set_title(title + ' Battery Energy Stored', fontsize=fontSize)
    barBat = axarr[1].bar(timeIterations, batteryState, 1.0,
                          alpha=0.8,
                          color='blue',
                          linewidth=0,
                          antialiased=True)
    axarr[1].legend([barBat[0]], ['Battery SOC'], loc=1)
    axarr[1].grid(axis='both', color='black', linestyle='-', linewidth=1, alpha=0.5)
    # Buy sell schedule
    # axarr[2].set_xlabel('Time')

    axarr[2].set_ylabel('Energy Units')
    axarr[2].set_title("\n" + title + ' Action Taken', fontsize=fontSize)
    buyaction=axarr[2].bar(timeIterations,buyactionList,1.0,
                          alpha=0.9,
                          color='maroon',
                          linewidth=0,
                          antialiased=True)
    sellaction = axarr[2].bar(timeIterations, sellactionList, 1.0,
                             alpha=0.9,
                             color='seagreen',
                             linewidth=0,
                             antialiased=True)

    axarr[2].legend([buyaction[0], sellaction[0]], ['Charge', 'Discharge'], loc=1)
    axarr[2].grid(axis='both', color='black', linestyle='-', linewidth=1, alpha=0.5)


    axarr[3].set_ylabel('Energy Units')
    axarr[3].set_title("\n" + title + ' Buy Sell Schedule', fontsize=fontSize)
    barBuy = axarr[3].bar(timeIterations, buyEnergy, 1.0,
                          alpha=0.9,
                          color='salmon',
                          linewidth=0,
                          antialiased=True)
    barSell = axarr[3].bar(timeIterations, sellEnergy, 1.0,
                           alpha=0.9,
                           color='lime',
                           linewidth=0,
                           antialiased=True)
    axarr[3].legend([barBuy[0], barSell[0]], ['Buy', 'Sell'], loc=1)
    axarr[3].grid(axis='both', color='black', linestyle='-', linewidth=1, alpha=0.5)
    # Cumulate value
    axarr[4].set_xlabel('Time in Hours')
    axarr[4].set_ylabel(' $ Value')
    axarr[4].set_title(title + ' Operational Cost/Benefit', fontsize=fontSize)
    axarr[4].plot(costList, ls='steps', c='b')
    toColor = {'off': 'yellowgreen', 'mid': 'gold', 'peak': 'brown', '': 'white'}
    for i in range(0, len(zoneList)):
        axarr[4].axvspan(i - 1.5, i - 0.5, facecolor=toColor[zoneList[i]], alpha=0.2)
    legends = []
    for key, value in toColor.items():
        if not value == 'white':
            legends.append(Patch(facecolor=value, label=key, alpha=1.0))
    (xPositions, xLabels) = getTimeAxisInfo(nowDayTime, sampleTime, maxTime)
    axarr[4].set_xticks(xPositions)
    axarr[4].set_xticklabels(xLabels)
    axarr[4].legend(handles=legends, loc=1)
    axarr[3].grid(axis='both', color='black', linestyle='-', linewidth=1, alpha=0.5)
    # plt.figure(figsize=(5, 10))
    plt.show()
    # SAVE FILE
    ##    local = arrow.utcnow().to('US/Mountain')
    ##    date = local.format('YYYY-MM-DD')
    # directory = "D:\Courses\Reinforcement Learning\Project\Microgrid\MicroGrid\python code"
    # If the directory does not exist, create it
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    # The final path to save to
    # filename = "test-" + title + ".png"
    # savepath = os.path.join(directory, filename)
    # plt.savefig(filename)


def wToWH(powerArray):
    answer = np.zeros(len(powerArray))
    total = 0
    for i in range(0, len(powerArray)):
        total = total + data.toWH(powerArray[i])
        answer[i] = total
    return answer


def toK(data):
    # data us alreadt a numpy array
    return data / 1000.0

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