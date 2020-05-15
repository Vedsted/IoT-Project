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
initial_rgb = (settings['light_red'], settings['light_green'], settings['light_blue'])
current_state = {
    'lux': settings['lux'],
    'lux_formula_value': settings['lux'],
    'setpoint': settings['setpoint'],
    'setpoint_error': settings['setpoint_error'],
    'light_red': initial_rgb[0],
    'light_green': initial_rgb[1],
    'light_blue': initial_rgb[2],
    'ref_red': initial_rgb[0], # ref values are for adjusting intensity accordingly to the color 
    'ref_green': initial_rgb[1],
    'ref_blue': initial_rgb[2],
    'intensity': settings['intensity_max']
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
        u"lux_formula_value": current_state['lux_formula_value'],
        u"setpoint": current_state['setpoint'],
        u"setpoint_error": current_state['setpoint_error'],
        u"light_red": current_state['light_red'],
        u"light_green": current_state['light_green'],
        u"light_blue": current_state['light_blue'],
        u"message_count": util.increment_mqtt_message_send_count()
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
        setpoint = int(payload['setpoint'])
        current_state['setpoint'] = setpoint
    elif msg.topic == base_mqtt_topic+'rgb':
        current_state['ref_red'] = int(payload['red'])
        current_state['ref_green'] = int(payload['green'])
        current_state['ref_blue'] = int(payload['blue'])
        new_rgb = util.map_intensity_to_rgb(current_state)
        f.adjust_light_source(new_rgb)
    elif msg.topic == base_mqtt_topic+'setpoint_error':
        current_state['setpoint_error'] = int(payload['setpoint_error'])

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
    client.on_connect = subscribe([
        (base_mqtt_topic + 'rgb', 0), 
        (base_mqtt_topic + 'setpoint', 0), 
        (base_mqtt_topic + 'setpoint_error', 0)
    ])
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

            adjust_light_source()

            # publish current state through MQTT
            topic = base_mqtt_topic + 'data'
            try:
                mqtt_publish(settings['broker_address'], settings['broker_port'], settings['broker_keep_alive'], topic)
            except:
                # Accept that we might get an error.
                # A few lost messages are not critical.
                # Do not try to send the same message again.
                print("An error occured while trying to publish to MQTT broker.")


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
    lux = util.lux(current_state['lux'])
    current_state['lux_formula_value'] = lux
    difference = lux - current_state['setpoint']

    new_rgb = None

    if difference > current_state['setpoint_error']:
        # Adjust down
        #new_rgb = util.get_rgb_values(current_rgb, 95)
        if current_state['intensity'] > settings['intensity_min']:
            current_state['intensity'] = current_state['intensity'] -1
            new_rgb = util.map_intensity_to_rgb(current_state)
            f.adjust_light_source(new_rgb)
        
    elif difference < current_state['setpoint_error']:
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