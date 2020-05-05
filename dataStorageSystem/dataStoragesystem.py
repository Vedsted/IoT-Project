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

query = ("SHOW TABLES;")
cursor.execute(query)

for (Tables_in_FilipsBlue) in cursor:
  print(Tables_in_FilipsBlue)