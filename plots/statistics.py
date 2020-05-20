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


grp = 'cc4'
upper = 5
lower = -5
start = datetime(2020, 5, 16, 14)
end = datetime(2020, 5, 20, 15, 30)


##############################################

time_start = int(start.timestamp()) * 1000000000  # 1589911200000 * 1000000
time_end = int(end.timestamp()) * 1000000000  # 1589918400000 * 1000000
query = ("SELECT lux_formula_value, timestamp, setpoint, light_red FROM Measurements "
         "WHERE timestamp >= %s AND timestamp <= %s AND group_id = %s ORDER BY timestamp")
cursor.execute(query, (time_start, time_end, grp))

error = []
time = []
intensity = []

for (lux_formula_value, timestamp, setpoint, light_red) in cursor:
    #print((lux_formula_value, timestamp, setpoint, light_red))
    if light_red == 0 and lux_formula_value > setpoint:
        # Natural light level too high
        continue
    elif abs(lux_formula_value - setpoint) > 25:
        # filter outlier
        continue
    elif light_red == 255 and (lux_formula_value - setpoint) < -10:
        # light source can't illuminate to the given setpoint
        continue
    else:
        # lux above setpoint -> positive error
        error.append(lux_formula_value - setpoint)
        time.append(datetime.fromtimestamp(int(timestamp) // 1000000000))
        intensity.append(light_red)



################# plot ##############3
dates = matplotlib.dates.date2num(time)
fig, ax = plt.subplots()
ax.set_ylabel('Error [Lux]')
error_line, = ax.step(dates, error, label='Error')
ax.xaxis_date()
plt.gcf().autofmt_xdate()
#plt.ylim(top=10, bottom=-10)
ax.set(xlabel='time [MM-dd hh]',
       title='Error over time for group: ' + grp)
ax.grid()
fig.tight_layout()
fig.set_size_inches(10, 5)
plt.show()
####################################

cursor.close()
cnx.close()




print('Group:' + grp + ' in period:' + start.strftime("%m/%d/%Y, %H:%M:%S") + ' to ' +end.strftime("%m/%d/%Y, %H:%M:%S"))
print('number of obs: ' + str(len(error)))
print('SD: ' + str(np.std(error)))
print('Avg: ' + str(np.average(error)))
print('Median: ' + str(np.median(error)))


arr = np.sort(error)
p = np.diff(arr.searchsorted([-2, 2]))[0]/arr.size
print('percentage of values between [' +str(lower) + '-' + str(upper)+']: ' + str(p))
