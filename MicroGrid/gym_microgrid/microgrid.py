import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import random
import datetime
import pandas as pd
import PriceCalculation as pc


# totalcapacity=1000
class MicroGrid(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):

    self.action_space = spaces.Discrete(100)
    self.observation_space = spaces.Discrete(100)



  def step(self, action):
    # print(self.state)
    doen=0
    state = self.state
    battery,time = state
    # battery+=action-self.demand[time]+self.solar[time]
    battery+=action
    netEnergy = (self.solar[time] - self.demand[time] - action)/self.EnergySample
    Rbuysell = netEnergy * self.priceofelectricity[time]
    batterypercent=battery*self.EnergySample/self.BatteryMaxEnergy
    # print(batterypercent,battery,time)
    if batterypercent<20:

        BatteryPercentagePanalty=(batterypercent*-self.BatteryPanalty/20+self.BatteryPanalty)/self.HourSample
        # BatteryPercentagePanalty=100
        # print(BatteryPercentagePanalty)
    elif batterypercent>80:
        BatteryPercentagePanalty = (self.BatteryPanalty*batterypercent/20-80*self.BatteryPanalty/20) / self.HourSample
        # BatteryPercentagePanalty=100
        # print(BatteryPercentagePanalty)
    else:
        BatteryPercentagePanalty=0
    # print (battery)
    time+=1
    if time==self.MaxTime:
      doen=1

    # Rbuysell=(self.solar[time]-action*self.batterycapacity*.01-self.demand[time])*self.priceofelectricity[time]
    # Rbuysell = (- action * self.batterycapacity * .01) * self.priceofelectricity[time]

    BatteryLoss=0
    # BatteryPercentagePanalty=0
    reward=Rbuysell+BatteryLoss-BatteryPercentagePanalty
    # print(reward)
    reward=round(reward,4)
    # print(battery, action,reward)
    dt = np.dtype(np.int32)
    return np.array([battery,time],dtype=dt), reward, doen, {}


  def reset(self):

    now = datetime.datetime.now()
    slot=now.minute//15+4*now.hour
    dt = np.dtype(np.int32)
    self.state = np.array([random.randint(0, self.MaxPower),slot],dtype=dt)
    return self.state



  def render(self, mode='human',SampleTime=15,BatteryMaxEnergy=100,NumberOfHours=24,EnergySample=10,BatteryPanalty=0.01,DataFile='predict.csv'):
    self.SampleTime = SampleTime  # 60 #5 #20 #60 #in minutes, connot be greater than one hour
    self.BatteryMaxEnergy = BatteryMaxEnergy
    self.NumberOfHours = NumberOfHours  # 40 #24*2 #24*2 #can be multi day
    self.MaxTime = self.NumberOfHours * 60 // self.SampleTime  # number of sampleTime minute intervals

    self.EnergySample = EnergySample
    self.HourSample = 60 / self.SampleTime
    self.BatteryPanalty = BatteryPanalty
    self.MaxPower = 100

    df = pd.read_csv(DataFile)
    self.solar = df['Solar'].values
    self.demand = df['Demand'].values
    self.priceofelectricity = df['Price'].values
    for i in range(0, len(self.solar)):
      self.solar[i] = self.solar[i] * self.EnergySample / self.HourSample
      self.demand[i] = self.demand[i] * self.EnergySample / self.HourSample
    return 0
  def close(self,batteryindex,time):
    self.state = np.array([batteryindex, time])
