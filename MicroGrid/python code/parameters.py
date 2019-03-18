HOME_ENERGY_FILE_LOCATION = "24_hr_test_load.csv"
LOAD_V_TABLE_INITIALIZER_FILE_LOCATION = "24_hr_test_load.csv"
LOAD_COL_INDEX = 0
SOLAR_GENERATION_FILE_LOCATION = ""
ENERGY_COL_INDEX = 0
NUM_DAYS_TO_SIMULATE = 3
# Time in hours
NUM_TIME_STEP_BINS = 24
TIME_STEP = 1
PEAK_TIME_BEGIN = 9
PEAK_TIME_END = 20
# Cost in dollars
PEAK_TIME_COST = -0.20
COST = -.08
PEAK_TIME_SELL = abs(PEAK_TIME_COST/3)
SELL = abs(COST/3)
# Battery limits in Kw*hrs
# TODO implement these in main to determine how much to charge and discharge the battery
MAX_DISCHARGE = -10
MAX_CHARGE = 10
MAX_BATTERY_CAPACITY = 14
NUM_BATTERY_CAPACITY_BINS = 14
# TODO Max load parameters
# V Table
MIN_ACCEPTABLE_DELTA = .5
# parameters for SELECT function
MAX_ACCEPTABLE_LOAD_FOR_SELECT = 1.5 # Kw