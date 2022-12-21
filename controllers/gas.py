import math
from enviroplus import gas

class Gas :
    def read_raw_gas(self):
        gas_data = gas.read_all()
        raw_red_rs = round(gas_data.reducing, 0)
        raw_oxi_rs = round(gas_data.oxidising, 0)
        raw_nh3_rs = round(gas_data.nh3, 0)
        return raw_red_rs, raw_oxi_rs, raw_nh3_rs


    def read_gas_in_ppm(self, gas_calib_temp, gas_calib_hum, gas_calib_bar, raw_temp, raw_hum, raw_barometer, gas_sensors_warm):
        red_r0, oxi_r0, nh3_r0 = self.read_raw_gas()

        if gas_sensors_warm:
            comp_red_rs, comp_oxi_rs, comp_nh3_rs, raw_red_rs, raw_oxi_rs, raw_nh3_rs = comp_gas(gas_calib_temp,
                                                                                                gas_calib_hum,
                                                                                                gas_calib_bar,
                                                                                                raw_temp,
                                                                                                raw_hum, raw_barometer)
            print("Reading Compensated Gas sensors after warmup completed")
        else:
            raw_red_rs, raw_oxi_rs, raw_nh3_rs = self.read_raw_gas()
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


    def comp_gas(self, gas_calib_temp, gas_calib_hum, gas_calib_bar, raw_temp, raw_hum, raw_barometer,):
        red_temp_comp_factor = -0.015
        red_hum_comp_factor = 0.0125
        red_bar_comp_factor = -0.0053
        oxi_temp_comp_factor = -0.017
        oxi_hum_comp_factor = 0.0115
        oxi_bar_comp_factor = -0.0072
        nh3_temp_comp_factor = -0.02695
        nh3_hum_comp_factor = 0.0094
        nh3_bar_comp_factor = 0.003254

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