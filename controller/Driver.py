from BLEController import BLEController
from bluepy.btle import DefaultDelegate
import paho.mqtt.client as mqtt
import uuid
import _thread
import time
import json
import util
from config import settings

############################
# Current state
############################
current_state = {
    'lux': (float('-inf'), float('-inf')),
    'setpoint': 50,
    'light_red': 255,
    'light_green': 255,
    'light_blue': 255,
    'intensity': 0
}

base_mqtt_topic = 'remote/' + settings['controller_id'] + '/' + settings['group_id'] + '/'

############################
# MQTT
############################
def on_connect(client, userdata, flags, rc):
    print("on_connect() -> Connected to MQTT with result code " + str(rc))


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
    print("mqtt_publish() -> Published MQTT message: {}".format(payload))

    client.disconnect()


def on_msg(client, userdata, msg):
    print("on_msg() -> Received MQTT message..")
    payload = json.loads(msg.payload)

    if msg.topic == base_mqtt_topic+'setpoint':
        setpoint = payload['setpoint']
        current_state['setpoint'] = setpoint
    elif msg.topic == base_mqtt_topic+'rgb':
        current_state['light_red'] = payload['red']
        current_state['light_green'] = payload['green']
        current_state['light_blue'] = payload['blue']
        new_rgb = util.map_intensity_to_rgb(current_state)
        f.adjust_light_source(new_rgb)

    print("on_msg() -> Updated current state: {}".format(payload))

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
    client.on_connect = subscribe([base_mqtt_topic + 'rgb', base_mqtt_topic + 'setpoint'])
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
            print("AmbientSensorNotificationHandler.handleNotification() -> received lux values: " + decoded_data)
            # Update the current state with the lux tuple
            lux = tuple(map(int, decoded_data.replace('(', '').replace(')', '').split(', '))) # cast from string '(int, int)' -> tuple 
            current_state['lux'] = lux

            # publish current state through MQTT
            topic = base_mqtt_topic + 'data'
            mqtt_publish(settings['broker_address'], settings['broker_port'], settings['broker_keep_alive'], topic)

            adjust_light_source()

f = BLEController(AmbientSensorNotificationHandler(params=None))
f.connect(settings['ambient_sensor_ble_mac']) # Establish the connection to the ambient sensor
initial_rgb = (settings['light_red'], settings['light_green'], settings['light_blue'])
f.adjust_light_source(initial_rgb)

def AmbientSensorThread():
    f.listen() # Blocking call

############################
# Main program
############################
def block():
    while True:
        print("block()")
        time.sleep(5)


def adjust_light_source():
    # TODO: Find a better way to adjust light source
    lux_avg = (current_state['lux'][0] + current_state['lux'][1])/2
    difference = lux_avg - current_state['setpoint']
    current_rgb = (current_state['light_red'], current_state['light_green'], current_state['light_blue'])

    new_rgb = None

    

    if difference > settings['setpoint_error']:
        # Adjust down
        #new_rgb = util.get_rgb_values(current_rgb, 95)
        if current_state['intensity'] > settings['intensity_min']:
            current_state['intensity'] = current_state['intensity'] -1
            new_rgb = util.map_intensity_to_rgb(current_state)
            f.adjust_light_source(new_rgb)
        
        
    elif difference < settings['setpoint_error']:
        # Adjust up
        #new_rgb = util.get_rgb_values(current_rgb, 105)
        if current_state['intensity'] < settings['intensity_max']:
            current_state['intensity'] = current_state['intensity'] +1
            new_rgb = util.map_intensity_to_rgb(current_state)
            f.adjust_light_source(new_rgb)
    else:
        # Don't adjust
        pass

    # Update state of the light source
    print("adjust_light_source() -> " + str(new_rgb))
    if new_rgb != None:
        current_state['light_red'] = new_rgb[0]
        current_state['light_green'] = new_rgb[1]
        current_state['light_blue'] = new_rgb[2]
    

print("Starting thread: Receive ambient sensor values")
_thread.start_new_thread(AmbientSensorThread, ())

print("Starting thread: MQTT subscribe")
_thread.start_new_thread(mqtt_subscribe_thread, (settings['broker_address'], settings['broker_port'], settings['broker_keep_alive']))

block()