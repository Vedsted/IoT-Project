import mysql.connector
import paho.mqtt.client as mqtt
import json
import time
from configparser import ConfigParser # Used for reading config file

# Wait for broker and db to be ready
time.sleep(30)

# Load configs
config = ConfigParser()
config.read('/config.conf')

# Set up database connection
def connect_to_db():
  user        = config.get('database', 'user')
  password    = config.get('database', 'password')
  host        = config.get('database', 'host')
  database    = config.get('database', 'database')
  return mysql.connector.connect(
                                user=user, 
                                password=password,
                                host=host,
                                database=database
                              )

# callback when messages are received from the broker
def on_message(client, userdata, message):
  msg = json.loads(message.payload.decode("utf-8"))
  # Lines below can be included in recieved messages should be shown
  # print("\nmessage received from "+msg['controller']+"!")
  # print("topic= ",message.topic)

  controller = msg['controller']
  group = msg['group']

  # Create controller if missing
  query = "insert ignore into Controllers (id) values (%s);"
  cursor.execute(query, (controller,))
  # Create group if missing
  query = "insert ignore into `Groups` (id, controller_id) VALUES (%s, %s);"
  cursor.execute(query, (group, controller))
  # Insert message
  query = "insert into Measurements (group_id, timestamp, lux1, lux2, setpoint, light_red, light_green, light_blue, message_count) VALUES (%s, %i, %i, %i, %i, %i, %i, %i, %i);"
  cursor.execute(query, (group, msg['timestamp'], msg['lux1'], msg['lux2'], msg['setpoint'], msg['light_red'], msg['light_green'], msg['light_blue'], msg['message_count']))
  # Commit the changes
  db.commit()

# Set up broker connection
def connect_to_broker():
  client_id   = config.get('mqtt', 'id')
  user        = config.get('mqtt', 'user')
  password    = config.get('mqtt', 'password')
  host        = config.get('mqtt', 'host')
  port        = int(config.get('mqtt', 'port'))
  topic       = config.get('mqtt', 'topic')

  # Displys configurations
  # print(client_id) print(user) print(password) print(host) print(port) print(topic)

  client = mqtt.Client(client_id)
  client.on_message = on_message # on message callback

  #client.username_pw_set('filip', 'Chcla15Jonso16') #user_pass currently not used
  client.connect(host, port=port)
  client.loop_start() #start the loop (shoud be done before subscribing)  

  client.subscribe(topic)
  return client


#Start data storage system
db = connect_to_db()
cursor = db.cursor()
broker = connect_to_broker()

print('Storage system ready!')
while True:
  time.sleep(30)
