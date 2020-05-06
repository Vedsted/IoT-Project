
import ubinascii
import time
from network import Bluetooth

# Code from:
# https://forum.pycom.io/topic/3522/is-it-possible-to-use-lopy-as-ble-gatt_server-and-gatt_client-at-the-same-time

deviceid = "chcla"

#Global variables used in this file
BLEConnectionCounter = 0 # count the connection by clients

################ BLE & LoRa Node ################
# This node will act as both BLE client and a   # 
# LoRa node device                              #
#################################################
###### First, set up BLE server service ######
def BLEServer():
    pycom.heartbeat(False)
    bluetooth = Bluetooth() #create a bluetooth object
    bluetooth.set_advertisement(name='LoPyServer'+deviceid, service_uuid=b'0000000000000000')  

    #using callback conn_cb to check client's connection
    ##Function:   conn_cb(callback for bluetooth object events checking)
    ##Description:check there is any client connected to the service
    def conn_cb (bt_o):
        events = bt_o.events()#using events to check if there is any client connected to the service      
        if  events & Bluetooth.CLIENT_CONNECTED:#2
            print("Client connected")
            pycom.rgbled(0x007f00) # green
        elif events & Bluetooth.CLIENT_DISCONNECTED:#4
            bt_o.disconnect_client()# in this way other client will have the chance to connect?
            print("Client disconnected")
            pycom.rgbled(0x7f0000) # red    
            time.sleep(3)

    bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
    bluetooth.advertise(True)
    print("Started BLE advertising")

    #set up BLE service
    srv1 = bluetooth.service(uuid=b'1111111111111111', isprimary=True)
    srv1.start()
    #set up service character
    chr1 = srv1.characteristic(uuid=b'2222222222222222', properties = Bluetooth.PROP_READ | Bluetooth.PROP_WRITE, value=123)
    # chr1.value(123) # Can take an integer, a string or a bytes object. Can only be called if there clients are connected.

    def char1_cb_handler(chr):
        events = chr.events()
        if  events & Bluetooth.CHAR_WRITE_EVENT:
            print("Write request with value = {}".format(chr.value()))
        elif events & Bluetooth.CHAR_READ_EVENT:
            return 'some data' # Lux values

    #using the callback to send the data to other clients
    char1_cb = chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)
    

# Start the BLE server
BLEServer()

while True:
    print("Keep main thread alive..")
    time.sleep(2)