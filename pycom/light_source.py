import time
from LTR329ALS01 import LTR329ALS01 # Ambient Light Sensor

class LightSource:

    # Constructor
    def __init__(self):
        # Initialize the light source
        pycom.rgbled(0xFFFFFF)

        # Init a connection to the controller

    
    def set_LED(self, red, green, blue):
        """
        Sets the RED, GREEN and BLUE components of the LED
        """

        # Append 16 bits before adding the RED component to the 3rd octet
        red = int(bin(red) + "0000000000000000", 2)

        # Append 8 bits before adding the GREEN component to the 2nd octet
        green = int(bin(green)+"00000000", 2)

        pycom.rgbled(red + green + blue) # BLUE is the 1st octet

    def __send(self, sample):
        # Send the sample to the controller
        print(sample)