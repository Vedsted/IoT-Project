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

def lux(light_level):
    # This formula was found on github.
    # Apparently it should be found in Appendix A of the specification of the Ambient sensor.
    # Ambient sensor model: LTR-329ALS-01
    # Link to spec: https://optoelectronics.liteon.com/upload/download/DS86-2014-0006/LTR-329ALS-01_DS_V1.pdf
    # Link to github: https://github.com/pycom/pycom-libraries/issues/97
    # Link to github commit with formula: https://github.com/mcqn/pycom-libraries/commit/3faed579996044865ab9ea84625852782d5cad97 
     ratio = light_level[1]/(light_level[0]+light_level[1])
     if ratio < 0.45:
         return (1.7743 * light_level[0] + 1.1059 * light_level[1]) / settings['ALS_GAIN_VALUE'] / settings['ALS_INT_VALUE']
     elif ratio < 0.64 and ratio >= 0.45:
         return (4.2785 * light_level[0] - 1.9548 * light_level[1]) / settings['ALS_GAIN_VALUE'] / settings['ALS_INT_VALUE']
     elif ratio < 0.85 and ratio >= 0.64:
         return (0.5926 * light_level[0] + 0.1185 * light_level[1]) / settings['ALS_GAIN_VALUE'] / settings['ALS_INT_VALUE']
     else:
         return 0