
import ubinascii
import time
import _thread
from light_source import set_LED_rgb
from ambient_sensor import AmbientSensor
from network import Bluetooth

# Code from:
# https://forum.pycom.io/topic/3522/is-it-possible-to-use-lopy-as-ble-gatt_server-and-gatt_client-at-the-same-time

deviceid = "LoPyServerchcla"
my_service_uuid = b'1111222233334444' # can be converted to the uuid equivalent with: uuid.UUID(bytes=b'1111222233334444')
isConnected = False

################ BLE node        ################
# This node acts as both BLE GATT server        # 
#################################################
def BLEServer():
    bluetooth = Bluetooth() #create a bluetooth object
    bluetooth.set_advertisement(name=deviceid, service_uuid=my_service_uuid)  

    #using callback conn_cb to check client's connection
    ##Function:   conn_cb(callback for bluetooth object events checking)
    ##Description:check there is any client connected to the service
    def conn_cb (bt_o):
        events = bt_o.events()#using events to check if there is any client connected to the service
        global isConnected
        if  events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
            
            isConnected = True
            pycom.rgbled(0x007f00) # green
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            bt_o.disconnect_client()# in this way other client will have the chance to connect?
            print("Client disconnected")
            isConnected = False
            pycom.rgbled(0x7f0000) # red    
            time.sleep(3)

    bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
    bluetooth.advertise(True)
    print("Started BLE advertising")

    ###########################
    # BLE Ambient Sensor Service
    ###########################
    ambient_sensor_service = bluetooth.service(uuid=b'2222222222222220', isprimary=True, nbr_chars=2) # nbr_chars indicates the number of characteristics of this service
    #set up service characteristic
    ambient_sensor_chr = ambient_sensor_service.characteristic(uuid=b'2222222222222221', properties=Bluetooth.PROP_NOTIFY, value='NA')
    ambient_sensor_sample_rate_chr = ambient_sensor_service.characteristic(uuid=b'2222222222222222', properties=Bluetooth.PROP_WRITE, value='NA')

    def ambient_sensor_sample_rate_cb_handler(chr):
        events = chr.events()
        if  events & Bluetooth.CHAR_WRITE_EVENT:
            print("ambient_sensor_sample_rate_cb_handler : Raw value: {}".format(chr.value()))

            try:
                sample_rate = float(chr.value())
                ambient_sensor.set_sample_rate(sample_rate)
                print("Updated ambient sampling rate: {}".format(sample_rate))
            except:
                print("ambient_sensor_sample_rate_cb_handler : Invalid value. Expected type float.")
                pass
            
    ambient_sensor_sample_rate_chr.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=ambient_sensor_sample_rate_cb_handler)

    ambient_sensor_service.start()

    def ble_ambient_sensor_callback(lux_sample):
        print("Should we notify? : " + str(isConnected))
        # Can take an integer, a string or a bytes object. Can only be called if there clients are connected?
        # Should trigger notification if a client has registered for notifications
        if isConnected:
            try:
                ambient_sensor_chr.value(str(lux_sample)) # Send the notification over BLE
                print("Emitted lux value: " + str(lux_sample))
            except:
                # Some error happened during notification.
                # Most likely no client is connected to receive notifications.
                # Disconnect bluetooth communication.
                bluetooth.disconnect_client()

    threshold = 2 # The threshold of when the ambient sensor should emit new lux values
    ambient_sensor = AmbientSensor(threshold=threshold, callback_on_emit=ble_ambient_sensor_callback)
    _thread.start_new_thread(ambient_sensor.start_sampling, ()) # Start sampling the ambient sensor

    ###########################
    # BLE Light Source Service
    ###########################
    light_source_service = bluetooth.service(uuid=b'3333333333333330', isprimary=True)
    #set up service characteristic
    light_source_chr = light_source_service.characteristic(uuid=b'3333333333333331', properties=Bluetooth.PROP_WRITE, value='(255,255,255)')

    def light_source_chr_cb_handler(chr):
        events = chr.events()
        if  events & Bluetooth.CHAR_WRITE_EVENT:
            colorsArray = chr.value()

            try:
                print("light_source_chr_cb_handler : Raw value: {}".format(chr.value()))
                red = colorsArray[0]
                green = colorsArray[1]
                blue = colorsArray[2]
                print("Set LED with value = {} {} {}".format(red, green, blue))
                set_LED_rgb(red, green, blue)
            except:
                print("light_source_chr_cb_handler : Invalid value. Expected byte array of length 3.")
                pass
            

    light_source_chr.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=light_source_chr_cb_handler)
    light_source_service.start()
    

# Start the BLE server
BLEServer()

