############################
# Controller settings
############################
settings = {
    'ambient_sensor_ble_mac': '30:AE:A4:50:5D:2A',

    'broker_address': 'localhost',
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
    'intensity_min': 0
}