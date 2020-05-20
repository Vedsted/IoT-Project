import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
from datetime import datetime
from configparser import ConfigParser # Used for reading config file

############### DB Connection ##################
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
date=19
start = datetime(2020, 5, 16, 12)
end = datetime(2020, 5, 20, 16, 30)


#################### QUERY DATA #######################

time_start = int(start.timestamp()) * 1000000000  # 1589911200000 * 1000000
time_end = int(end.timestamp()) * 1000000000  # 1589918400000 * 1000000
query = ("SELECT lux_formula_value, timestamp, setpoint, light_red FROM Measurements "
         "WHERE timestamp >= %s AND timestamp <= %s AND group_id = %s ORDER BY timestamp")
cursor.execute(query, (time_start, time_end, grp))


################### PREPARE DATA #######################
error = []
time = []
intensity = []

# Extract from query result
for (lux_formula_value, timestamp, setpoint, light_red) in cursor:
    #print((lux_formula_value, timestamp, setpoint, light_red))
    if light_red == 0 and lux_formula_value > setpoint:
        # Natural light level too high
        continue
    elif abs(lux_formula_value - setpoint) > 10:
        # Outliers
        continue
    else:
        # lux above setpoint -> positive error
        error.append(lux_formula_value - setpoint)
        time.append(datetime.fromtimestamp(int(timestamp) // 1000000000))
        intensity.append(light_red)

# convert python date objects to matplotlib dates
dates = matplotlib.dates.date2num(time)

fig, ax = plt.subplots()

################# eroor ##############3
color = 'tab:blue'
ax.set_ylabel('Error [Lux]', color=color)
error_line, = ax.step(dates, error, color=color, label='Error')
ax.xaxis_date()
plt.gcf().autofmt_xdate()
plt.ylim(top=10, bottom=-10)
ax.set(xlabel='time [MM-dd hh]',
       title='Error over time for group: ' + grp)
ax.grid()

################# INTENSITY ######################
ax2 = ax.twinx()
color = 'tab:red'
ax2.set_ylabel('Intensity [0-255]', color=color)  # we already handled the x-label with ax1
intensity_line, = ax2.step(dates, intensity, color=color, label='Intensity')
#ax2.tick_params(axis='y', labelcolor=color)
plt.ylim(top=265, bottom=-10)
plt.yticks(np.arange(0, 260, 25))

#####################################################
# fig.savefig("test.png")

# fig.legend(loc='upper left')
plt.legend(handles=[error_line, intensity_line], bbox_to_anchor=(1.05, 1), loc='upper left',
           borderaxespad=0.)
fig.tight_layout()
fig.set_size_inches(20, 5)
plt.savefig("lineplots/lineplot_" + grp + "_" + str(start.year) + '-' + str(start.month) + '-' + str(start.day)  +".svg", bbox_inches = "tight") # 'tight' makes room for x-axis labels
plt.show()  # Must be called last since this clears the figure, resulting in a white svg.

cursor.close()
cnx.close()

print('number of obs: ' + str(len(error)))
print('SD: ' + str(np.std(error)))
print('Avg: ' + str(np.average(error)))




np.histogram(error)
fig, ax = plt.subplots()
n, bins, patches = ax.hist(error, range(-10, 11, 2))
ax.set(xlabel='Error [Lux]', ylabel='Frequency',
       title='Lux error distribution for group: ' + grp)
fig.tight_layout()
fig.set_size_inches(5, 5)
plt.savefig("lineplots/lineplot_" + grp + "_" + str(start.year) + '-' + str(start.month) + '-' + str(start.day)  +"_hist.svg", bbox_inches = "tight") # 'tight' makes room for x-axis labels
plt.show()
