import paho.mqtt.client as mqtt #import the client
import time
import json

message = """{
    "controller": "broker_test", 
    "group": "broker_test", 
    "timestamp": 1234, 
    "lux1":255, 
    "lux2":255, 
    "setpoint":255,
    "light_red":3,
    "light_green":0,
    "light_blue":100
    }"""


broker_address="localhost"
topic = "test/test"

client = mqtt.Client("test")
client.connect(broker_address, port=1883)
client.loop_start()

print("Publishing message to topic","test/test")
client.publish(topic,message)

time.sleep(4) # wait
client.loop_stop() #stop the loop