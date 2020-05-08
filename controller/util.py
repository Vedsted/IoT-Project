import math

def get_rgb_values(rgb, intensity):
# Helper function that returns a tuple with new rgb values depending on the intencity
    def new_channel_value(channel, percentage):
        return  int(math.ceil(channel / 100 * percentage))
    def downscale(greatest_channel_value, channel):
        return int(math.ceil((255/greatest_channel_value * channel)))
    r = new_channel_value(rgb[0], intensity)
    g = new_channel_value(rgb[1], intensity)
    b = new_channel_value(rgb[2], intensity)
    t = (r, g, b)
    if max(t) > 255: # Downscale if any channel is greater than 255
        max(t)
        r = downscale(max(t), r)
        g = downscale(max(t), g)
        b = downscale(max(t), b)
        t = (r, g, b)
    return t