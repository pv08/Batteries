import numpy as np
from py_dss_interface import DSSDLL
class Powerflow():
    def __init__(self, battery_size, case, hour, day, bat_list, lv_bus_list, lvbus_basekv_list):
        self.dss = DSSDLL()
        self.battery_size = battery_size
        self.case = case
        self.hour = hour
        self.day = day
        self.bat_list = bat_list
        self.lv_bus_list = lv_bus_list
        self.lvbus_basekv_list = lvbus_basekv_list

    def calcDSSPowerflow(self, master_file, community_buses, community_lines):
        self.dss.text(f"compile {master_file}")

        if self.day == 0 and self.hour == 0:
            for battery in self.bat_list:
                name = "Storage.%s" % battery
                self.dss.circuit_set_active_element(name)
                # dss.cktelement_all_property_names()
                # property_index = str(dss.cktelement_all_property_names().index("%stored") + 1)
                # dss.dssproperties_read_value(str(dss.cktelement_all_property_names().index("%stored") + 1))
                self.dss.text(f"edit {name} %stored=50")

        self.dss.solution_write_hour(self.hour)
        if self.battery_size == 0:
            self.dss.text("set casename=case0%s_day%shour%s_no_storage" % (self.case, self.day, self.hour))
        if self.battery_size != 0:
            self.dss.text("set casename=case0%s_day%shour%s_with_storage%s" % (self.case, self.day, self.hour, self.battery_size))

        # ...::: SETTINGS FOR VOLTAGE AND OVERLOAD VIOLATIONS REPORTS - OBS => needs CloseDI after SOLVE:::...
        # dss.text("set DemandInterval=true")
        # dss.text("set overloadreport=true")
        # dss.text("set voltexceptionreport=true")
        # dss.text("set DIVerbose=true")

        # ...::: POWER FLOW :::...
        # Solving Power Flow
        self.dss.solution_solve()
        # Closing Violation Reports
        # dss.text("CloseDI")

        # ...::: POWER FLOW REPORTS :::...

        # 1 - Community Buses Voltages
        community_bus_results = []
        for bus in community_buses:
            idx = np.where(self.lv_bus_list == bus)
            self.dss.circuit_set_active_bus(bus)
            self.dss.circuit_all_bus_vmag_pu()
            if self.dss.bus_num_nodes() == 1:
                vmag = self.dss.bus_vmag_angle()
                community_bus_results.append(
                    {'Vmag': vmag}
                )
            if self.dss.bus_num_nodes() == 2:
                vmag = self.dss.bus_vmag_angle()
                vmag_min = min(vmag[0], vmag[2])
                vmag_max = max(vmag[0], vmag[2])
                if vmag_min < 0.95 * self.lvbus_basekv_list[idx[0][0]] * 1000:
                    community_bus_results.append({
                        'Vmag': vmag_min
                    })
                else:
                    community_bus_results.append({
                        'Vmag': vmag_max
                    })
            if self.dss.bus_num_nodes() == 3:
                vmag = self.dss.bus_vmag_angle()
                vmag_min = min(vmag[0], vmag[2], vmag[4])
                vmag_max = max(vmag[0], vmag[2], vmag[4])
                if vmag_min < 0.95 * self.lvbus_basekv_list[idx[0][0]] * 1000:
                    community_bus_results.append({
                        'Vmag': vmag_min
                    })
                else:
                    community_bus_results.append({
                        'Vmag': ('%s_3PH' % vmag_max)
                    })

        community_lines_results = []
        for line in community_lines:
            self.dss.circuit_set_active_element("Line.%s" % line)
            current_mag = self.dss.cktelement_currents_mag_ang()
            current_base = float(self.dss.lines_read_norm_amps())
            line_phases = self.dss.lines_read_phases()
            if line_phases == 1:
                current_mag = max(current_mag[0], current_mag[2])
            if line_phases == 2:
                current_mag = max(current_mag[0], current_mag[2],
                                  current_mag[4], current_mag[6])
            if line_phases == 3:
                current_mag = max(current_mag[0], current_mag[2],
                                  current_mag[4], current_mag[6],
                                  current_mag[8], current_mag[10])
            community_lines_results.append({
                'Imag': current_mag,
                'Imag_pu': current_mag / current_base
            })

        # dss.text("show voltages LN node")

        # dss.text("show Meters")
        # dss.text("export Meters")
        return community_bus_results, community_lines_results




