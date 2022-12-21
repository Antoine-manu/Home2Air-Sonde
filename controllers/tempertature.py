import math

class Temperature :
    def adjusted_temperature(bme280, comp_temp_cub_a, comp_temp_cub_b, comp_temp_cub_c ,comp_temp_cub_d):
        raw_temp = bme280.get_temperature()
        # comp_temp = comp_temp_slope * raw_temp + comp_temp_intercept
        comp_temp = (comp_temp_cub_a * math.pow(raw_temp, 3) + comp_temp_cub_b * math.pow(raw_temp, 2) +
                    comp_temp_cub_c * raw_temp + comp_temp_cub_d)
        return comp_temp