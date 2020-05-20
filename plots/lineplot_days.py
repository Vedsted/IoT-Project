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

for i in range(16, 20):

    # first obs - last obs
    time_start = int(datetime(2020,5,i,22,40).timestamp()) * 1000000000 #1589911200000 * 1000000
    time_end = int(datetime(2020,5,i,22,50).timestamp()) * 1000000000#1589918400000 * 1000000
    query = ("SELECT lux_formula_value, timestamp, setpoint, light_red FROM Measurements "
             "WHERE timestamp >= %s AND timestamp <= %s AND group_id = 'cc4' ORDER BY timestamp")
    cursor.execute(query, (time_start, time_end))

    luxs = []
    timestamps = []
    dto = []
    setpoints = []
    intensity = []

    for (lux_formula_value, timestamp, setpoint, light_red) in cursor:
        luxs.append(lux_formula_value)
        timestamps.append(timestamp)
        setpoints.append(setpoint)
        dto.append(datetime.fromtimestamp(int(timestamp) // 1000000000))
        intensity.append(light_red)

    # convert dto to matplotlib dates
    dates = matplotlib.dates.date2num(dto)

    fig, ax = plt.subplots()

    ################# LUX VALUES AND SETPOINT ##############3
    color = 'tab:blue'
    lux_line, = ax.step(dates, luxs, color=color, label='Lux')
    setpoint_line, = ax.step(dates, setpoints, color='black', dashes=[6, 2], label="Setpoint")
    ax.xaxis_date()
    plt.gcf().autofmt_xdate()
    plt.ylim(top=150, bottom=100)
    ax.set(xlabel='time (ns)', ylabel='Lux',
           title='Lux values over time')
    ax.grid()



    ################# INTENSITY ######################
    ax2 = ax.twinx()
    color = 'tab:red'
    ax2.set_ylabel('intensity', color=color)  # we already handled the x-label with ax1
    intensity_line, = ax2.step(dates, intensity, color=color, label='Intensity')
    ax2.tick_params(axis='y', labelcolor=color)
    plt.ylim(top=265, bottom=-10)
    plt.yticks(np.arange(0, 260, 25))

    #####################################################
    #fig.savefig("test.png")

    #fig.legend(loc='upper left')
    plt.legend(handles=[lux_line, setpoint_line, intensity_line], bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    fig.tight_layout()
    fig.set_size_inches(13, 8)
    plt.show()



cursor.close()
cnx.close()