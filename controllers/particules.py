class Particules : 
    def get_particules_values(diameter):
        try:
            data = pms5003.read()
        except pmsReadTimeoutError:
            print("Failed to read PMS5003")
        else:
            return float(data.pm_ug_per_m3(diameter))