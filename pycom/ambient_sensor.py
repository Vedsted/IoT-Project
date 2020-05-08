import time
from LTR329ALS01 import LTR329ALS01 # Ambient Light Sensor

class AmbientSensor:

    # Constructor
    def __init__(self, threshold, callback_on_emit):
        # Initialize the sensor
        integration_time = LTR329ALS01.ALS_INT_100
        measurement_rate = LTR329ALS01.ALS_RATE_500 
        gain = LTR329ALS01.ALS_GAIN_8X
        self.__lightsensor = LTR329ALS01(integration=integration_time, rate=measurement_rate, gain=gain)
        self.__is_sampling = False

        # Set default sample rate
        self.__sample_rate = 0.2

        # Threshold for when a sample should be emitted
        self.__threshold = threshold

        # Callback that should receive the sample
        self.__cb_on_emit = callback_on_emit

    def set_sample_rate(self, sample_rate):
        if sample_rate > 0: # Don't be mean
            self.__sample_rate = sample_rate

    def start_sampling(self):
        if self.__is_sampling == False: # Are we sampling already?
            self.__is_sampling = True

            lastSample = (float('-inf'), float('-inf')) # Initial value should always be overridden on 1st sample

            while self.__is_sampling:
                currentSample = self.__lightsensor.light()

                # Should we emit?
                if (abs(lastSample[0] - currentSample[0]) > self.__threshold or abs(lastSample[1] - currentSample[1]) > self.__threshold):
                    lastSample = currentSample
                    self.__emit(lastSample)
                
                time.sleep(self.__sample_rate)

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