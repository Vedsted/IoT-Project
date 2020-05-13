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

