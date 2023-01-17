from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
pms5003 = PMS5003()

class Particules : 
    def get_particules_values(self,diameter):
        try:
            data = pms5003.read()
        except pmsReadTimeoutError:
            print("Failed to read PMS5003")
        else:
            return float(data.pm_ug_per_m3(diameter))