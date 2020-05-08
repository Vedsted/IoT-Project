import paho.mqtt.client as mqtt #import the client
import time

############ Call Back #################
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
########################################

broker_address="localhost"
topic="remote/setpoint/test/test"

client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop

client.subscribe(topic)

input()
client.loop_stop() #stop the loop