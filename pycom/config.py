from LTR329ALS01 import LTR329ALS01 # Ambient Light Sensor constants

settings = {
    'deviceid': 'FilipsBlue',
    
    # Bluetooth services
    'filipsblue_service': b'1111222233334444', # can be converted to the uuid equivalent with: uuid.UUID(bytes=b'1111222233334444')
    'ambient_sensor_service' : b'2222222222222220',
    'ambient_sensor_chr' : b'2222222222222221',
    'ambient_sensor_sample_rate_chr' : b'2222222222222222',
    'light_source_service' : b'3333333333333330',
    'light_source_chr' : b'3333333333333331'
}

settings_ambient_sensor = {
    'integration_time' : LTR329ALS01.ALS_INT_100,
    'measurement_rate' : LTR329ALS01.ALS_RATE_500,
    'gain' : LTR329ALS01.ALS_GAIN_1X,
    'sample_rate' : 1 # in seconds. Allows floating point.
}