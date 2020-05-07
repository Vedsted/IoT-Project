import time
import pycom
    
def set_LED_rgb(red, green, blue):
    """
    Sets the RED, GREEN and BLUE components of the LED
    """

    # Append 16 bits before adding the RED component to the 3rd octet
    red = int(bin(red) + "0000000000000000", 2)

    # Append 8 bits before adding the GREEN component to the 2nd octet
    green = int(bin(green)+"00000000", 2)

    pycom.rgbled(red + green + blue) # BLUE is the 1st octet

def set_LED(color):
    pycom.rgbled(color)