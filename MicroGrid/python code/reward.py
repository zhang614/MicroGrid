# peak schedule: https://www.rockymountainpower.net/ya/po/otou.html
# prices per kwh: https://www.rockymountainpower.net/content/dam/rocky_mountain_power/doc/About_Us/Rates_and_Regulation/Utah/Approved_Tariffs/Rate_Schedules/Residential_Service_Optional_Time_of_Day_Rider_Experimental.pdf
# ontario data: https://www.powerstream.ca/customers/rates-support-programs/time-of-use-pricing.html
# charging data: https://pushevs.com/2018/05/21/fast-charging-curves/

import math
import data1
import numpy as np
import matplotlib.pyplot as plt

# battery capacity in percentages
EBATT_CAPACITY = 30
# how much to multiply 24 hours by to get number of sections a day is split up into
TIME_FACTOR = 3
dayCh = data1.storecharge()
NIGHT_TIME_SECTIONS = (72 - data1.findPrevTime(data1.storePrevCharge()))
TIME_SECTIONS = data1.findTime(data1.storecharge()) + NIGHT_TIME_SECTIONS
level1 = 4
level2 = 22
start_time = 1


# returns 
def max_delta_e(fullnes):
    if (((fullnes * 1.0)) / (EBATT_CAPACITY * 1.0) < .60):
        return math.floor((level1 * 2) / TIME_FACTOR)
    return math.floor((level1 * 1.0) / TIME_FACTOR)


# dictionary holding all possible states
V = [0] * EBATT_CAPACITY
for i in range(0, EBATT_CAPACITY):
    V[i] = [0] * TIME_SECTIONS


# takes in current state and change in eBatt; gives you next state
def action(eBatt, time, delta_e):
    new_ebatt = eBatt + delta_e
    time = time + 1
    s_prime = (new_ebatt, time)
    return s_prime


# returns cost of energy at given time of day
tod_price = [0] * 72
for i in range(0, len(tod_price)):
    if (i >= 23 * TIME_FACTOR or i <= 4 * TIME_FACTOR):  # 20 * TIME_FACTOR):
        tod_price[i] = 0.016334
    else:
        tod_price[i] = 0.043560


# returns reward at given state and action 
def reward(state, action):
    eBatt, time = state
    delta_e = action
    timeOfDay = (time + (72 - NIGHT_TIME_SECTIONS)) % 72
    price = tod_price[timeOfDay] * delta_e
    if action < EBATT_CAPACITY / 20.0:
        rBatt = 0
    else:
        rBatt = 0.5 * action / (EBATT_CAPACITY * 1.0)
    return price


# fills state array with associated reward
def value_function():
    max_error = 2
    while (max_error):
        max_error = 0
        for time in range(0, TIME_SECTIONS - 1):
            for eBatt in range(0, EBATT_CAPACITY - 1):
                value = V[eBatt][time]
                best = 100
                for delta_e in range(0, max_delta_e(eBatt) + 1):
                    v_eBatt, v_time = action(eBatt, time, delta_e)
                    best = min(best, reward((eBatt, time), delta_e) + V[v_eBatt][v_time])
                V[eBatt][time] = best
                max_error = max(max_error, abs(value - best))


def policy(eBatt):  # beginning battery at index 0
    # return the policy for each index
    policy = []
    time = 0
    for time in range(0, TIME_SECTIONS - 1):
        best = 100000
        bestDeltaE = 0
        for delta_e in range(0, max_delta_e(eBatt) + 1):
            v_eBatt, v_time = action(eBatt, time, delta_e)
            now = reward((eBatt, time), delta_e) + V[v_eBatt][v_time]
            if now <= best:
                best = now
                bestDeltaE = delta_e
        policy.append(bestDeltaE)
    return policy


def calc(eBatt):
    x = 0
    if (eBatt - trip[0] <= 19):
        x = .55
    return x


def termReward():
    for eBatt in range(0, EBATT_CAPACITY):
        x = calc(eBatt)
        V[eBatt][TIME_SECTIONS - 1] = x


trip = data1.storeUse()

termReward()
value_function()
# used to draw images needed
plt.imshow(V, interpolation="nearest", origin='lower')

cbar = plt.colorbar()
cbar.set_label('Money spent in dollars', size=18)
plt.title('Data Results')
plt.ylabel('Battery Charged kwh')
plt.xlabel('Hours in twenty minute intervals')
plt.xticks(np.arange(10) * 3, ('9', '10', '11', '12am', '1', '2', '3', '4', '5', '6', '7'))
ax = plt.axes()
eBatt = 5
policy = policy(eBatt)
for i in range(0, TIME_SECTIONS - 1):
    ax.arrow(i, eBatt, 1, policy[i], head_width=0.05, head_length=0.1, fc='k', ec='k')
    eBatt = eBatt + policy[i]
plt.show()
