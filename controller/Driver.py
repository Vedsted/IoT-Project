from BLEController import BLEController
from bluepy.btle import DefaultDelegate
import paho.mqtt.client as mqtt
import uuid
import _thread
import time
import util
import json

############################
# Controller settings
############################
settings = {
    'controller_id': 'controller1',
    'group_id': 'group1',
    'lux': (float('-inf'), float('-inf')),
    'setpoint': 400,
    'light_red': 255,
    'light_green': 255,
    'light_blue': 255
}

############################
# Current state
############################
current_state = {
    'lux': (float('-inf'), float('-inf')),
    'setpoint': 400,
    'light_red': 255,
    'light_green': 255,
    'light_blue': 255
}

############################
# Bluetooth Ambient Sensor
############################
server_ambient_sensor_mac = '30:AE:A4:50:5D:2A' # MAC of the ambient light sensor
#primary_service_uuid = str(uuid.UUID(bytes=b'2222222222222222')) # Primary service UUID of the service that provide lux values
#lux_characteristic_uuid = str(uuid.UUID(bytes=b'3333333333333333')) # The specific characteristic that provides lux values

class AmbientSensorNotificationHandler(DefaultDelegate):
    def __init__(self, params):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        # The specific handle has to be found using service/characteristic discovery in bluez or similar tool
        if cHandle == 42: 
            print(data.decode('utf-8'))

def AmbientSensorThread():
    f = BLEController(AmbientSensorNotificationHandler(params=None))
    f.connect(server_ambient_sensor_mac) # Establish the connection to the ambient sensor
    f.listen() # Blocking call

############################
# Bluetooth Light Source
############################


############################
# MQTT
############################
broker_address="localhost"
broker_port = 1883
broker_keep_alive = 60 # seconds

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code " + str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def mqtt_publish_thread(host, port, keep_alive):
    # connect to broker
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(host, port, keep_alive)

    while True:

        if shouldPublish:
            # Timestamp in ns
            timestamp = time.time_ns()

            # MQTT payload
            payload = json.dumps({
                u"controller": settings['controller_id'],
                u"group": settings['group_id'],
                u"timestamp": timestamp,
                u"lux1": current_state['lux'][0],
                u"lux2": current_state['lux'][1],
                u"setpoint": current_state['setpoint'],
                u"light_red": current_state['light_red'],
                u"light_green": current_state['light_green'],
                u"light_blue": current_state['light_blue']
            })

            # Publish to mylaptop/uptime
            client.publish("filipsblue/controllers/" + settings['controller_id'] + "/current", payload, qos=0)
                                                            # QoS0 -> deliver no more than once without receipt
                                                            # QoS1 -> is delivered as often as necessary until the subscriber has confirmed receipt
                                                            # QoS2 -> ensures that the subscriber receives the message exactly once


def on_msg(client, userdata, msg):
    print("Received MQTT message..")

    #payload = json.loads(msg.payload)
    #setpoint = payload['setpoint']

# Wrapper function for returning the expected callback given the topic
def subscribe(topic):
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(topic) # for example: "$SYS/broker/uptime"

    return on_connect # Return the function..

def mqtt_subscribe_thread(host, port, keep_alive):
    # connect to broker
    client = mqtt.Client()
    client.on_connect = subscribe("filipsblue/controllers/" + settings['controller_id'] + "/setting")
    client.on_message = on_msg
    client.connect(host, port, keep_alive)
    client.loop_forever()

############################
# Main program
############################
def block():
    while True:
        print("Keep alive..")
        time.sleep(1)

print("Starting thread: Receive ambient sensor values")
_thread.start_new_thread(AmbientSensorThread, ())

print("Starting thread: MQTT publish")
_thread.start_new_thread(mqtt_publish_thread, (broker_address, broker_port, broker_keep_alive))

print("Starting thread: MQTT subscribe")
_thread.start_new_thread(mqtt_subscribe_thread, (broker_address, broker_port, broker_keep_alive))

block()