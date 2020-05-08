from BLEController import BLEController
from bluepy.btle import DefaultDelegate
import paho.mqtt.client as mqtt
import uuid
import _thread
import time
import json
import util

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
    'setpoint': 2000, # initial setpoint
    'setpoint_error' : 5, # accept a certain error
    'light_red': 0,
    'light_green': 255,
    'light_blue': 255
}

############################
# Current state
############################
current_state = {
    'lux': (float('-inf'), float('-inf')),
    'setpoint': 2000,
    'light_red': 0,
    'light_green': 255,
    'light_blue': 255
}

############################
# MQTT
############################
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code " + str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def mqtt_publish(host, port, keep_alive, topic):
    # connect to broker
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(host, port, keep_alive)

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
    client.publish(topic, payload, qos=0)
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
# Bluetooth Ambient Sensor
############################
#primary_service_uuid = str(uuid.UUID(bytes=b'2222222222222222')) # Primary service UUID of the service that provide lux values
#lux_characteristic_uuid = str(uuid.UUID(bytes=b'3333333333333333')) # The specific characteristic that provides lux values

class AmbientSensorNotificationHandler(DefaultDelegate):
    def __init__(self, params):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        # The specific handle has to be found using service/characteristic discovery in bluez or similar tool
        if cHandle == 42:
            decoded_data = data.decode('utf-8')
            print(decoded_data)
            # Update the current state with the lux tuple
            lux = tuple(map(int, decoded_data.replace('(', '').replace(')', '').split(', '))) # cast from string '(int, int)' -> tuple 
            current_state['lux'] = lux

            # publish current state through MQTT
            topic = 'remote/' + settings['controller_id'] + '/' + settings['group_id'] + '/' + '/data'
            mqtt_publish(settings['broker_address'], settings['broker_port'], settings['broker_keep_alive'], topic)

            adjust_light_source()

f = BLEController(AmbientSensorNotificationHandler(params=None))
f.connect(settings['ambient_sensor_ble_mac']) # Establish the connection to the ambient sensor
current_rgb = (settings['light_red'], settings['light_green'], settings['light_blue'])
f.adjust_light_source(current_rgb)

def AmbientSensorThread():
    f.listen() # Blocking call

############################
# Main program
############################
def block():
    while True:
        print("block() thread")
        time.sleep(1)

def adjust_light_source():
    # TODO: Find a better way to adjust light source
    lux_avg = (current_state['lux'][0] + current_state['lux'][1])/2
    difference = lux_avg - current_state['setpoint']
    current_rgb = (current_state['light_red'], current_state['light_green'], current_state['light_blue'])

    new_rgb = None

    if difference > settings['setpoint_error']:
        # Adjust down
        new_rgb = util.get_rgb_values(current_rgb, 90)
        f.adjust_light_source(new_rgb)
        
    elif difference < settings['setpoint_error']:
        # Adjust up
        new_rgb = util.get_rgb_values(current_rgb, 110)
        f.adjust_light_source(new_rgb)
    else:
        # Don't adjust
        pass

    # Update state of the light source
    print(new_rgb)
    if new_rgb != None:
        current_state['light_red'] = new_rgb[0]
        current_state['light_green'] = new_rgb[1]
        current_state['light_blue'] = new_rgb[2]
    

print("Starting thread: Receive ambient sensor values")
_thread.start_new_thread(AmbientSensorThread, ())

print("Starting thread: MQTT subscribe")
_thread.start_new_thread(mqtt_subscribe_thread, (settings['broker_address'], settings['broker_port'], settings['broker_keep_alive']))

block()