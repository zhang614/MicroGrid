import datetime
import parameters
from enum import Enum
import pandas
import math
import matplotlib.pyplot as plt
import random

BATTERY_SCALAR = parameters.MAX_BATTERY_CAPACITY / parameters.NUM_BATTERY_CAPACITY_BINS


class Buy_Sell_Amount:
    def __init__(self):
        self.amount_to_buy = 0
        self.amount_to_sell = 0


class State:
    def __init__(self, is_v_table_initializer=False):
        self.time = 0
        self.date = 0
        self.battery_charge = 0
        self.net_gain = 0
        # TODO Future work, use max_load to calculate a terminal reward at the end of a billing cycle
        # self.max_load = 0
        self.cur_load = 0
        self.__get_next_load = get_system_load(is_v_table_initializer)
        self.cur_energy_gen = 0
        self.__get_next_energy = get_energy_generated()
        self.max_battery_capacity = parameters.MAX_BATTERY_CAPACITY
        self.get_next_energy_gen()
        self.get_next_system_load()

    def get_next_energy_gen(self):
        self.cur_energy_gen = self.__get_next_energy(self.time)

    def get_next_system_load(self, row=None):
        self.cur_load = self.__get_next_load(row)

    '''
    This function returns the excess amount.
        ie if you try to charge it more than is possible or discharge more than it has.
    '''

    def get_difference_battery_level(self, delta_energy):
        buy_sell = Buy_Sell_Amount()
        total_energy = self.battery_charge + delta_energy
        if total_energy > parameters.MAX_BATTERY_CAPACITY:
            buy_sell.amount_to_sell = total_energy - parameters.MAX_BATTERY_CAPACITY
        elif total_energy < 0:
            buy_sell.amount_to_buy = abs(total_energy)
        return buy_sell

    def change_battery_level(self, delta_energy):
        self.battery_charge += delta_energy
        if self.battery_charge > parameters.MAX_BATTERY_CAPACITY:
            self.battery_charge = parameters.MAX_BATTERY_CAPACITY
        elif self.battery_charge < 0:
            self.battery_charge = 0

    def increment_time(self):
        self.time += parameters.TIME_STEP
        if (self.time > parameters.TIME_STEP * parameters.NUM_TIME_STEP_BINS):
            self.time -= parameters.TIME_STEP * parameters.NUM_TIME_STEP_BINS


class plot_info:
    def __init__(self):
        self.time = []
        self.battery_charges = []
        self.loads = []
        self.gains = []
        self.energy_gens = []


'''
Commented out code can be used if you'd like to use data from a csv file to run the simulation.
TODO Get live data for current energy generated
TODO Create a Neural Network to predict next time step's energy generation
'''


def get_energy_generated():
    '''
    df = pandas.read_csv(parameters.SOLAR_GENERATION_FILE_LOCATION)
    row = 0
    '''
    cloud_ahoy = False
    cloud_timer = parameters.TIME_STEP * random.randint(0, 3)

    def get_energy(time):
        nonlocal
        cloud_ahoy
        nonlocal
        cloud_timer
        begin_solar_gen_time = 11
        end_solar_gen_time = 18
        if cloud_ahoy:
            scalar = random.randint(700, 900) / 600
            cloud_timer -= 1
            if cloud_timer == 0:
                cloud_ahoy = False
                cloud_timer = parameters.TIME_STEP * random.randint(0, 4)
        else:
            scalar = random.randint(700, 900) / 100
            if random.randint(0, 50) / 50 == 1: cloud_ahoy = True

        if (time > begin_solar_gen_time and time < end_solar_gen_time):
            return math.sin(
                (time - begin_solar_gen_time) * math.pi / (end_solar_gen_time - begin_solar_gen_time)) * scalar
        return 0

    '''def get_energy():
        nonlocal row
        energy_generated = df.iloc[row, parameters.ENERGY_COL_INDEX]
        row += 1
        return energy_generated'''

    return get_energy


'''
Gets system load from a CSV
TODO Get live data for current load
TODO Create a Neural Network to predict next time step's load
'''


def get_system_load(is_v_table_initializer=False):
    if is_v_table_initializer:
        df = pandas.read_csv(parameters.LOAD_V_TABLE_INITIALIZER_FILE_LOCATION, header=None)
    else:
        df = pandas.read_csv(parameters.HOME_ENERGY_FILE_LOCATION, header=None)
    row = 0

    def get_load(cur_time_bin=None):
        nonlocal
        row
        nonlocal
        is_v_table_initializer
        if cur_time_bin != None: row = cur_time_bin
        energy_generated = df.iloc[row, parameters.LOAD_COL_INDEX]
        row += 1
        row %= 24
        if is_v_table_initializer == False:
            offset = random.randint(0, 100) / 100
        else:
            offset = 0
        return energy_generated + offset

    return get_load


def get_battery_wear(delta_energy):
    # TODO Replace this function with the real one from Select
    return -abs((delta_energy / BATTERY_SCALAR) ** 2 / 1000)


def get_reward(state, action):
    buy_sell = state.get_difference_battery_level(action)
    battery_percent = (state.battery_charge / parameters.MAX_BATTERY_CAPACITY)
    # Linear function to give negative weight to discharging the battery too much
    battery_percent_penalty = (0 if battery_percent > 0.2 else (0.2 - battery_percent))

    return gain_changer(state, action) + get_battery_wear(
        action - buy_sell.amount_to_buy - buy_sell.amount_to_sell) - battery_percent_penalty


'''
Calculates the cost of any given action based on the state.
Return a BuySell class with the $ amount
'''


def gain_changer(state, action):
    buy_sell = Buy_Sell_Amount()
    energy_difference = -action - state.cur_load + state.cur_energy_gen
    if energy_difference < 0:
        buy_sell.amount_to_buy = abs(energy_difference)
    else:
        buy_sell.amount_to_sell = abs(energy_difference)

    if state.time > parameters.PEAK_TIME_BEGIN and state.time < parameters.PEAK_TIME_END:
        return buy_sell.amount_to_buy * parameters.PEAK_TIME_COST + buy_sell.amount_to_sell * parameters.PEAK_TIME_SELL
    else:
        return buy_sell.amount_to_buy * parameters.COST + buy_sell.amount_to_sell * parameters.SELL


'''
Return the best action based off the v_table for given a particular state.
'''


def arg_max(state, v_table):
    cur_battery_level = int(state.battery_charge / BATTERY_SCALAR)
    best = float("-inf")
    for delta_battery_level in range(-cur_battery_level, parameters.NUM_BATTERY_CAPACITY_BINS - cur_battery_level):
        cur_score = get_reward(state, delta_battery_level * BATTERY_SCALAR) + \
                    v_table[(state.time + 1) % parameters.NUM_TIME_STEP_BINS][cur_battery_level + delta_battery_level]
        if best < cur_score:
            best = cur_score
            action = delta_battery_level

    return action * BATTERY_SCALAR


def get_state_to_initialize_v_table_from_end_state():
    is_v_table_initializer = True
    state = State(is_v_table_initializer)
    state.time = parameters.TIME_STEP * (parameters.NUM_TIME_STEP_BINS - 1)
    state.get_next_system_load(parameters.NUM_TIME_STEP_BINS - 1)
    state.get_next_energy_gen()
    state.cur_energy_gen = 0
    state.cur_load = 0
    return state


def initialize_v_table():
    v_table = []
    # Initialize v_table
    for time_step_bin in range(parameters.NUM_TIME_STEP_BINS):
        v_table.append([])
        for battery_bin in range(parameters.NUM_BATTERY_CAPACITY_BINS):
            v_table[time_step_bin].append(0)

    state = get_state_to_initialize_v_table_from_end_state()

    # Fill in final column of v_table
    for battery_level in range(parameters.NUM_BATTERY_CAPACITY_BINS):
        v_table[parameters.NUM_TIME_STEP_BINS - 1][battery_level] = get_reward(state, -battery_level * BATTERY_SCALAR)

    # Fill v_table
    delta = float("inf")
    while delta > parameters.MIN_ACCEPTABLE_DELTA:
        delta = 0
        for cur_time_bin in range(parameters.NUM_TIME_STEP_BINS - 2, -1, -1):
            # Update State for current time
            state.time = cur_time_bin * parameters.TIME_STEP
            state.get_next_system_load(cur_time_bin)
            state.get_next_energy_gen()

            # Loop through all battery states
            for cur_battery_level in range(parameters.NUM_BATTERY_CAPACITY_BINS):
                state.battery_charge = cur_battery_level * BATTERY_SCALAR
                v = v_table[cur_time_bin][cur_battery_level]

                # Loop through all possible actions (empty battery to charge fully)
                best = float("-inf")
                for delta_battery_level in range(-cur_battery_level,
                                                 parameters.NUM_BATTERY_CAPACITY_BINS - cur_battery_level):
                    best = max(best,
                               get_reward(state, delta_battery_level * BATTERY_SCALAR) + v_table[cur_time_bin + 1][
                                   cur_battery_level + delta_battery_level])
                delta = max(delta, abs(v - best))
                v_table[cur_time_bin][cur_battery_level] = best

    return v_table


'''
Simulates a time step
TODO Track billing cycle's max amount bought at any given time step for calculating terminal reward (state.max_load)
'''


def simulate_time_step(state, action):
    state.net_gain += get_reward(state, action)
    state.change_battery_level(action)
    state.increment_time()
    state.get_next_energy_gen()
    state.get_next_system_load()


'''
Simple print function for debugging purposes
'''


def print_v_table(v_table):
    print("--- V_Table ---")
    for i, time_bin in enumerate(v_table):
        print(i)
        print(time_bin)
    print("-------------")


'''
Similar to the basic function that SELECT uses in controlling when their battery charges or discharges
'''


def get_action_for_select_function(state):
    if state.cur_load >= parameters.MAX_ACCEPTABLE_LOAD_FOR_SELECT:
        action = -min(state.cur_load - parameters.MAX_ACCEPTABLE_LOAD_FOR_SELECT, state.battery_charge)
    elif (state.time > 23 or state.time < 5) and state.battery_charge < parameters.MAX_BATTERY_CAPACITY:
        action = state.cur_load + parameters.MAX_BATTERY_CAPACITY / 6
    else:
        action = 0
    return action


'''
Function to plot a single methods results
Plots energy gen, load, and battery charge over time on one graph and cost to run the system on another
'''


def plot_results(info, title):
    plt.figure(1)
    plt.title(title)
    plt.subplot(211)
    plt.plot(info.time, info.energy_gens, label='Energy gen')
    plt.plot(info.time, info.loads, label='Load')
    plt.ylabel("Kilowatts")
    plt.xlabel("Hours")
    plt.legend()
    plt.plot(info.time, info.battery_charges, label='Battery charge')

    plt.subplot(212)
    plt.plot(info.time, info.gains, label='Net gain/loss')
    plt.ylabel("Net gain/loss ($)")
    plt.xlabel("Hours")
    plt.legend()
    plt.show()


'''
Plots a comparison of two methods
Plots energy gen, load, and battery charges over time on one graph and cost to run the systems on another
'''


def plot_comparison(graph_ml_info, graph_select_info, graph_title):
    plt.rcParams.update({'font.size': 20})
    plt.figure(1)
    plt.title(graph_title)
    plt.subplot(211)
    plt.plot(graph_ml_info.time, graph_ml_info.energy_gens, label='Energy gen', color='g')
    plt.plot(graph_select_info.time, graph_select_info.loads, label='Load', color='r')
    plt.ylabel("Kilowatts")
    plt.legend()

    plt.subplot(212)
    plt.plot(graph_ml_info.time, graph_ml_info.battery_charges, label='ML Battery charge', color='b')
    plt.plot(graph_select_info.time, graph_select_info.battery_charges, label='SELECT Battery charge', color='m')
    plt.ylabel("Kilowatt/Hours")
    plt.xlabel("Hours")
    plt.legend()

    plt.show()

    plt.plot(graph_ml_info.time, graph_ml_info.gains, label='ML Net gain/loss', color='b')
    plt.plot(graph_select_info.time, graph_select_info.gains, label='SELECT Net gain/loss', color='m')
    plt.ylabel("Net gain/loss ($)")
    plt.xlabel("Hours")
    plt.legend()

    plt.show()


'''
Return a function that
    if use_machine_learning: returns actions based on the v_table
    else: returns actions based off SELECT's algorithm
'''


def choose_action_method(use_machine_learning):
    def get_machine_learning_action(cur_state):
        nonlocal
        v_table
        return arg_max(cur_state, v_table)

    if use_machine_learning:
        v_table = initialize_v_table()
        return get_machine_learning_action
    else:
        return get_action_for_select_function


def update_graph_info(graph_info, state, time_of_day):
    graph_info.time.append(time_of_day)
    graph_info.energy_gens.append(state.cur_energy_gen)
    graph_info.loads.append(state.cur_load)
    graph_info.battery_charges.append(state.battery_charge)
    graph_info.gains.append(state.net_gain)


def run_simulation(use_machine_learning):
    is_v_table_initializer = False
    cur_state = State(is_v_table_initializer)
    num_time_steps_to_simulate = parameters.NUM_DAYS_TO_SIMULATE * parameters.NUM_TIME_STEP_BINS
    get_action = choose_action_method(use_machine_learning)

    graph_info = plot_info()

    update_graph_info(graph_info, cur_state, cur_state.time)

    for time_step in range(num_time_steps_to_simulate):
        update_graph_info(graph_info, cur_state, parameters.TIME_STEP * time_step)

        cur_action = get_action(cur_state)
        simulate_time_step(cur_state, cur_action)

    return graph_info


if __name__ == "__main__":
    use_machine_learning = True
    graph_ml_info = run_simulation(use_machine_learning)
    use_machine_learning = False
    graph_select_info = run_simulation(use_machine_learning)
    # plot_results(graph_ml_info, 'ML Function')
    # plot_results(graph_select_info, 'SELECT Function')

    graph_title = str(parameters.NUM_DAYS_TO_SIMULATE) + ' Day Simulation'
    plot_comparison(graph_ml_info, graph_select_info, graph_title)
