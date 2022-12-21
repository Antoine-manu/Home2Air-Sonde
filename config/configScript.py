import json
from enviroplus import gas

class Config :
    def retrieve_config():
        try:
            with open('./config.json', 'r') as f:
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
