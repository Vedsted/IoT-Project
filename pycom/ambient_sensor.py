import time
from LTR329ALS01 import LTR329ALS01 # Ambient Light Sensor

class AmbientSensor:

    # Constructor
    def __init__(self):
        # Initialize the sensor
        integration_time = LTR329ALS01.ALS_INT_100
        measurement_rate = LTR329ALS01.ALS_RATE_500 
        gain = LTR329ALS01.ALS_GAIN_1X
        self.__lightsensor = LTR329ALS01(integration=integration_time, rate=measurement_rate, gain=gain)

        # Set default sample rate
        self.__sample_rate = 1

        # Threshold for when a sample should be emitted
        self.__threshold = 2

    def start_sampling(self):
        lastSample = (float('-inf'), float('-inf')) # Initial value should always be overridden on 1st sample

        while True:
            currentSample = self.__lightsensor.light()

            # Should we emit?
            if (abs(lastSample[0] - currentSample[0]) > self.__threshold or abs(lastSample[1] - currentSample[1]) > self.__threshold):
                lastSample = currentSample
                self.__send(lastSample)
            
            time.sleep(self.__sample_rate)

    def __send(self, sample):
        # Send the sample to the controller
        print(sample)