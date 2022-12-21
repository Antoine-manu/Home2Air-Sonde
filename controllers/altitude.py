import math

class Altitude :
    def barometer_altitude_comp_factor(alt, temp, altitude):
        comp_factor = math.pow(
            1 - (0.0065 * altitude/(temp + 0.0065 * alt + 273.15)), -5.257)
        return comp_factor