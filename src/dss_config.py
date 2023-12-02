import os
import glob
from src.utils.functions import mkdir_if_not_exists
from pathlib import Path

class DSSConfig:
    def __init__(self, root_dir, battery_allocation ,battery_size, study_case, profiles, bat_bus_location: list = None):

        mkdir_if_not_exists('etc/')
        mkdir_if_not_exists('etc/dss/')
        self.root_dir = root_dir
        self.bat_bus_location = bat_bus_location
        self.battery_size = battery_size
        self.battery_allocation = battery_allocation
        self.study_case = study_case
        #sets
        self.defaultbasefrequency = 60

        #new
        self.circuit_name = 'circuit.SJU'
        self.config = {
            'BasekV': 138,
            'pu': 1.00,
            'angle': 0,
            'frequency': 60,
            'phases': 3,
            'Isc3': 10000.0,
            'Isc1': 10500.0
        }

        abspath = f"{self.root_dir}/data/profiles_edited"
        self.generateLoadShapeFile(profiles=profiles, abspath=abspath)

        #redirect
        self.redirection = ["Bibliotecas/bibliotecas.dss",
                            "FLX_LinesMV.dss",
                            "FLX_Substation.dss",
                            "FLX_Transformers.dss",
                            "FLX_Monitors.dss",
                            "FLX_LinesLV.dss",
                            "FLX_Loadshapes_Nom_hourly_edited.dss",
                            f'FLX_LoadsLV_Caso0{self.study_case}.dss',
                            f'FLX_DG_Caso0{self.study_case}.dss']


        #buscoords
        self.bus_coor = ["FLX_BusListMV.csv", "FLX_BusListLV.csv"]

        #sets
        self.mode = 'daily'
        self.stepsize = 1
        self.number = 1
        self.masterfile = self.createMasterDSSFiles()

    @staticmethod
    def generateLoadShapeFile(profiles: list, abspath: str):
        file_content = ''
        for profile in profiles:
            files = glob.glob(f'{abspath}\\{profile}\\*.csv')
            if profile != 'DG':
                for file in files:
                    name = file.split('\\')[-1].replace('.csv', '')
                    file_content += f'New Loadshape.{name} npts=24 interval=1 mult=(file={file}) useactual=no\n'
        file_content += 'New XYCurve.MyPvsT npts=4 xarray=[.001 25 75 100] yarray=[1.0 1.0 1.0 1.0]\n'
        file_content += 'New XYCurve.MyEff npts=4 xarray=[.1 .2 .4 1.0] yarray=[1.0 1.0 1.0 1.0]\n'
        file_content += f'New Tshape.MyTemp npts=24 interval=1 csvfile={abspath}\DG\PVtemp_nom.csv\n'
        file_content += f'New Tshape.PVtemp npts=24 interval=1 csvfile={abspath}\DG\PVtemp_nom.csv\n'
        file_content += f'New Loadshape.MyIrrad npts=24 interval=1 csvfile={abspath}\DG\PVprofile.csv\n'
        file_content += f'New Loadshape.PVprofile npts=24 interval=1 csvfile={abspath}\DG\PVprofile.csv\n'
        with open(f'etc/dss/FLX_Loadshapes_Nom_hourly_edited.dss', 'w') as dss_file:
            dss_file.write(file_content)
            dss_file.close()



    @staticmethod
    def createStorageFile(case: int, bus_location: list, battery_size: int = 1):
        file = ''
        for bat_bus in bus_location:
            file += f"New Storage.{bat_bus['name']} phases=1 Bus1={bat_bus['bus']}.1.2.3 kv=0.24 kwrated={2.56 * battery_size} kwhrated={10.24 * battery_size} dispmode=follow daily=BatteryProfile\n"

        with open(f'etc/dss/FLX_Storage_Caso0{case}.dss', 'w') as dss_file:
            dss_file.write(file)
            dss_file.close()


    def createMasterDSSFiles(self):
        file = f"clear\nset defaultbasefrequency={self.defaultbasefrequency}\nnew {self.circuit_name} "
        new_command = ''

        for key in self.config.keys():
            new_command += f'{key}={self.config[key]} '
        file += new_command.strip() + '\n'

        for redirect in self.redirection:
            file += f'redirect {redirect}\n'

        file += f'!Case Study 0{self.study_case}\n'
        if self.battery_allocation and self.bat_bus_location is not None:
            self.createStorageFile(case=self.study_case, bus_location=self.bat_bus_location, battery_size=self.battery_size)
            file += f'redirect FLX_Storage_Caso0{self.study_case}.dss\n'

        file += f'!Bus coordinates\n'
        for coor in self.bus_coor:
            file += f'buscoords {coor}\n'

        file += f'set mode={self.mode}\nset stepsize={self.stepsize}\nset number={self.number}'

        with open(f'etc/dss/master.dss', 'w') as dss_file:
            dss_file.write(file)
            dss_file.close()


        abspath = f"{self.root_dir}/etc/dss/master.dss"
        return abspath

