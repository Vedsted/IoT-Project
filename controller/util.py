import math
from config import settings

intensity_max = settings['intensity_max']
intensity_min = settings['intensity_min']

def map_intensity_to_rgb(state):    
    intensity = state['intensity']

    if intensity < intensity_min:
        print('Error: Intensity is below minimum!')
        return (0,0,0)
    elif intensity > intensity_max:
        print('Error: Intensity is above maximum!')
        return (255,255,255)
   
    r = math.floor((state['ref_red']/intensity_max)*intensity)
    g = math.floor((state['ref_green']/intensity_max)*intensity)
    b = math.floor((state['ref_blue']/intensity_max)*intensity)
    return (r,g,b)

def increment_mqtt_message_send_count():
    # Read the current content of the file (if it exists)
    filename = "mqtt_messages_sent_counter.state"
    myfile = open(filename, 'r')
    current_counter = int(myfile.readline())
    myfile.close()
    new_counter = current_counter + 1
    myfile = open(filename, 'w')
    myfile.write(str(new_counter))
    myfile.close()
    return new_counter