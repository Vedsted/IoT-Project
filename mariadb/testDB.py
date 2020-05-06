import mysql.connector
from configparser import ConfigParser # Used for reading config file

config = ConfigParser()
config.read('./config.conf')

user        = config.get('database', 'user')
password    = config.get('database', 'password')
host        = config.get('database', 'host')
database    = config.get('database', 'database')

print("user: " + user)
print("password: " + password)
print("host: " + host)
print("database: " + database)

cnx = mysql.connector.connect(
                              user=user, 
                              password=password,
                              host=host,
                              database=database
                            )

cursor = cnx.cursor()

#query = ("SHOW TABLES;")
#cursor.execute(query)
#
#for (Tables_in_FilipsBlue) in cursor:
#    print(Tables_in_FilipsBlue)



def insertTest():
    controller = 'jonas_cnt'
    group = 'jonas_grp'
    time = 255
    lux1 = 255
    lux2 = 255
    setpoint = 255
    red = 255
    green = 255
    blue = 255

    query = "insert ignore into Controllers (id) values (%s);"
    cursor.execute(query, (controller,))
    print('1: ' + str(cursor.description))

    query = "insert ignore into `Groups` (id, controller_id) VALUES (%s, %s);"
    cursor.execute(query, (group, controller))
    print('2: ' + str(cursor.description))

    query = "insert into Measurements (group_id, timestamp, lux1, lux2, setpoint, light_red, light_green, light_blue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(query, (group, time, lux1, lux2, setpoint, red, green, blue))
    print('3: ' + str(cursor.description))

    cnx.commit()


insertTest()