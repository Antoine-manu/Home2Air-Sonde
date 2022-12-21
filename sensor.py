import json
import math
import redis
import time
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
from bme280 import BME280
from enviroplus import gas
from datetime import datetime
from config.configScript import Config

#Init config
config = Config()

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()


class Datas:
    def __init__(self, temperature, pressure, humidity, light, oxidised, reduced, nh3):
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity
        self.light = light
        self.oxidised = oxidised
        self.reduced = reduced
        self.nh3 = nh3


# Config Setup
(temp_offset, altitude, enable_display, enable_adafruit_io, aio_user_name, aio_key, aio_feed_window,
 aio_feed_sequence, aio_household_prefix, aio_location_prefix, aio_package, enable_send_data_to_homemanager,
 enable_receive_data_from_homemanager, enable_indoor_outdoor_functionality,
 mqtt_broker_name, mqtt_username, mqtt_password, outdoor_source_type, outdoor_source_id, enable_noise, enable_luftdaten,
 enable_luftdaten_noise, disable_luftdaten_sensor_upload, enable_climate_and_gas_logging, enable_particle_sensor,
 enable_eco2_tvoc, gas_daily_r0_calibration_hour, reset_gas_sensor_calibration, incoming_temp_hum_mqtt_topic,
 incoming_temp_hum_mqtt_sensor_name, incoming_barometer_mqtt_topic, incoming_barometer_sensor_id,
 indoor_outdoor_function, mqtt_client_name, outdoor_mqtt_topic, indoor_mqtt_topic) = Config.retrieve_config()

if enable_particle_sensor:
    # Create a PMS5003 instance
    pms5003 = PMS5003()
    time.sleep(1)

red_temp_comp_factor = -0.015
red_hum_comp_factor = 0.0125
red_bar_comp_factor = -0.0053
oxi_temp_comp_factor = -0.017
oxi_hum_comp_factor = 0.0115
oxi_bar_comp_factor = -0.0072
nh3_temp_comp_factor = -0.02695
nh3_hum_comp_factor = 0.0094
nh3_bar_comp_factor = 0.003254


if enable_display and not enable_eco2_tvoc:
    # protection cover in place) and no ECO2 or TVOC sensor is in place
    # Cubic polynomial temp comp coefficients adjusted by config's temp_offset
    comp_temp_cub_a = -0.0001
    comp_temp_cub_b = 0.0037
    comp_temp_cub_c = 1.00568
    comp_temp_cub_d = -6.78291
    comp_temp_cub_d = comp_temp_cub_d + temp_offset
    # Quadratic polynomial hum comp coefficients
    comp_hum_quad_a = -0.0032
    comp_hum_quad_b = 1.6931
    comp_hum_quad_c = 0.9391
# Set temp and hum compensation when display is enabled (no weather
elif enable_display and enable_eco2_tvoc:
    # protection cover in place) and ECO2 or TVOC sensor is in place
    comp_temp_cub_a = -0.00005
    comp_temp_cub_b = 0.00563
    comp_temp_cub_c = 0.76548
    comp_temp_cub_d = -5.2795
    comp_temp_cub_d = comp_temp_cub_d + temp_offset
    # Quadratic polynomial hum comp coefficients
    comp_hum_quad_a = -0.0047
    comp_hum_quad_b = 2.1582
    comp_hum_quad_c = -3.8446
# Set temp and hum compensation when display is disabled (weather protection cover in place)
else:
    # Cubic polynomial temp comp coefficients adjusted by config's temp_offset
    comp_temp_cub_a = 0.00033
    comp_temp_cub_b = -0.03129
    comp_temp_cub_c = 1.8736
    comp_temp_cub_d = -14.82131
    comp_temp_cub_d = comp_temp_cub_d + temp_offset
    # Quadratic polynomial hum comp coefficients
    comp_hum_quad_a = -0.0221
    comp_hum_quad_b = 3.3824
    comp_hum_quad_c = -25.8102


def describe_humidity(humidity):
    """Convert relative humidity into wet/good/dry description."""
    if 30 < humidity <= 75:
        description = "good"
    elif humidity > 75:
        description = "wet"
    else:
        description = "dry"
    return description


def adjusted_temperature():
    raw_temp = bme280.get_temperature()
    # comp_temp = comp_temp_slope * raw_temp + comp_temp_intercept
    comp_temp = (comp_temp_cub_a * math.pow(raw_temp, 3) + comp_temp_cub_b * math.pow(raw_temp, 2) +
                 comp_temp_cub_c * raw_temp + comp_temp_cub_d)
    return comp_temp


def get_particules_values(diameter):
    try:
        data = pms5003.read()
    except pmsReadTimeoutError:
        print("Failed to read PMS5003")
    else:
        return float(data.pm_ug_per_m3(diameter))


def adjusted_humidity():
    raw_hum = bme280.get_humidity()
    # comp_hum = comp_hum_slope * raw_hum + comp_hum_intercept
    comp_hum = comp_hum_quad_a * \
        math.pow(raw_hum, 2) + comp_hum_quad_b * raw_hum + comp_hum_quad_c
    return min(100, comp_hum)


def barometer_altitude_comp_factor(alt, temp):
    comp_factor = math.pow(
        1 - (0.0065 * altitude/(temp + 0.0065 * alt + 273.15)), -5.257)
    return comp_factor


def record_datas():
    # Connect to the Redis server
    r = redis.Redis(host='localhost', port=6379, db=1)
    date = str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

# Create a stream with the name "mystream"
    gas_in_ppm = read_gas_in_ppm(bme280.get_temperature(), round(bme280.get_humidity(), 1), round(bme280.get_pressure(
    ) * barometer_altitude_comp_factor(altitude, bme280.get_temperature()), 1),
        adjusted_temperature(), adjusted_humidity(), bme280.get_pressure(), False)
    print(describe_humidity(round(adjusted_humidity(), 2)))
    results = []
    results.append(round(adjusted_temperature(), 2))
    results.append(round(bme280.get_pressure(), 2))
    results.append(round(adjusted_humidity(), 2))
    results.append(round(ltr559.get_lux(), 2))
    results.append(round(gas_in_ppm[0], 2))
    results.append(round(gas_in_ppm[1], 2))
    results.append(round(gas_in_ppm[2], 2))
    results.append(round(get_particules_values(1.0)))
    results.append(round(get_particules_values(2.5)))
    results.append(round(get_particules_values(10)))
    results.append(date)
    r.xadd('mystream', {'mylist': json.dumps(results)})
    return results


# Compensation factors for temperature, humidity and air pressure
# Set temp and hum compensation when display is enabled (no weather
