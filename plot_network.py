# ---------------------------------------- #
# Created by:                              #
#            PEDRO HENRIQUE PETERS BARBOSA #
#                                          #
# email:   pedro.peters@engenharia.ufjf.br #
# ---------------------------------------- #

# ...::: PACKAGES MANAGEMENT :::...

import numpy as np
import pandas as pd
import pandapower as pp
import matplotlib.pyplot as plt
from pandapower.plotting import simple_plot, simple_plotly
import sys


# CASE STUDY
case = 6            # options = [1,2,3,4,5,6,7]
battery_size = 10    # options = [0,1,3,5,10]  -> 0 = no battery // 1 = base battery // 10 = 10x base battery

# ...::: IMPORTING DATA :::...
# HIGH VOLTAGE BUSES DATA
hvbus_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\BusListHV.csv",delimiter=',')
hvbus_names = hvbus_data['NAME']
hvbus_basekv = hvbus_data['BASE_KV']
hvbus_latitude = hvbus_data['LATITUDE']
hvbus_longitude = hvbus_data['LONGITUDE']
hvbus_geodata = list(zip(hvbus_latitude, hvbus_longitude))
# MEDIUM VOLTAGE BUSES DATA
mvbus_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\BusListMV.csv",delimiter=',')
mvbus_names = mvbus_data['NAME']
mvbus_basekv = mvbus_data['BASE_KV']
mvbus_latitude = mvbus_data['LATITUDE']
mvbus_longitude = mvbus_data['LONGITUDE']
mvbus_geodata = list(zip(mvbus_latitude, mvbus_longitude))
# LOW VOLTAGE BUSES DATA
lvbus_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\BusListLV.csv",delimiter=',')
lvbus_names = lvbus_data['NAME']
lvbus_basekv = lvbus_data['BASE_KV']
lvbus_latitude = lvbus_data['LATITUDE']
lvbus_longitude = lvbus_data['LONGITUDE']
lvbus_geodata = list(zip(lvbus_latitude, lvbus_longitude))
# MEDIUM VOLTAGE LINES DATA
mvline_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\LinesListMV.csv",delimiter=',')
mvline_names = mvline_data['NAME']
mvline_from = mvline_data['BUS_FROM']
mvline_to = mvline_data['BUS_TO']
mvline_length = mvline_data['LENGTH[M]']
mvline_geometry = mvline_data['GEOMETRY']
mvline_basekv = mvline_data['BASE_KV']
# LOW VOLTAGE LINES DATA
lvline_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\LinesListLV.csv",delimiter=',')
lvline_names = lvline_data['NAME']
lvline_from = lvline_data['BUS_FROM']
lvline_to = lvline_data['BUS_TO']
lvline_length = lvline_data['LENGTH[M]']
lvline_geometry = lvline_data['GEOMETRY']
lvline_basekv = lvline_data['BASE_KV']
# SUBSTATIONS DATA - THREE WINDING TRANSFORMER
trafo3w_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\SubstationList.csv", delimiter=',')
trafo3w_names = trafo3w_data['NAME']
trafo3w_hvbus = trafo3w_data['HV_BUS']
trafo3w_mvbus = trafo3w_data['MV_BUS']
trafo3w_lvbus = trafo3w_data['LV_BUS']
trafo3w_hvbasekv = trafo3w_data['VN_HV_KV']
trafo3w_mvbasekv = trafo3w_data['VN_MV_KV']
trafo3w_lvbasekv = trafo3w_data['VN_LV_KV']
trafo3w_hvbasekva = trafo3w_data['SN_HV_MVA']
trafo3w_mvbasekva = trafo3w_data['SN_MV_MVA']
trafo3w_lvbasekva = trafo3w_data['SN_LV_MVA']
trafo3w_hvvsc = trafo3w_data['VK_HV_PERCENT']
trafo3w_mvvsc = trafo3w_data['VK_MV_PERCENT']
trafo3w_lvvsc = trafo3w_data['VK_LV_PERCENT']
trafo3w_hvvscr = trafo3w_data['VKR_HV_PERCENT']
trafo3w_mvvscr = trafo3w_data['VKR_MV_PERCENT']
trafo3w_lvvscr = trafo3w_data['VKR_LV_PERCENT']
trafo3w_pfe = trafo3w_data['PFE_KW']
trafo3w_i0 = trafo3w_data['I0_PERCENT']
# TRANSFORMERS DATA
trafo_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\TransformersList.csv", delimiter=',')
trafo_names = trafo_data['NAME']
trafo_hvbus = trafo_data['HV_BUS']
trafo_lvbus = trafo_data['LV_BUS']
trafo_hvbasekv = trafo_data['VN_HV_KV']
trafo_lvbasekv = trafo_data['VN_LV_KV']
trafo_basekva = trafo_data['SN_MVA']
trafo_vscr = trafo_data['VKR_PERCENT']
trafo_vsc = trafo_data['VK_PERCENT']
trafo_pfe = trafo_data['PFE_KW']
trafo_i0 = trafo_data['I0_PERCENT']
# LOADS DATA
load_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\LoadsList_Caso0%s.csv" % case,delimiter=',')
load_name = load_data['NAME']
load_bus = load_data['BUS']
load_basekv = load_data['BASE_KV']
load_basekw = load_data['BASE_KW']
load_basekvar = load_data['BASE_KVAR']
load_phases = load_data['PHASES']
load_loadshape = load_data['LOADSHAPE']
load_kwh = load_data['KWH']
load_community = load_data['COMMUNITY']
# GENERATORS DATA
gen_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\PvList_Caso0%s.csv" % case,delimiter=',')
gen_name = gen_data['NAME']
gen_bus = gen_data['BUS']
gen_basekv = gen_data['BASE_KV']
gen_phases = gen_data['PHASES']
gen_basekva = gen_data['BASE_KVA']
gen_pf = gen_data['PF']
gen_basekw = gen_data['BASE_KW']
gen_genshape = gen_data['GEN_SHAPE']
gen_community = gen_data['COMMUNITY']
# STORAGE DATA - COMMUNITY BATTERIES
bat_data = pd.read_csv(r"C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\BatteryList_Caso0%s.csv" % case,delimiter=',')
bat_name = bat_data['NAME']
bat_bus = bat_data['BUS']
bat_community = bat_data['COMMUNITY']
bat_basekw = bat_data['BASE_KW']
bat_capacity = bat_data['NOMINAL_CAPACITY_[KWH]']
bat_socmax = bat_data['SOC_MAX']
bat_socmin = bat_data['SOC_MIN']
bat_socinit = bat_data['SOC_INIT']
bat_chargeeff = bat_data['CHARGE_EFF']
bat_dischargeeff = bat_data['DISCHARGE_EFF']
bat_chargerate = bat_data['CHARGE_RATE']
bat_dischargerate = bat_data['DISCHARGE_RATE']
bat_autodischargerate = bat_data['AUTODISCHARGE_RATE']
bat_loadshape = bat_data['LOADSHAPE']

# XXX - FUNCTION TO FILTER AGENTS INFORMATION
def agents_info():
    agent_number = []
    agent_name = []
    agent_type = []
    agent_basekw = []
    agent_bus = []
    community_location = []
    agent_profile = []
    for i in range(0, n_agents):
        agent_number.append(i)
    for i in range(0, len(load_data)):
        agent_name.append(load_name[i])
        agent_type.append('CONSUMER')
        agent_bus.append(load_bus[i])
        agent_basekw.append(load_basekw[i])
        community_location.append(load_community[i])
        agent_profile.append(load_loadshape[i])
    for i in range(0, len(gen_data)):
        agent_name.append(gen_name[i])
        agent_type.append('PRODUCER')
        agent_bus.append(gen_bus[i])
        agent_basekw.append(gen_basekw[i])
        community_location.append(gen_community[i])
        agent_profile.append(gen_genshape[i])
    if battery_size != 0:
        for i in range(0, len(bat_data)):
            agent_name.append(bat_name[i])
            agent_type.append('BATTERY')
            agent_bus.append(bat_bus[i])
            agent_basekw.append(bat_basekw[i])
            community_location.append(bat_community[i])
            agent_profile.append(bat_loadshape[i])

    agent_name.append('EXTERNAL_GRID')
    agent_name.append('EXTERNAL_GRID')
    agent_type.append('EXT_CONSUMER')
    agent_type.append('EXT_PRODUCER')
    agent_bus.append('SOURCEBUS')
    agent_bus.append('SOURCEBUS')
    agent_basekw.append(999999)
    agent_basekw.append(999999)
    community_location.append(n_communities)
    community_location.append(n_communities)
    agent_profile.append('')
    agent_profile.append('')

    agent_data = {'AGENT': agent_number, 'NAME': agent_name, 'TYPE': agent_type, 'BUS': agent_bus,
                  'BASE_KW': agent_basekw,
                  'COMMUNITY_LOCATION': community_location, 'PROFILE': agent_profile}
    agent_df = pd.DataFrame(data=agent_data, index=None)
    return agent_df

# XXX - FUNCTION FOR PANDAPOWER PLOT OF NETWORK
def pandapower_plot():
    # CREATING PANDAPOWER ELEMENTS AND COLLECTIONS
    net = pp.create_empty_network()  # pandapower network creation
    hvbus_collection_list = []  # high voltage buses collection
    mvbus_collection_list = []  # medium voltage buses collection
    lvbus_collection_list = []  # low voltage buses collection
    mvlines_collection_list = []  # medium voltage lines collection
    lvlines_collection_list = []  # low voltage lines collection
    trafo_collection_list = []  # transformers collection
    load_collection_list = []  # loads collection
    gen_collection_list = []  # generators collection
    prosumer_collection_list = []  # prosumers collection
    bat_collection_list = []  # batteries collection

    for i in range(0, len(hvbus_data)):  # creating high voltage buses
        pp.create_bus(net, vn_kv=hvbus_basekv[i], name=hvbus_names[i], geodata=hvbus_geodata[i])
        hvbus_index = pp.get_element_index(net, "bus", hvbus_names[i])
        hvbus_collection_list.append(hvbus_index)
    for i in range(0, len(mvbus_data)):  # creating medium voltage buses
        pp.create_bus(net, vn_kv=mvbus_basekv[i], name=mvbus_names[i], geodata=mvbus_geodata[i])
        mvbus_index = pp.get_element_index(net, "bus", mvbus_names[i])
        mvbus_collection_list.append(mvbus_index)
    for i in range(0, len(lvbus_data)):  # creating low voltage buses
        pp.create_bus(net, vn_kv=lvbus_basekv[i], name=lvbus_names[i], geodata=lvbus_geodata[i])
        lvbus_index = pp.get_element_index(net, "bus", lvbus_names[i])
        lvbus_collection_list.append(lvbus_index)
    for i in range(0, len(mvline_data)):  # creating medium voltage lines
        from_bus = pp.get_element_index(net, "bus", mvline_from[i])
        to_bus = pp.get_element_index(net, "bus", mvline_to[i])
        pp.create_line(net, from_bus=from_bus, to_bus=to_bus, length_km=mvline_length[i] / 1000,
                       std_type='149-AL1/24-ST1A 10.0', name=mvline_names[i])
        mvlines_index = pp.get_element_index(net, "line", mvline_names[i])
        mvlines_collection_list.append(mvlines_index)
    for i in range(0, len(lvline_data)):  # creating low voltage lines
        from_bus = pp.get_element_index(net, "bus", lvline_from[i])
        to_bus = pp.get_element_index(net, "bus", lvline_to[i])
        pp.create_line(net, from_bus=from_bus, to_bus=to_bus, length_km=lvline_length[i] / 1000,
                       std_type='149-AL1/24-ST1A 10.0', name=lvline_names[i])
        lvlines_index = pp.get_element_index(net, "line", lvline_names[i])
        lvlines_collection_list.append(lvlines_index)
    for i in range(0, len(trafo3w_data)):  # creating substation - 3w transformer
        hv_bus = pp.get_element_index(net, "bus", trafo3w_hvbus[i])
        mv_bus = pp.get_element_index(net, "bus", trafo3w_mvbus[i])
        lv_bus = pp.get_element_index(net, "bus", trafo3w_lvbus[i])
        pp.create_transformer3w_from_parameters(net, hv_bus=hv_bus, mv_bus=mv_bus, lv_bus=lv_bus,
                                                vn_hv_kv=trafo3w_hvbasekv[i], vn_mv_kv=trafo3w_mvbasekv[i],
                                                vn_lv_kv=trafo3w_lvbasekv[i],
                                                sn_hv_mva=trafo3w_hvbasekva[i], sn_mv_mva=trafo3w_mvbasekva[i],
                                                sn_lv_mva=trafo3w_lvbasekva[i],
                                                vk_hv_percent=trafo3w_hvvsc[i], vk_mv_percent=trafo3w_hvvsc[i],
                                                vk_lv_percent=trafo3w_hvvsc[i],
                                                vkr_hv_percent=trafo3w_hvvscr[i], vkr_mv_percent=trafo3w_hvvscr[i],
                                                vkr_lv_percent=trafo3w_hvvscr[i],
                                                pfe_kw=0, i0_percent=0, name=trafo3w_names[i])
    for i in range(0, len(trafo_data)):  # creating transformers
        hv_bus = pp.get_element_index(net, "bus", trafo_hvbus[i])
        lv_bus = pp.get_element_index(net, "bus", trafo_lvbus[i])
        pp.create_transformer_from_parameters(net, name=trafo_names[i], hv_bus=hv_bus, lv_bus=lv_bus,
                                              sn_mva=trafo_basekva[i], vn_hv_kv=trafo_hvbasekv[i],
                                              vn_lv_kv=trafo_lvbasekv[i],
                                              vkr_percent=trafo_vscr[i], vk_percent=trafo_vsc[i],
                                              pfe_kw=trafo_pfe[i], i0_percent=trafo_i0[i])
        trafo_index = pp.get_element_index(net, "trafo", trafo_names[i])
        trafo_collection_list.append(trafo_index)
    for i in range(0, len(load_data)):  # creating loads
        load_loc_bus = pp.get_element_index(net, "bus", load_bus[i])
        pp.create_load(net, name=load_name[i], bus=load_loc_bus, p_mw=load_basekw[i] / 1000)
        load_collection_list.append(load_loc_bus)
    for i in range(0, len(gen_data)):  # creating loads
        gen_loc_bus = pp.get_element_index(net, "bus", gen_bus[i])
        pp.create_gen(net, name=gen_name[i], bus=gen_loc_bus, p_mw=gen_basekw[i] / 1000)
        gen_collection_list.append(gen_loc_bus)
        if (gen_loc_bus in load_collection_list):
            prosumer_collection_list.append(gen_loc_bus)
    for i in range(0, len(bat_data)):  # creating loads
        bat_loc_bus = pp.get_element_index(net, "bus", bat_bus[i])
        pp.create_gen(net, name=bat_name[i], bus=bat_loc_bus, p_mw=bat_basekw[i] / 1000)
        bat_collection_list.append(bat_loc_bus)

    #  Creating External Grid
    sourcebus = pp.get_element_index(net, "bus", 'SOURCEBUS')
    pp.create_ext_grid(net, bus=sourcebus, vm_pu=1.00, va_degree=0, name='External grid', in_service=True)

    # PANDAPOWER PLOTTING
    # Plotting Collections
    ### full color pallette in: https://xkcd.com/color/rgb/
    hvbus_collection = pp.plotting.create_bus_collection(net, buses=hvbus_collection_list, size=1.0, patch_type='rect',
                                                         color='grey')
    mvbus_collection = pp.plotting.create_bus_collection(net, buses=mvbus_collection_list, size=1.0, patch_type='poly3',
                                                         color='grey') # '#ff000d' = bright red color
    lvbus_collection = pp.plotting.create_bus_collection(net, buses=lvbus_collection_list, size=1.0,
                                                         patch_type='circle', color='grey') # '#0165fc' = bright blue color
    mvlines_collection = pp.plotting.create_line_collection(net, lines=mvlines_collection_list, use_bus_geodata=True,
                                                            color='grey') # '#ff000d' = bright red color
    lvlines_collection = pp.plotting.create_line_collection(net, lines=lvlines_collection_list, use_bus_geodata=True,
                                                            color='grey') # '#0165fc' = bright blue color
    # trafo_collection = pp.plotting.create_trafo_collection(net, trafos=trafo_collection_list, size=1.0, color='black')
    load_collection = pp.plotting.create_bus_collection(net, buses=load_collection_list, size=2.5, patch_type='poly3',
                                                        color='cyan')
    gen_collection = pp.plotting.create_bus_collection(net, buses=gen_collection_list, size=2.5, patch_type='poly3',
                                                       color='yellow')
    prosumer_collection = pp.plotting.create_bus_collection(net, buses=prosumer_collection_list, size=15,
                                                            patch_type='poly6', color='#01ff07') # bright green color
    bat_collection = pp.plotting.create_bus_collection(net, buses=bat_collection_list, size=15,
                                                            patch_type='rect', color='#be03fd') # bright purple color

    if battery_size == 0:
        collections = [mvlines_collection, lvlines_collection,
                       hvbus_collection, mvbus_collection, lvbus_collection,
                       load_collection, gen_collection, prosumer_collection]
    else:
        collections = [mvlines_collection, lvlines_collection,
                       hvbus_collection, mvbus_collection, lvbus_collection,
                       load_collection, gen_collection, prosumer_collection, bat_collection]

    pp.plotting.draw_collections(collections=collections)
    # plt.savefig(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\DSS\plot_data\teste.svg')
    # plt.show()

    # Plotting Network
    # simple_plot(net, bus_size=0.05, trafo_size=0.05)
    # simple_plot(net, respect_switches=False, line_width=1.0, bus_size=0.01, ext_grid_size=0.05, trafo_size=0.05,
    #             plot_loads=True, plot_sgens=True, load_size=0.05, sgen_size=0.05, scale_size=True,
    #             bus_color='b', line_color='grey', trafo_color='k', ext_grid_color='y')

    return

# XXX - PLOT COMMUNITY SOCIAL WELFARE
def social_welfare_plot():
    plt.figure()
    plt.grid()
    optimization_df = pd.DataFrame(optimization_results[day].values())
    plt.plot(optimization_df['Objective'],label='Social Welfare')
    plt.legend()
    plt.title('Social Welfare',fontsize=22)
    plt.xlabel('Time (hours)',fontsize=18)
    plt.ylabel('Social Welfare (R$)',fontsize=18)
    # plt.show()
    return

# XXX - PLOT INDIVIDUAL BATTERY STATE OF CHARGE
def battery_state_of_charge_plot(bat_soc):
    if battery_size != 0:
        plt.figure()
        plt.grid()
        if day == 0:
            soc_start = pd.Series([50])
            for battery in bat_soc:
                agent_soc = soc_start.append(bat_soc[battery], ignore_index=True)
                plt.plot(range(-1, len(agent_soc) - 1), agent_soc, label='Battery %s' % battery)
        else:
            for battery in bat_soc:
                soc_start = pd.Series(last_soc_of_day[battery])
                agent_soc = soc_start.append(bat_soc[battery], ignore_index=True)
                plt.plot(range(-1, len(agent_soc) - 1), agent_soc, label='Battery %s' % battery)
        plt.legend()
        plt.title('Battery State Of Charge', fontsize=22)
        plt.xlabel('Time (hours)', fontsize=18)
        plt.ylabel('SOC (%)', fontsize=18)
        # plt.show()
    else:
        print("No Batteries In Network")
    return

# XXX - PLOT INDIVIDUAL BATTERY DISPATCH
def battery_dispatch_plot(bat_dispatch):
    if battery_size != 0:
        plt.figure()
        plt.grid()
        for battery in bat_dispatch:
            plt.plot(bat_dispatch[battery], label='Battery %s' % battery)
        plt.legend()
        plt.title('Battery Dispatch', fontsize=22)
        plt.xlabel('Time (hours)', fontsize=18)
        plt.ylabel('Power (W)', fontsize=18)
        # plt.show()
    else:
        print("No Batteries In Network")
    return

# XXX - PLOT TOTAL BATTERY DISPATCH
def total_battery_dispatch_plot(bat_dispatch):
    if battery_size != 0:
        total_bat_dispatch = bat_dispatch.to_numpy()
        total_bat_dispatch = np.sum(total_bat_dispatch, axis=1)
        plt.figure()
        plt.grid()
        plt.plot(total_bat_dispatch, label='Total Battery Dispatch')
        plt.legend()
        plt.title('Battery Dispatch', fontsize=22)
        plt.xlabel('Time (hours)', fontsize=18)
        plt.ylabel('Power (W)', fontsize=18)
        # plt.show()
    else:
        print("No Batteries In Network")
    return

# XXX - PLOT INDIVIDUAL LOAD DISPATCH
def load_dispatch_plot(load_dispatch):
    plt.figure()
    plt.grid()
    for load in load_dispatch:
        plt.plot(load_dispatch[load], label='Load %s' % load)
    plt.legend()
    plt.title('Load Dispatch', fontsize=22)
    plt.xlabel('Time (hours)', fontsize=18)
    plt.ylabel('Power (W)', fontsize=18)
    # plt.show()
    return

# XXX - PLOT TOTAL LOAD DISPATCH
def total_load_dispatch_plot(load_dispatch,bat_dispatch):
    if battery_size != 0:
        total_bat_dispatch = bat_dispatch.to_numpy()
        total_bat_dispatch = np.sum(total_bat_dispatch, axis=1)
    total_load_dispatch = load_dispatch.to_numpy()
    total_load_dispatch = np.sum(total_load_dispatch, axis=1)

    plt.figure()
    plt.grid()
    plt.plot(total_load_dispatch, label='Total Load Dispatch')
    if battery_size != 0:
        plt.plot(total_bat_dispatch, label='Total Battery Dispatch')
    plt.legend()
    plt.title('Total Load Dispatch', fontsize=22)
    plt.xlabel('Time (hours)', fontsize=18)
    plt.ylabel('Power (W)', fontsize=18)
    # plt.show()
    return

# XXX - PLOT INDIVIDUAL GENERATOR DISPATCH
def generators_dispatch_plot(gen_dispatch):
    plt.figure()
    plt.grid()
    for generator in gen_dispatch:
        plt.plot(gen_dispatch[generator], label='Generator %s' % generator)
    plt.legend()
    plt.title('Generator Dispatch', fontsize=22)
    plt.xlabel('Time (hours)', fontsize=18)
    plt.ylabel('Power (W)', fontsize=18)
    # plt.show()
    return

# XXX - PLOT TOTAL GENERATOR DISPATCH
def total_generators_dispatch_plot(gen_dispatch,bat_dispatch):
    if battery_size != 0:
        total_bat_dispatch = bat_dispatch.to_numpy()
        total_bat_dispatch = np.sum(total_bat_dispatch, axis=1)
    total_gen_dispatch = gen_dispatch.to_numpy()
    total_gen_dispatch = np.sum(total_gen_dispatch, axis=1)

    plt.figure()
    plt.grid()
    plt.plot(total_gen_dispatch, label='Total Generator Dispatch')
    if battery_size != 0:
        plt.plot(total_bat_dispatch, label='Total Battery Dispatch')
    plt.legend()
    plt.title('Total Generator Dispatch', fontsize=22)
    plt.xlabel('Time (hours)', fontsize=18)
    plt.ylabel('Power (W)', fontsize=18)
    # plt.show()

# XXX - PLOT COMMUNITY ENERGY BALANCE
def community_energy_balance_plot(bat_dispatch,load_dispatch,gen_dispatch):
    if battery_size != 0:
        total_bat_dispatch = bat_dispatch.to_numpy()
        total_bat_dispatch = np.sum(total_bat_dispatch, axis=1)
    total_load_dispatch = load_dispatch.to_numpy()
    total_load_dispatch = np.sum(total_load_dispatch, axis=1)
    total_gen_dispatch = gen_dispatch.to_numpy()
    total_gen_dispatch = np.sum(total_gen_dispatch, axis=1)

    if battery_size != 0:
        plt.figure()
        plt.grid()
        energy_balance = total_load_dispatch + total_gen_dispatch + total_bat_dispatch
        plt.plot(energy_balance, color='b', label='Community Energy Balance')
        plt.plot(total_bat_dispatch, '--', color='g', label='Battery Dispatch')
        plt.plot(total_load_dispatch, '--', color='r', label='Load Dispatch')
        plt.plot(total_gen_dispatch, '--', color='y', label='Generator Dispatch')
        plt.legend()
        plt.title('Hourly Energy Balance', fontsize=22)
        plt.xlabel('Time (hours)', fontsize=18)
        plt.ylabel('Power (W)', fontsize=18)
        # plt.show()
    else:
        plt.figure()
        plt.grid()
        energy_balance = total_load_dispatch + total_gen_dispatch
        plt.plot(energy_balance, color='b', label='Community Energy Balance')
        plt.plot(total_load_dispatch, '--', color='r', label='Load Dispatch')
        plt.plot(total_gen_dispatch, '--', color='y', label='Generator Dispatch')
        plt.legend()
        plt.title('Hourly Energy Balance', fontsize=22)
        plt.xlabel('Time (hours)', fontsize=18)
        plt.ylabel('Power (W)', fontsize=18)
        # plt.show()
    return

# XXX - PLOT BUSES VOLTAGE PU
def bus_voltage_pu_plot(buses_volt_pu):
    plt.figure()
    plt.grid()
    for bus in buses_volt_pu:
        plt.plot(buses_volt_pu[bus], label='Voltage at %s' % bus)
    plt.hlines(y=1.05, xmin=0, xmax=23, color='r', linestyle='dashed')
    plt.hlines(y=0.95, xmin=0, xmax=23, color='r', linestyle='dashed')
    plt.legend()
    plt.title('Community Buses Voltage', fontsize=22)
    plt.xlabel('Time (hours)', fontsize=18)
    plt.ylabel('Vmag (p.u.)', fontsize=18)
    # plt.show()

# XXX - PLOT BUSES WITH VIOLATIONS
def problem_buses_pu_plot(problem_buses):
    if len(problem_buses) != 0:
        plt.figure()
        plt.grid()
        for bus in problem_buses:
            plt.plot(problem_buses[bus], label='Voltage at %s' % bus)
        # bus = 'BUSLVFLX1057'
        # plt.plot(problem_buses[bus], label='Voltage at %s' % bus)
        plt.hlines(y=1.05, xmin=0, xmax=23, color='r', linestyle='dashed')
        plt.hlines(y=0.95, xmin=0, xmax=23, color='r', linestyle='dashed')
        plt.legend()
        plt.title('Community Buses Voltage Violations', fontsize=22)
        plt.xlabel('Time (hours)', fontsize=18)
        plt.ylabel('Vmag (p.u.)', fontsize=18)
        # plt.show()
    else:
        print("No Bus Voltage Violations")
    return

# XXX - PLOT LINE LOADING AMPERE
def line_loading_mag_plot(lines_amps_mag):
    plt.figure()
    plt.grid()
    for line in community_lines:
        plt.plot(lines_amps_mag[line], label='Loading at %s' % line)
    plt.legend()
    plt.title('Community Lines Loadings', fontsize=22)
    plt.xlabel('Time (hours)', fontsize=18)
    plt.ylabel('Imag (A)', fontsize=18)
    # plt.show()
    return

# XXX - PLOT LINE LOADING PU
def line_loading_pu_plot(lines_amps_pu):
    plt.figure()
    plt.grid()
    for line in community_lines:
        plt.plot(lines_amps_pu[line], label='Loading at %s' % line)
    plt.hlines(y=100, xmin=0, xmax=23, color='r', linestyle='dashed')
    plt.legend()
    plt.title('Community Lines Loadings', fontsize=22)
    plt.xlabel('Time (hours)', fontsize=18)
    plt.ylabel('Imag (%)', fontsize=18)
    # plt.show()
    return

# XXX - PLOT LINES WITH VIOLATIONS
def problem_lines_pu_plot(problem_lines):
    if len(problem_lines) != 0:
        plt.figure()
        plt.grid()
        for line in problem_lines:
            plt.plot(problem_lines[line], label='Loading at %s' % line)
        plt.hlines(y=100, xmin=0, xmax=23, color='r', linestyle='dashed')
        plt.legend()
        plt.title('Community Lines Loading Violations', fontsize=22)
        plt.xlabel('Time (hours)', fontsize=18)
        plt.ylabel('Imag (%)', fontsize=18)
        # plt.show()
    else:
        print("No Line Loading Violations")
    return

# XXX -  RESULT DATA PROCESSING
def data_processing(agents_df):
    ##### AGENT DISPATCH RESULTS
    bat_soc = []
    bat_dispatch = []
    load_dispatch = []
    gen_dispatch = []
    for agent in range(0, n_agents):
        name = agents_df['NAME'][agent]
        type = agents_df['TYPE'][agent]
        if type == 'BATTERY':
            battery_daily_results = pd.DataFrame(agents_results[agent][day].values())
            battery_kw = pd.DataFrame(1000 * battery_daily_results['S'])
            state_of_charge = pd.DataFrame(100 * battery_daily_results['Soc'])
            if len(bat_dispatch) == 0:
                bat_dispatch = battery_kw
                bat_dispatch = bat_dispatch.rename(columns={'S': name})
                bat_soc = state_of_charge
                bat_soc = bat_soc.rename(columns={'Soc': name})
            else:
                bat_dispatch = pd.concat([bat_dispatch, battery_kw], axis=1)
                bat_dispatch = bat_dispatch.rename(columns={'S': name})
                bat_soc = pd.concat([bat_soc, state_of_charge], axis=1)
                bat_soc = bat_soc.rename(columns={'Soc': name})
        if type == 'CONSUMER':
            agent_daily_results = pd.DataFrame(agents_results[agent][day].values())
            agent_kw = 1000 * agent_daily_results['P']
            agent_kw = agent_kw.rename({'0': name}, axis='columns')
            if len(load_dispatch) == 0:
                load_dispatch = agent_kw
                load_dispatch = load_dispatch.rename(name)
            else:
                load_dispatch = pd.concat([load_dispatch, agent_kw], axis=1)
                load_dispatch = load_dispatch.rename(columns={'P': name})
        if type == 'PRODUCER':
            agent_daily_results = pd.DataFrame(agents_results[agent][day].values())
            agent_kw = 1000 * agent_daily_results['P']
            if len(gen_dispatch) == 0:
                gen_dispatch = agent_kw
                gen_dispatch = gen_dispatch.rename(name)
            else:
                gen_dispatch = pd.concat([gen_dispatch, agent_kw], axis=1)
                gen_dispatch = gen_dispatch.rename(columns={'P': name})

    ##### OPENDSS BUS VOLTAGE RESULTS
    buses_volt_pu = []
    for bus in community_buses:
        base_vmag = []
        idx = np.where(lvbus_names == bus)
        bus_vmag = pd.DataFrame(community_bus_results[bus][day].values())
        for i in range(0, len(bus_vmag['Vmag'])):
            if isinstance(bus_vmag['Vmag'][i], str):
                bus_vmag['Vmag'][i] = float(bus_vmag['Vmag'][i].strip('_3PH'))
                base_vmag.append(208)
            else:
                base_vmag.append(lvbus_basekv[idx[0][0]] * 1000)
        bus_vmag_pu = pd.Series([x / y for x, y in zip(bus_vmag['Vmag'], base_vmag)])
        if len(buses_volt_pu) == 0:
            buses_volt_pu = bus_vmag_pu
            buses_volt_pu = buses_volt_pu.rename(bus)
        else:
            buses_volt_pu = pd.concat([buses_volt_pu, bus_vmag_pu], axis=1)
            buses_volt_pu = buses_volt_pu.rename(columns={0: bus})

    problem_buses = []
    for bus in community_buses:
        if any(vmag <= 0.95 or vmag >= 1.05 for vmag in buses_volt_pu[bus]):
            if len(problem_buses) == 0:
                problem_buses = pd.DataFrame(buses_volt_pu[bus])
                problem_buses = problem_buses.rename(columns={0: bus})
            else:
                problem_buses = pd.concat([problem_buses, buses_volt_pu[bus]], axis=1)
                problem_buses = problem_buses.rename(columns={0: bus})

    ##### OPENDSS LINE LOADING RESULTS
    lines_amps_mag = []
    lines_amps_pu = []
    for line in community_lines:
        line_daily_results = pd.DataFrame(community_lines_results[line][day].values())
        line_current_mag = line_daily_results['Imag']
        line_current_pu = 100 * line_daily_results['Imag_pu']
        if len(lines_amps_mag) == 0:
            lines_amps_mag = line_current_mag
            lines_amps_mag = lines_amps_mag.rename(line)
        else:
            lines_amps_mag = pd.concat([lines_amps_mag, line_current_mag], axis=1)
            lines_amps_mag = lines_amps_mag.rename(columns={'Imag': line})
        if len(lines_amps_pu) == 0:
            lines_amps_pu = line_current_pu
            lines_amps_pu = lines_amps_pu.rename(line)
        else:
            lines_amps_pu = pd.concat([lines_amps_pu, line_current_pu], axis=1)
            lines_amps_pu = lines_amps_pu.rename(columns={'Imag_pu': line})

    problem_lines = []
    for line in community_lines:
        if any(imag > 100 for imag in lines_amps_pu[line]):
            if len(problem_lines) == 0:
                problem_lines = lines_amps_pu[line]
            else:
                problem_lines = pd.concat([problem_lines, lines_amps_pu[line]], axis=1)

    return bat_soc, bat_dispatch, load_dispatch, gen_dispatch, buses_volt_pu, problem_buses, lines_amps_mag, lines_amps_pu, problem_lines

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX - MAIN - XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX #
n_days = 1
n_hours = 24
n_agents = len(load_data) + len(gen_data) + 2  # two extra agents representing external_grid
if battery_size != 0:
    n_agents = len(load_data) + len(gen_data) + len(bat_data) + 2  # one battery per community and two extra agents representing external_grid
n_communities = max(max(load_community), max(gen_community)) + 1  # agent communities plus external grid community

agents_df = agents_info()

community_buses = []
community_lines = []
for i in range(0,n_agents-2):
    bus = agents_df['BUS'][i]
    if bus not in community_buses:
        community_buses.append(bus)
    if bus in lvline_from.values:
        idx = [i for i,j in enumerate(lvline_from) if j == bus]
        for i in range(0,len(idx)):
            community_lines.append(lvline_names[idx[i]])
    if bus in lvline_to:
        idx = [i for i,j in enumerate(lvline_to) if j == bus]
        for i in range(0,len(idx)):
            community_lines.append(lvline_names[idx[i]])
    community_lines = list(set(community_lines))

# num_all_buses = len(lvbus_data) + len(mvbus_data)
num_community_buses = len(community_buses)
# num_all_lines = len(lvline_data) + len(mvline_data)
num_community_lines =  len(community_lines)

# LOADING RESULTS DICTIONARIES
optimization_results = np.load(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_optimization_results.npy',allow_pickle='TRUE').item()
agents_results = np.load(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_agents_results.npy',allow_pickle='TRUE').item()
communities_results = np.load(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_communities_results.npy',allow_pickle='TRUE').item()
community_bus_results = np.load(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_community_bus_results.npy',allow_pickle='TRUE').item()
community_lines_results = np.load(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_community_lines_results.npy',allow_pickle='TRUE').item()

for day in range(0, n_days):
    ### PLOTTING NETWORK IN PANDAPOWER
    # pandapower_plot()
    ### RESULTS DATA PROCESSING
    [bat_soc, bat_dispatch, load_dispatch, gen_dispatch, buses_volt_pu, problem_buses, lines_amps_mag, lines_amps_pu, problem_lines] = data_processing(agents_df)
    ### COMMUNITY SOCIAL WELFARE PLOT
    social_welfare_plot()
    ### BATTERY RESULT PLOTS
    battery_state_of_charge_plot(bat_soc)
    last_soc_of_day = bat_soc[-1:]
    # battery_dispatch_plot(bat_dispatch)
    # total_battery_dispatch_plot(bat_dispatch)
    ### LOAD RESULT PLOTS
    # load_dispatch_plot(load_dispatch)
    # total_load_dispatch_plot(load_dispatch, bat_dispatch)
    ### GENERATOR RESULT PLOTS
    # generators_dispatch_plot(gen_dispatch)
    # total_generators_dispatch_plot(gen_dispatch, bat_dispatch)
    ### COMMUNITY DISPATCH RESULT PLOTS
    community_energy_balance_plot(bat_dispatch, load_dispatch, gen_dispatch)
    ### OPENDSS NETWORK RESULTS PLOTS
    # bus_voltage_pu_plot(buses_volt_pu)
    problem_buses_pu_plot(problem_buses)
    # line_loading_mag_plot(lines_amps_mag)
    # line_loading_pu_plot(lines_amps_pu)
    # problem_lines_pu_plot(problem_lines)
    plt.show()