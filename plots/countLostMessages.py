import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
from datetime import datetime
from configparser import ConfigParser # Used for reading config file

config = ConfigParser()
config.read('config.conf')

user        = config.get('database', 'user')
password    = config.get('database', 'password')
host        = config.get('database', 'host')
database    = config.get('database', 'database')

cnx = mysql.connector.connect(user=user, password=password,
                              host=host,
                              database=database)

cursor = cnx.cursor()

############# CONFIGS ########################

grp = 'cc4'
start = datetime(2020, 5, 16, 12)
end = datetime(2020, 5, 20, 16)

#################### QUERY DATA #######################

time_start = int(start.timestamp()) * 1000000000  # 1589911200000 * 1000000
time_end = int(end.timestamp()) * 1000000000  # 1589918400000 * 1000000
query = ("SELECT message_count FROM Measurements "
         "WHERE timestamp >= %s AND timestamp <= %s AND group_id = %s ORDER BY message_count")
cursor.execute(query, (time_start, time_end, grp))

################### PREPARE DATA #######################
missing = []
expected = 0


# Extract from query result
for (message_count,) in cursor:
    if message_count == expected:
        expected = expected +1
        continue
    else:
        while expected <= message_count:
            # The expected matching is not missing
            if message_count != expected:
                missing.append(expected)
            expected = expected +1

print('Total number of messages: ' + str(expected-1))
print('Number of missing messages: ' + str(len(missing)))
print('Percentage of messages lost: ' + str(len(missing)/(expected-1.)*100))