import math

class Humidity :
    
    def describe_humidity(self, humidity):
        """Convert relative humidity into wet/good/dry description."""
        if 30 < humidity <= 75:
            description = "good"
        elif humidity > 75:
            description = "wet"
        else:
            description = "dry"
        return description

    def adjusted_humidity(self, bme280, comp_hum_quad_a, comp_hum_quad_b, comp_hum_quad_c):
        raw_hum = bme280.get_humidity()
        # comp_hum = comp_hum_slope * raw_hum + comp_hum_intercept
        comp_hum = comp_hum_quad_a * \
            math.pow(raw_hum, 2) + comp_hum_quad_b * raw_hum + comp_hum_quad_c
        return min(100, comp_hum)