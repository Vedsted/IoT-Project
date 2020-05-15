import time
from config import settings_ambient_sensor
from LTR329ALS01 import LTR329ALS01 # Ambient Light Sensor

class AmbientSensor:

    # Constructor
    def __init__(self, callback_on_emit):
        # Initialize the sensor
        integration_time = settings_ambient_sensor['integration_time']
        measurement_rate = settings_ambient_sensor['measurement_rate']
        gain = settings_ambient_sensor['gain']
        self.__lightsensor = LTR329ALS01(integration=integration_time, rate=measurement_rate, gain=gain)
        self.__is_sampling = False

        # Set default sample interval
        self.__sample_interval = settings_ambient_sensor['sample_interval']

        # Callback that should receive the sample
        self.__cb_on_emit = callback_on_emit

    def set_sample_interval(self, sample_interval):
        if sample_interval > 0: # Don't be mean
            self.__sample_interval = sample_interval

    def start_sampling(self):
        if self.__is_sampling == False: # Are we sampling already?
            self.__is_sampling = True

            lastSample = (float('-inf'), float('-inf')) # Initial value should always be overridden on 1st sample

            while self.__is_sampling:
                currentSample = self.__lightsensor.light()

                # Should we emit?
                #if (abs(lastSample[0] - currentSample[0]) > self.__threshold or abs(lastSample[1] - currentSample[1]) > self.__threshold):
                lastSample = currentSample
                self.__emit(lastSample)
                
                time.sleep(self.__sample_interval)

    def stop_sampling(self):
        self.__is_sampling = False

    def __emit(self, sample):
        print(sample)
        try:
            # Emit through the callback
            self.__cb_on_emit(sample)
        except:
            # The callback doesn't handle errors gracefully. Stop sampling.
            self.__is_sampling = False