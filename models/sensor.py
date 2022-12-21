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


def retrieve_config():
    try:
        with open('../config/config.json', 'r') as f:
            parsed_config_parameters = json.loads(f.read())
            print('Retrieved Config', parsed_config_parameters)
    except IOError:
        print('Error retrieved config')
    temp_offset = parsed_config_parameters['temp_offset']
    altitude = parsed_config_parameters['altitude']
    # Enables the display and flags that the
    enable_display = parsed_config_parameters['enable_display']
    # weather protection cover is used with different temp/hum compensation
    enable_adafruit_io = parsed_config_parameters['enable_adafruit_io']
    aio_user_name = parsed_config_parameters['aio_user_name']
    aio_key = parsed_config_parameters['aio_key']
    aio_feed_window = parsed_config_parameters['aio_feed_window']
    aio_feed_sequence = parsed_config_parameters['aio_feed_sequence']
    aio_household_prefix = parsed_config_parameters['aio_household_prefix']
    aio_location_prefix = parsed_config_parameters['aio_location_prefix']
    aio_package = parsed_config_parameters['aio_package']
    enable_send_data_to_homemanager = parsed_config_parameters['enable_send_data_to_homemanager']
    enable_receive_data_from_homemanager = parsed_config_parameters[
        'enable_receive_data_from_homemanager']
    enable_indoor_outdoor_functionality = parsed_config_parameters[
        'enable_indoor_outdoor_functionality']
    mqtt_broker_name = parsed_config_parameters['mqtt_broker_name']
    enable_luftdaten = parsed_config_parameters['enable_luftdaten']
    enable_climate_and_gas_logging = parsed_config_parameters['enable_climate_and_gas_logging']
    enable_particle_sensor = parsed_config_parameters['enable_particle_sensor']
    if 'enable_eco2_tvoc' in parsed_config_parameters:
        enable_eco2_tvoc = parsed_config_parameters['enable_eco2_tvoc']
    else:
        enable_eco2_tvoc = False
    if 'gas_daily_r0_calibration_hour' in parsed_config_parameters:
        gas_daily_r0_calibration_hour = parsed_config_parameters['gas_daily_r0_calibration_hour']
    else:
        gas_daily_r0_calibration_hour = 3
    if 'reset_gas_sensor_calibration' in parsed_config_parameters:
        reset_gas_sensor_calibration = parsed_config_parameters['reset_gas_sensor_calibration']
    else:
        reset_gas_sensor_calibration = False
    if 'mqtt_username' in parsed_config_parameters:
        mqtt_username = parsed_config_parameters['mqtt_username']
    else:
        mqtt_username = None
    if 'mqtt_password' in parsed_config_parameters:
        mqtt_password = parsed_config_parameters['mqtt_password']
    else:
        mqtt_password = None
    if 'outdoor_source_type' in parsed_config_parameters:
        # Can be "Enviro", "Luftdaten"
        outdoor_source_type = parsed_config_parameters['outdoor_source_type']
        # or "Adafruit IO"
    else:
        outdoor_source_type = 'Enviro'
    if 'outdoor_source_id' in parsed_config_parameters:
        # Sets Luftdaten or Adafruit IO Sensor IDs
        outdoor_source_id = parsed_config_parameters['outdoor_source_id']
        # if using those sensors for outdoor readings, with the format: {"Climate": id, "PM": id} for Luftdaten or
        # {"User Name": "<aio_user_name>", "Key": "<aio_key>", "Household Name": "<aio_household_name>"} for Adafruit IO
    else:
        outdoor_source_id = {}
    if 'enable_noise' in parsed_config_parameters:  # Enables Noise level sensing
        enable_noise = parsed_config_parameters['enable_noise']
    else:
        enable_noise = False
    # Enables Noise level uploads to Luftdaten. enable_noise must also be set to true for this to work
    if 'enable_luftdaten_noise' in parsed_config_parameters:
        enable_luftdaten_noise = parsed_config_parameters['enable_luftdaten_noise']
    else:
        enable_luftdaten_noise = False
    # Luftdaten currently only supports two sensors per node
    if 'disable_luftdaten_sensor_upload' in parsed_config_parameters:
        # When enable_luftdaten_noise is true, this must be set to either 'Climate' to disable climate reading uploads or 'PM' to disable air particle reading uploads
        # Set to 'None' when enable_luftdaten_noise is false
        disable_luftdaten_sensor_upload = parsed_config_parameters[
            'disable_luftdaten_sensor_upload']
    else:
        disable_luftdaten_sensor_upload = 'None'
    # Correct any Luftdaten Noise misconfigurations
    if not enable_noise:
        disable_luftdaten_sensor_upload = 'None'
        if enable_luftdaten_noise:
            print(
                'Noise sensor must be enabled in order to enable Luftdaten Noise. Disabling Luftdaten Noise')
            enable_luftdaten_noise = False
    else:
        if enable_luftdaten_noise and disable_luftdaten_sensor_upload == 'None':
            # Comment out next two lines once Luftdaten supports three sensors per node
            print('Luftdaten currently only supports two sensors and three have been enabled. Disabling Luftdaten Climate uploads')
            disable_luftdaten_sensor_upload = 'Climate'
            pass
    incoming_temp_hum_mqtt_topic = parsed_config_parameters['incoming_temp_hum_mqtt_topic']
    incoming_temp_hum_mqtt_sensor_name = parsed_config_parameters[
        'incoming_temp_hum_mqtt_sensor_name']
    incoming_barometer_mqtt_topic = parsed_config_parameters['incoming_barometer_mqtt_topic']
    incoming_barometer_sensor_id = parsed_config_parameters['incoming_barometer_sensor_id']
    indoor_outdoor_function = parsed_config_parameters['indoor_outdoor_function']
    mqtt_client_name = parsed_config_parameters['mqtt_client_name']
    outdoor_mqtt_topic = parsed_config_parameters['outdoor_mqtt_topic']
    indoor_mqtt_topic = parsed_config_parameters['indoor_mqtt_topic']
    return (temp_offset, altitude, enable_display, enable_adafruit_io, aio_user_name, aio_key, aio_feed_window,
            aio_feed_sequence, aio_household_prefix, aio_location_prefix, aio_package, enable_send_data_to_homemanager,
            enable_receive_data_from_homemanager, enable_indoor_outdoor_functionality,
            mqtt_broker_name, mqtt_username, mqtt_password, outdoor_source_type, outdoor_source_id, enable_noise, enable_luftdaten,
            enable_luftdaten_noise, disable_luftdaten_sensor_upload, enable_climate_and_gas_logging, enable_particle_sensor,
            enable_eco2_tvoc, gas_daily_r0_calibration_hour, reset_gas_sensor_calibration, incoming_temp_hum_mqtt_topic,
            incoming_temp_hum_mqtt_sensor_name, incoming_barometer_mqtt_topic, incoming_barometer_sensor_id,
            indoor_outdoor_function, mqtt_client_name, outdoor_mqtt_topic, indoor_mqtt_topic)


# Config Setup
(temp_offset, altitude, enable_display, enable_adafruit_io, aio_user_name, aio_key, aio_feed_window,
 aio_feed_sequence, aio_household_prefix, aio_location_prefix, aio_package, enable_send_data_to_homemanager,
 enable_receive_data_from_homemanager, enable_indoor_outdoor_functionality,
 mqtt_broker_name, mqtt_username, mqtt_password, outdoor_source_type, outdoor_source_id, enable_noise, enable_luftdaten,
 enable_luftdaten_noise, disable_luftdaten_sensor_upload, enable_climate_and_gas_logging, enable_particle_sensor,
 enable_eco2_tvoc, gas_daily_r0_calibration_hour, reset_gas_sensor_calibration, incoming_temp_hum_mqtt_topic,
 incoming_temp_hum_mqtt_sensor_name, incoming_barometer_mqtt_topic, incoming_barometer_sensor_id,
 indoor_outdoor_function, mqtt_client_name, outdoor_mqtt_topic, indoor_mqtt_topic) = retrieve_config()

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


def read_raw_gas():
    gas_data = gas.read_all()
    raw_red_rs = round(gas_data.reducing, 0)
    raw_oxi_rs = round(gas_data.oxidising, 0)
    raw_nh3_rs = round(gas_data.nh3, 0)
    return raw_red_rs, raw_oxi_rs, raw_nh3_rs


red_r0, oxi_r0, nh3_r0 = read_raw_gas()


def read_gas_in_ppm(gas_calib_temp, gas_calib_hum, gas_calib_bar, raw_temp, raw_hum, raw_barometer, gas_sensors_warm):
    if gas_sensors_warm:
        comp_red_rs, comp_oxi_rs, comp_nh3_rs, raw_red_rs, raw_oxi_rs, raw_nh3_rs = comp_gas(gas_calib_temp,
                                                                                             gas_calib_hum,
                                                                                             gas_calib_bar,
                                                                                             raw_temp,
                                                                                             raw_hum, raw_barometer)
        print("Reading Compensated Gas sensors after warmup completed")
    else:
        raw_red_rs, raw_oxi_rs, raw_nh3_rs = read_raw_gas()
        comp_red_rs = raw_red_rs
        comp_oxi_rs = raw_oxi_rs
        comp_nh3_rs = raw_nh3_rs
        print("Reading Raw Gas sensors before warmup completed")
    if comp_red_rs/red_r0 > 0:
        red_ratio = comp_red_rs/red_r0
    else:
        red_ratio = 0.0001
    if comp_oxi_rs/oxi_r0 > 0:
        oxi_ratio = comp_oxi_rs/oxi_r0
    else:
        oxi_ratio = 0.0001
    if comp_nh3_rs/nh3_r0 > 0:
        nh3_ratio = comp_nh3_rs/nh3_r0
    else:
        nh3_ratio = 0.0001
    red_in_ppm = math.pow(10, -1.25 * math.log10(red_ratio) + 0.64)
    oxi_in_ppm = math.pow(10, math.log10(oxi_ratio) - 0.8129)
    nh3_in_ppm = math.pow(10, -1.8 * math.log10(nh3_ratio) - 0.163)
     print("Red Rs:", round(red_in_ppm, 0), "Oxi Rs:", round(oxi_in_ppm, 0), "NH3 Rs:", round(nh3_in_ppm, 0))
    return red_in_ppm, oxi_in_ppm, nh3_in_ppm


def comp_gas(gas_calib_temp, gas_calib_hum, gas_calib_bar, raw_temp, raw_hum, raw_barometer):
    gas_data = gas.read_all()
    gas_temp_diff = raw_temp - gas_calib_temp
    gas_hum_diff = raw_hum - gas_calib_hum
    gas_bar_diff = raw_barometer - gas_calib_bar
    raw_red_rs = round(gas_data.reducing, 0)
    comp_red_rs = round(raw_red_rs - (red_temp_comp_factor * raw_red_rs * gas_temp_diff +
                                      red_hum_comp_factor * raw_red_rs * gas_hum_diff +
                                      red_bar_comp_factor * raw_red_rs * gas_bar_diff), 0)
    raw_oxi_rs = round(gas_data.oxidising, 0)
    comp_oxi_rs = round(raw_oxi_rs - (oxi_temp_comp_factor * raw_oxi_rs * gas_temp_diff +
                                      oxi_hum_comp_factor * raw_oxi_rs * gas_hum_diff +
                                      oxi_bar_comp_factor * raw_oxi_rs * gas_bar_diff), 0)
    raw_nh3_rs = round(gas_data.nh3, 0)
    comp_nh3_rs = round(raw_nh3_rs - (nh3_temp_comp_factor * raw_nh3_rs * gas_temp_diff +
                                      nh3_hum_comp_factor * raw_nh3_rs * gas_hum_diff +
                                      nh3_bar_comp_factor * raw_nh3_rs * gas_bar_diff), 0)
    print("Gas Compensation. Raw Red Rs:", raw_red_rs, "Comp Red Rs:", comp_red_rs, "Raw Oxi Rs:",
          raw_oxi_rs, "Comp Oxi Rs:", comp_oxi_rs,
          "Raw NH3 Rs:", raw_nh3_rs, "Comp NH3 Rs:", comp_nh3_rs)
    return comp_red_rs, comp_oxi_rs, comp_nh3_rs, raw_red_rs, raw_oxi_rs, raw_nh3_rs


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
