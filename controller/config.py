############################
# Ambient sensor constants
############################
ALS_GAIN_VALUES = {
    'ALS_GAIN_1X': 1,
    'ALS_GAIN_2X': 2,
    'ALS_GAIN_4X': 4,
    'ALS_GAIN_8X': 8,
    'ALS_GAIN_48X': 48,
    'ALS_GAIN_96X': 96
}

ALS_INT_VALUES = {
    'ALS_INT_50': 0.5,
    'ALS_INT_100': 1,
    'ALS_INT_150': 1.5,
    'ALS_INT_200': 2,
    'ALS_INT_250': 2.5,
    'ALS_INT_300': 3,
    'ALS_INT_350': 3.5,
    'ALS_INT_400': 4
}

############################
# Controller settings
############################
settings = {
    'ambient_sensor_ble_mac': '30:AE:A4:50:5D:2A',

    'broker_address': '178.62.226.29',
    'broker_port': 1883,
    'broker_keep_alive': 60, # seconds

    'controller_id': 'controller1',
    'group_id': 'group1',
    'lux': (float('-inf'), float('-inf')),
    'setpoint': 60, # Initial setpoint. This is the lux level we aim for
    'setpoint_error' : 5, # accept a certain error
    'light_red': 255,
    'light_green': 255,
    'light_blue': 255,
    'intensity_max': 51,
    'intensity_min': 0,

    # These settings must match up with the settings on the ambient sensor,
    # in order to calculate the lux value.
    'ALS_INT_VALUE' : ALS_INT_VALUES[1],
    'ALS_GAIN_VALUE' : ALS_GAIN_VALUES[0]
}