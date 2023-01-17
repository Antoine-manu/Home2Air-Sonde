import time
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559
from bme280 import BME280
from enviroplus import gas
from datetime import datetime
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError

from config.configScript import Config
from controllers.gas import Gas
from controllers.tempertature import Temperature
from controllers.particules import Particules
from controllers.humidity import Humidity
from controllers.altitude import Altitude

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# Init config
config = Config()

# Init classes
gasClass = Gas()
temperatureClass = Temperature()
particuleClass = Particules()
humidityClass = Humidity()
altitudeClass = Altitude()


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


def record_datas():
    gas_in_ppm = gasClass.read_gas_in_ppm(bme280.get_temperature(), round(bme280.get_humidity(), 1), round(bme280.get_pressure(
    ) * altitudeClass.barometer_altitude_comp_factor(altitude, bme280.get_temperature()), 1),
        temperatureClass.adjusted_temperature(bme280, comp_temp_cub_a, comp_temp_cub_b, comp_temp_cub_c, comp_temp_cub_d), humidityClass.adjusted_humidity(bme280, comp_hum_quad_a, comp_hum_quad_b, comp_hum_quad_c), bme280.get_pressure(), False)

    return {"temperature": round(temperatureClass.adjusted_temperature(
        bme280, comp_temp_cub_a, comp_temp_cub_b, comp_temp_cub_c, comp_temp_cub_d), 2),
        "pressure": round(bme280.get_pressure(), 2),
        "humidity": round(humidityClass.adjusted_humidity(
            bme280, comp_hum_quad_a, comp_hum_quad_b, comp_hum_quad_c), 2),
        "light": round(ltr559.get_lux(), 2),
        "reduced": round(gas_in_ppm[0], 2),
        "oxidised": round(gas_in_ppm[1], 2),
        "ammoniac": round(gas_in_ppm[2], 2),
        "particules0": particuleClass.get_particules_values(1.0),
        "particules1": particuleClass.get_particules_values(2.5),
        "particules2": particuleClass.get_particules_values(10),
        "date": str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))}


# Compensation factors for temperature, humidity and air pressure
# Set temp and hum compensation when display is enabled (no weather
