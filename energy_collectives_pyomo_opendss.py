"""
Created on Thu Sep  9 15:19:47 2021

@author: PPeters
"""

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
# import py_dss_interface as pydss
from pyomo.environ import *
from pandapower.plotting import simple_plot, simple_plotly

import sys
# sys.exit()

# CASE STUDY
case = 6            # options = [1,2,3,4,5,6,7]
battery_size = 1    # options = [0,1,3,5,10]  -> 0 = no battery // 1 = base battery // 10 = 10x base battery

# ...::: IMPORTING DATA :::...
# HIGH VOLTAGE BUSES DATA
hvbus_data = pd.read_csv(r"data/dss_data/BusListHV.csv", delimiter=',')
hvbus_names = hvbus_data['NAME']
hvbus_basekv = hvbus_data['BASE_KV']
hvbus_latitude = hvbus_data['LATITUDE']
hvbus_longitude = hvbus_data['LONGITUDE']
hvbus_geodata = list(zip(hvbus_latitude, hvbus_longitude))
# MEDIUM VOLTAGE BUSES DATA
mvbus_data = pd.read_csv(r"data/dss_data/BusListMV.csv", delimiter=',')
mvbus_names = mvbus_data['NAME']
mvbus_basekv = mvbus_data['BASE_KV']
mvbus_latitude = mvbus_data['LATITUDE']
mvbus_longitude = mvbus_data['LONGITUDE']
mvbus_geodata = list(zip(mvbus_latitude, mvbus_longitude))
# LOW VOLTAGE BUSES DATA
lvbus_data = pd.read_csv(r"data/dss_data/BusListLV.csv", delimiter=',')
lvbus_names = lvbus_data['NAME']
lvbus_basekv = lvbus_data['BASE_KV']
lvbus_latitude = lvbus_data['LATITUDE']
lvbus_longitude = lvbus_data['LONGITUDE']
lvbus_geodata = list(zip(lvbus_latitude, lvbus_longitude))
# MEDIUM VOLTAGE LINES DATA
mvline_data = pd.read_csv(r"data/dss_data/LinesListMV.csv", delimiter=',')
mvline_names = mvline_data['NAME']
mvline_from = mvline_data['BUS_FROM']
mvline_to = mvline_data['BUS_TO']
mvline_length = mvline_data['LENGTH[M]']
mvline_geometry = mvline_data['GEOMETRY']
mvline_basekv = mvline_data['BASE_KV']
# LOW VOLTAGE LINES DATA
lvline_data = pd.read_csv(r"data/dss_data/LinesListLV.csv", delimiter=',')
lvline_names = lvline_data['NAME']
lvline_from = lvline_data['BUS_FROM']
lvline_to = lvline_data['BUS_TO']
lvline_length = lvline_data['LENGTH[M]']
lvline_geometry = lvline_data['GEOMETRY']
lvline_basekv = lvline_data['BASE_KV']
# SUBSTATIONS DATA - THREE WINDING TRANSFORMER
trafo3w_data = pd.read_csv(r"data/dss_data/SubstationList.csv", delimiter=',')
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
trafo_data = pd.read_csv(r"data/dss_data/TransformersList.csv", delimiter=',')
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
load_data = pd.read_csv(r"data/dss_data/LoadsList_Caso0%s.csv" % case, delimiter=',')
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
gen_data = pd.read_csv(r"data/dss_data/PvList_Caso0%s.csv" % case, delimiter=',')
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
bat_data = pd.read_csv(r"data/dss_data/BatteryList_Caso0%s.csv" % case, delimiter=',')
bat_name = bat_data['NAME']
bat_bus = bat_data['BUS']
bat_community = bat_data['COMMUNITY']
bat_basekw = bat_data['BASE_KW']*battery_size
bat_capacity = bat_data['NOMINAL_CAPACITY_[KWH]']*battery_size
bat_socmax = bat_data['SOC_MAX']
bat_socmin = bat_data['SOC_MIN']
bat_socinit = bat_data['SOC_INIT']
bat_chargeeff = bat_data['CHARGE_EFF']
bat_dischargeeff = bat_data['DISCHARGE_EFF']
bat_chargerate = bat_data['CHARGE_RATE']
bat_dischargerate = bat_data['DISCHARGE_RATE']
bat_autodischargerate = bat_data['AUTODISCHARGE_RATE']
bat_loadshape = bat_data['LOADSHAPE']

# FIX BATTERY DATA!!!

# XXX - FUNCTION TO FILTER LOADSHAPE AND GENSHAPE CURVES
def profile_curves():
    # profiles_path = r"data/profiles"
    profiles_path = r"data/profiles_edited/"
    # PV PROFILE
    BatteryProfile = pd.read_csv('%s/storage/BatteryProfile.txt' % profiles_path, header=None)
    # PV PROFILE
    PVprofile = pd.read_csv('%s/DG/PVprofile.txt' % profiles_path, header=None)
    # COMERCIAL PROFILE
    curve349_00C = pd.read_csv('%s/commercial/curve349_00C.txt' % profiles_path,   header=None)
    curve798_69C = pd.read_csv('%s/commercial/curve798_69C.txt' % profiles_path,   header=None)
    # INDUSTRIAL PROFILE
    curve52756_83I = pd.read_csv('%s/industrial/curve52756_83I.txt' % profiles_path,   header=None)
    curve149733_90I = pd.read_csv('%s/industrial/curve149733_90I.txt' % profiles_path,   header=None)
    curve192342_97I = pd.read_csv('%s/industrial/curve192342_97I.txt' % profiles_path,   header=None)
    # RESIDENTIAL PROFILE
    curve0_00R = pd.read_csv('%s/residential/curve0_00R.txt' % profiles_path,   header=None)
    curve1003_00R = pd.read_csv('%s/residential/curve1003_00R.txt' % profiles_path,   header=None)
    curve1032_00R = pd.read_csv('%s/residential/curve1032_00R.txt' % profiles_path,   header=None)
    curve103_00R = pd.read_csv('%s/residential/curve103_00R.txt' % profiles_path,   header=None)
    curve1064_00R = pd.read_csv('%s/residential/curve1064_00R.txt' % profiles_path,   header=None)
    curve107_00R = pd.read_csv('%s/residential/curve107_00R.txt' % profiles_path,   header=None)
    curve1094_00R = pd.read_csv('%s/residential/curve1094_00R.txt' % profiles_path,   header=None)
    curve10_00R = pd.read_csv('%s/residential/curve10_00R.txt' % profiles_path,   header=None)
    curve112_00R = pd.read_csv('%s/residential/curve112_00R.txt' % profiles_path,   header=None)
    curve1138_00R = pd.read_csv('%s/residential/curve1138_00R.txt' % profiles_path,   header=None)
    curve115_00R = pd.read_csv('%s/residential/curve115_00R.txt' % profiles_path,   header=None)
    curve1180_00R = pd.read_csv('%s/residential/curve1180_00R.txt' % profiles_path,   header=None)
    curve118_00R = pd.read_csv('%s/residential/curve118_00R.txt' % profiles_path,   header=None)
    curve11_00R = pd.read_csv('%s/residential/curve11_00R.txt' % profiles_path,   header=None)
    curve121_00R = pd.read_csv('%s/residential/curve121_00R.txt' % profiles_path,   header=None)
    curve1229_00R = pd.read_csv('%s/residential/curve1229_00R.txt' % profiles_path,   header=None)
    curve124_00R = pd.read_csv('%s/residential/curve124_00R.txt' % profiles_path,   header=None)
    curve1272_00R = pd.read_csv('%s/residential/curve1272_00R.txt' % profiles_path,   header=None)
    curve127_00R = pd.read_csv('%s/residential/curve127_00R.txt' % profiles_path,   header=None)
    curve12_00R = pd.read_csv('%s/residential/curve12_00R.txt' % profiles_path,   header=None)
    curve132_00R = pd.read_csv('%s/residential/curve132_00R.txt' % profiles_path,   header=None)
    curve1344_00R = pd.read_csv('%s/residential/curve1344_00R.txt' % profiles_path,   header=None)
    curve136_00R = pd.read_csv('%s/residential/curve136_00R.txt' % profiles_path,   header=None)
    curve1380_00R = pd.read_csv('%s/residential/curve1380_00R.txt' % profiles_path,   header=None)
    curve139_43R = pd.read_csv('%s/residential/curve139_43R.txt' % profiles_path,   header=None)
    curve13_00R = pd.read_csv('%s/residential/curve13_00R.txt' % profiles_path,   header=None)
    curve1416_00R = pd.read_csv('%s/residential/curve1416_00R.txt' % profiles_path,   header=None)
    curve143_00R = pd.read_csv('%s/residential/curve143_00R.txt' % profiles_path,   header=None)
    curve1448_00R = pd.read_csv('%s/residential/curve1448_00R.txt' % profiles_path,   header=None)
    curve146_00R = pd.read_csv('%s/residential/curve146_00R.txt' % profiles_path,   header=None)
    curve14_00R = pd.read_csv('%s/residential/curve14_00R.txt' % profiles_path,   header=None)
    curve150_00R = pd.read_csv('%s/residential/curve150_00R.txt' % profiles_path,   header=None)
    curve1544_00R = pd.read_csv('%s/residential/curve1544_00R.txt' % profiles_path,   header=None)
    curve154_00R = pd.read_csv('%s/residential/curve154_00R.txt' % profiles_path,   header=None)
    curve158_00R = pd.read_csv('%s/residential/curve158_00R.txt' % profiles_path,   header=None)
    curve162_00R = pd.read_csv('%s/residential/curve162_00R.txt' % profiles_path,   header=None)
    curve167_00R = pd.read_csv('%s/residential/curve167_00R.txt' % profiles_path,   header=None)
    curve1688_00R = pd.read_csv('%s/residential/curve1688_00R.txt' % profiles_path,   header=None)
    curve16_00R = pd.read_csv('%s/residential/curve16_00R.txt' % profiles_path,   header=None)
    curve172_00R = pd.read_csv('%s/residential/curve172_00R.txt' % profiles_path,   header=None)
    curve177_00R = pd.read_csv('%s/residential/curve177_00R.txt' % profiles_path,   header=None)
    curve180_93R = pd.read_csv('%s/residential/curve180_93R.txt' % profiles_path,   header=None)
    curve1840_00R = pd.read_csv('%s/residential/curve1840_00R.txt' % profiles_path,   header=None)
    curve188_00R = pd.read_csv('%s/residential/curve188_00R.txt' % profiles_path,   header=None)
    curve18_00R = pd.read_csv('%s/residential/curve18_00R.txt' % profiles_path,   header=None)
    curve1912_00R = pd.read_csv('%s/residential/curve1912_00R.txt' % profiles_path,   header=None)
    curve194_00R = pd.read_csv('%s/residential/curve194_00R.txt' % profiles_path,   header=None)
    curve198_33R = pd.read_csv('%s/residential/curve198_33R.txt' % profiles_path,   header=None)
    curve19_00R = pd.read_csv('%s/residential/curve19_00R.txt' % profiles_path,   header=None)
    curve1_00R = pd.read_csv('%s/residential/curve1_00R.txt' % profiles_path,   header=None)
    curve2037_00R = pd.read_csv('%s/residential/curve2037_00R.txt' % profiles_path,   header=None)
    curve207_00R = pd.read_csv('%s/residential/curve207_00R.txt' % profiles_path,   header=None)
    curve20_00R = pd.read_csv('%s/residential/curve20_00R.txt' % profiles_path,   header=None)
    curve211_74R = pd.read_csv('%s/residential/curve211_74R.txt' % profiles_path,   header=None)
    curve215_30R = pd.read_csv('%s/residential/curve215_30R.txt' % profiles_path,   header=None)
    curve217_83R = pd.read_csv('%s/residential/curve217_83R.txt' % profiles_path,   header=None)
    curve2180_00R = pd.read_csv('%s/residential/curve2180_00R.txt' % profiles_path,   header=None)
    curve219_48R = pd.read_csv('%s/residential/curve219_48R.txt' % profiles_path,   header=None)
    curve225_00R = pd.read_csv('%s/residential/curve225_00R.txt' % profiles_path,   header=None)
    curve22_00R = pd.read_csv('%s/residential/curve22_00R.txt' % profiles_path,   header=None)
    curve230_00R = pd.read_csv('%s/residential/curve230_00R.txt' % profiles_path,   header=None)
    curve2340_00R = pd.read_csv('%s/residential/curve2340_00R.txt' % profiles_path,   header=None)
    curve235_80R = pd.read_csv('%s/residential/curve235_80R.txt' % profiles_path,   header=None)
    curve2397_21R = pd.read_csv('%s/residential/curve2397_21R.txt' % profiles_path,   header=None)
    curve23_00R = pd.read_csv('%s/residential/curve23_00R.txt' % profiles_path,   header=None)
    curve242_00R = pd.read_csv('%s/residential/curve242_00R.txt' % profiles_path,   header=None)
    curve248_00R = pd.read_csv('%s/residential/curve248_00R.txt' % profiles_path,   header=None)
    curve24_00R = pd.read_csv('%s/residential/curve24_00R.txt' % profiles_path,   header=None)
    curve2500_00R = pd.read_csv('%s/residential/curve2500_00R.txt' % profiles_path,   header=None)
    curve255_96R = pd.read_csv('%s/residential/curve255_96R.txt' % profiles_path,   header=None)
    curve25_00R = pd.read_csv('%s/residential/curve25_00R.txt' % profiles_path,   header=None)
    curve264_00R = pd.read_csv('%s/residential/curve264_00R.txt' % profiles_path,   header=None)
    curve269_45R = pd.read_csv('%s/residential/curve269_45R.txt' % profiles_path,   header=None)
    curve275_00R = pd.read_csv('%s/residential/curve275_00R.txt' % profiles_path,   header=None)
    curve27_00R = pd.read_csv('%s/residential/curve27_00R.txt' % profiles_path,   header=None)
    curve2816_00R = pd.read_csv('%s/residential/curve2816_00R.txt' % profiles_path,   header=None)
    curve283_00R = pd.read_csv('%s/residential/curve283_00R.txt' % profiles_path,   header=None)
    curve28_00R = pd.read_csv('%s/residential/curve28_00R.txt' % profiles_path,   header=None)
    curve2919_00R = pd.read_csv('%s/residential/curve2919_00R.txt' % profiles_path,   header=None)
    curve292_50R = pd.read_csv('%s/residential/curve292_50R.txt' % profiles_path,   header=None)
    curve299_22R = pd.read_csv('%s/residential/curve299_22R.txt' % profiles_path,   header=None)
    curve29_00R = pd.read_csv('%s/residential/curve29_00R.txt' % profiles_path,   header=None)
    curve2_00R = pd.read_csv('%s/residential/curve2_00R.txt' % profiles_path,   header=None)
    curve301_77R = pd.read_csv('%s/residential/curve301_77R.txt' % profiles_path,   header=None)
    curve3033_00R = pd.read_csv('%s/residential/curve3033_00R.txt' % profiles_path,   header=None)
    curve304_21R = pd.read_csv('%s/residential/curve304_21R.txt' % profiles_path,   header=None)
    curve30_00R = pd.read_csv('%s/residential/curve30_00R.txt' % profiles_path,   header=None)
    curve313_00R = pd.read_csv('%s/residential/curve313_00R.txt' % profiles_path,   header=None)
    curve31_00R = pd.read_csv('%s/residential/curve31_00R.txt' % profiles_path,   header=None)
    curve325_00R = pd.read_csv('%s/residential/curve325_00R.txt' % profiles_path,   header=None)
    curve32_00R = pd.read_csv('%s/residential/curve32_00R.txt' % profiles_path,   header=None)
    curve332_00R = pd.read_csv('%s/residential/curve332_00R.txt' % profiles_path,   header=None)
    curve3332_00R = pd.read_csv('%s/residential/curve3332_00R.txt' % profiles_path,   header=None)
    curve339_00R = pd.read_csv('%s/residential/curve339_00R.txt' % profiles_path,   header=None)
    curve33_00R = pd.read_csv('%s/residential/curve33_00R.txt' % profiles_path,   header=None)
    curve346_00R = pd.read_csv('%s/residential/curve346_00R.txt' % profiles_path,   header=None)
    curve34_00R = pd.read_csv('%s/residential/curve34_00R.txt' % profiles_path,   header=None)
    curve353_33R = pd.read_csv('%s/residential/curve353_33R.txt' % profiles_path,   header=None)
    curve35_00R = pd.read_csv('%s/residential/curve35_00R.txt' % profiles_path,   header=None)
    curve361_00R = pd.read_csv('%s/residential/curve361_00R.txt' % profiles_path,   header=None)
    curve3652_00R = pd.read_csv('%s/residential/curve3652_00R.txt' % profiles_path,   header=None)
    curve369_00R = pd.read_csv('%s/residential/curve369_00R.txt' % profiles_path,   header=None)
    curve36_00R = pd.read_csv('%s/residential/curve36_00R.txt' % profiles_path,   header=None)
    curve37_00R = pd.read_csv('%s/residential/curve37_00R.txt' % profiles_path,   header=None)
    curve380_00R = pd.read_csv('%s/residential/curve380_00R.txt' % profiles_path,   header=None)
    curve38_00R = pd.read_csv('%s/residential/curve38_00R.txt' % profiles_path,   header=None)
    curve390_02R = pd.read_csv('%s/residential/curve390_02R.txt' % profiles_path,   header=None)
    curve39_00R = pd.read_csv('%s/residential/curve39_00R.txt' % profiles_path,   header=None)
    curve3_00R = pd.read_csv('%s/residential/curve3_00R.txt' % profiles_path,   header=None)
    curve401_82R = pd.read_csv('%s/residential/curve401_82R.txt' % profiles_path,   header=None)
    curve40_00R = pd.read_csv('%s/residential/curve40_00R.txt' % profiles_path,   header=None)
    curve413_00R = pd.read_csv('%s/residential/curve413_00R.txt' % profiles_path,   header=None)
    curve41_00R = pd.read_csv('%s/residential/curve41_00R.txt' % profiles_path,   header=None)
    curve423_36R = pd.read_csv('%s/residential/curve423_36R.txt' % profiles_path,   header=None)
    curve434_00R = pd.read_csv('%s/residential/curve434_00R.txt' % profiles_path,   header=None)
    curve43_00R = pd.read_csv('%s/residential/curve43_00R.txt' % profiles_path,   header=None)
    curve445_44R = pd.read_csv('%s/residential/curve445_44R.txt' % profiles_path,   header=None)
    curve459_00R = pd.read_csv('%s/residential/curve459_00R.txt' % profiles_path,   header=None)
    curve45_00R = pd.read_csv('%s/residential/curve45_00R.txt' % profiles_path,   header=None)
    curve46_00R = pd.read_csv('%s/residential/curve46_00R.txt' % profiles_path,   header=None)
    curve470_34R = pd.read_csv('%s/residential/curve470_34R.txt' % profiles_path,   header=None)
    curve47_00R = pd.read_csv('%s/residential/curve47_00R.txt' % profiles_path,   header=None)
    curve481_00R = pd.read_csv('%s/residential/curve481_00R.txt' % profiles_path,   header=None)
    curve48_00R = pd.read_csv('%s/residential/curve48_00R.txt' % profiles_path,   header=None)
    curve495_60R = pd.read_csv('%s/residential/curve495_60R.txt' % profiles_path,   header=None)
    curve49_00R = pd.read_csv('%s/residential/curve49_00R.txt' % profiles_path,   header=None)
    curve4_00R = pd.read_csv('%s/residential/curve4_00R.txt' % profiles_path,   header=None)
    curve506_00R = pd.read_csv('%s/residential/curve506_00R.txt' % profiles_path,   header=None)
    curve519_00R = pd.read_csv('%s/residential/curve519_00R.txt' % profiles_path,   header=None)
    curve51_00R = pd.read_csv('%s/residential/curve51_00R.txt' % profiles_path,   header=None)
    curve530_25R = pd.read_csv('%s/residential/curve530_25R.txt' % profiles_path,   header=None)
    curve53_00R = pd.read_csv('%s/residential/curve53_00R.txt' % profiles_path,   header=None)
    curve544_45R = pd.read_csv('%s/residential/curve544_45R.txt' % profiles_path,   header=None)
    curve556_00R = pd.read_csv('%s/residential/curve556_00R.txt' % profiles_path,   header=None)
    curve5572_00R = pd.read_csv('%s/residential/curve5572_00R.txt' % profiles_path,   header=None)
    curve567_55R = pd.read_csv('%s/residential/curve567_55R.txt' % profiles_path,   header=None)
    curve56_00R = pd.read_csv('%s/residential/curve56_00R.txt' % profiles_path,   header=None)
    curve582_00R = pd.read_csv('%s/residential/curve582_00R.txt' % profiles_path,   header=None)
    curve58_00R = pd.read_csv('%s/residential/curve58_00R.txt' % profiles_path,   header=None)
    curve597_00R = pd.read_csv('%s/residential/curve597_00R.txt' % profiles_path,   header=None)
    curve5_00R = pd.read_csv('%s/residential/curve5_00R.txt' % profiles_path,   header=None)
    curve610_00R = pd.read_csv('%s/residential/curve610_00R.txt' % profiles_path,   header=None)
    curve61_00R = pd.read_csv('%s/residential/curve61_00R.txt' % profiles_path,   header=None)
    curve625_00R = pd.read_csv('%s/residential/curve625_00R.txt' % profiles_path,   header=None)
    curve63_00R = pd.read_csv('%s/residential/curve63_00R.txt' % profiles_path,   header=None)
    curve641_00R = pd.read_csv('%s/residential/curve641_00R.txt' % profiles_path,   header=None)
    curve658_00R = pd.read_csv('%s/residential/curve658_00R.txt' % profiles_path,   header=None)
    curve66_00R = pd.read_csv('%s/residential/curve66_00R.txt' % profiles_path,   header=None)
    curve677_00R = pd.read_csv('%s/residential/curve677_00R.txt' % profiles_path,   header=None)
    curve692_00R = pd.read_csv('%s/residential/curve692_00R.txt' % profiles_path,   header=None)
    curve69_00R = pd.read_csv('%s/residential/curve69_00R.txt' % profiles_path,   header=None)
    curve6_00R = pd.read_csv('%s/residential/curve6_00R.txt' % profiles_path,   header=None)
    curve71_00R = pd.read_csv('%s/residential/curve71_00R.txt' % profiles_path,   header=None)
    curve721_00R = pd.read_csv('%s/residential/curve721_00R.txt' % profiles_path,   header=None)
    curve737_00R = pd.read_csv('%s/residential/curve737_00R.txt' % profiles_path,   header=None)
    curve73_00R = pd.read_csv('%s/residential/curve73_00R.txt' % profiles_path,   header=None)
    curve760_00R = pd.read_csv('%s/residential/curve760_00R.txt' % profiles_path,   header=None)
    curve76_00R = pd.read_csv('%s/residential/curve76_00R.txt' % profiles_path,   header=None)
    curve778_00R = pd.read_csv('%s/residential/curve778_00R.txt' % profiles_path,   header=None)
    curve7911_00R = pd.read_csv('%s/residential/curve7911_00R.txt' % profiles_path,   header=None)
    curve796_04R = pd.read_csv('%s/residential/curve796_04R.txt' % profiles_path,   header=None)
    curve79_00R = pd.read_csv('%s/residential/curve79_00R.txt' % profiles_path,   header=None)
    curve7_00R = pd.read_csv('%s/residential/curve7_00R.txt' % profiles_path,   header=None)
    curve81_00R = pd.read_csv('%s/residential/curve81_00R.txt' % profiles_path,   header=None)
    curve820_00R = pd.read_csv('%s/residential/curve820_00R.txt' % profiles_path,   header=None)
    curve83_00R = pd.read_csv('%s/residential/curve83_00R.txt' % profiles_path,   header=None)
    curve841_00R = pd.read_csv('%s/residential/curve841_00R.txt' % profiles_path,   header=None)
    curve86_00R = pd.read_csv('%s/residential/curve86_00R.txt' % profiles_path,   header=None)
    curve870_00R = pd.read_csv('%s/residential/curve870_00R.txt' % profiles_path,   header=None)
    curve888_00R = pd.read_csv('%s/residential/curve888_00R.txt' % profiles_path,   header=None)
    curve89_00R = pd.read_csv('%s/residential/curve89_00R.txt' % profiles_path,   header=None)
    curve8_00R = pd.read_csv('%s/residential/curve8_00R.txt' % profiles_path,   header=None)
    curve913_00R = pd.read_csv('%s/residential/curve913_00R.txt' % profiles_path,   header=None)
    curve91_00R = pd.read_csv('%s/residential/curve91_00R.txt' % profiles_path,   header=None)
    curve934_00R = pd.read_csv('%s/residential/curve934_00R.txt' % profiles_path,   header=None)
    curve93_00R = pd.read_csv('%s/residential/curve93_00R.txt' % profiles_path,   header=None)
    curve95_00R = pd.read_csv('%s/residential/curve95_00R.txt' % profiles_path,   header=None)
    curve968_00R = pd.read_csv('%s/residential/curve968_00R.txt' % profiles_path,   header=None)
    curve98_00R = pd.read_csv('%s/residential/curve98_00R.txt' % profiles_path,   header=None)
    profiles_dict = {
        'BatteryProfile': -BatteryProfile,
        'PVprofile': PVprofile,
        'curve349_00C': curve349_00C,
        'curve798_69C': curve798_69C,
        'curve52756_83I': curve52756_83I,
        'curve149733_90I': curve149733_90I,
        'curve192342_97I': curve192342_97I,
        'curve0_00R': curve0_00R,
        'curve1003_00R': curve1003_00R,
        'curve1032_00R': curve1032_00R,
        'curve103_00R': curve103_00R,
        'curve1064_00R': curve1064_00R,
        'curve107_00R': curve107_00R,
        'curve1094_00R': curve1094_00R,
        'curve10_00R': curve10_00R,
        'curve112_00R': curve112_00R,
        'curve1138_00R': curve1138_00R,
        'curve115_00R': curve115_00R,
        'curve1180_00R': curve1180_00R,
        'curve118_00R': curve118_00R,
        'curve11_00R': curve11_00R,
        'curve121_00R': curve121_00R,
        'curve1229_00R': curve1229_00R,
        'curve124_00R': curve124_00R,
        'curve1272_00R': curve1272_00R,
        'curve127_00R': curve127_00R,
        'curve12_00R': curve12_00R,
        'curve132_00R': curve132_00R,
        'curve1344_00R': curve1344_00R,
        'curve136_00R': curve136_00R,
        'curve1380_00R': curve1380_00R,
        'curve139_43R': curve139_43R,
        'curve13_00R': curve13_00R,
        'curve1416_00R': curve1416_00R,
        'curve143_00R': curve143_00R,
        'curve1448_00R': curve1448_00R,
        'curve146_00R': curve146_00R,
        'curve14_00R': curve14_00R,
        'curve150_00R': curve150_00R,
        'curve1544_00R': curve1544_00R,
        'curve154_00R': curve154_00R,
        'curve158_00R': curve158_00R,
        'curve162_00R': curve162_00R,
        'curve167_00R': curve167_00R,
        'curve1688_00R': curve1688_00R,
        'curve16_00R': curve16_00R,
        'curve172_00R': curve172_00R,
        'curve177_00R': curve177_00R,
        'curve180_93R': curve180_93R,
        'curve1840_00R': curve1840_00R,
        'curve188_00R': curve188_00R,
        'curve18_00R': curve18_00R,
        'curve1912_00R': curve1912_00R,
        'curve194_00R': curve194_00R,
        'curve198_33R': curve198_33R,
        'curve19_00R': curve19_00R,
        'curve1_00R': curve1_00R,
        'curve2037_00R': curve2037_00R,
        'curve207_00R': curve207_00R,
        'curve20_00R': curve20_00R,
        'curve211_74R': curve211_74R,
        'curve215_30R': curve215_30R,
        'curve217_83R': curve217_83R,
        'curve2180_00R': curve2180_00R,
        'curve219_48R': curve219_48R,
        'curve225_00R': curve225_00R,
        'curve22_00R': curve22_00R,
        'curve230_00R': curve230_00R,
        'curve2340_00R': curve2340_00R,
        'curve235_80R': curve235_80R,
        'curve2397_21R': curve2397_21R,
        'curve23_00R': curve23_00R,
        'curve242_00R': curve242_00R,
        'curve248_00R': curve248_00R,
        'curve24_00R': curve24_00R,
        'curve2500_00R': curve2500_00R,
        'curve255_96R': curve255_96R,
        'curve25_00R': curve25_00R,
        'curve264_00R': curve264_00R,
        'curve269_45R': curve269_45R,
        'curve275_00R': curve275_00R,
        'curve27_00R': curve27_00R,
        'curve2816_00R': curve2816_00R,
        'curve283_00R': curve283_00R,
        'curve28_00R': curve28_00R,
        'curve2919_00R': curve2919_00R,
        'curve292_50R': curve292_50R,
        'curve299_22R': curve299_22R,
        'curve29_00R': curve29_00R,
        'curve2_00R': curve2_00R,
        'curve301_77R': curve301_77R,
        'curve3033_00R': curve3033_00R,
        'curve304_21R': curve304_21R,
        'curve30_00R': curve30_00R,
        'curve313_00R': curve313_00R,
        'curve31_00R': curve31_00R,
        'curve325_00R': curve325_00R,
        'curve32_00R': curve32_00R,
        'curve332_00R': curve332_00R,
        'curve3332_00R': curve3332_00R,
        'curve339_00R': curve339_00R,
        'curve33_00R': curve33_00R,
        'curve346_00R': curve346_00R,
        'curve34_00R': curve34_00R,
        'curve353_33R': curve353_33R,
        'curve35_00R': curve35_00R,
        'curve361_00R': curve361_00R,
        'curve3652_00R': curve3652_00R,
        'curve369_00R': curve369_00R,
        'curve36_00R': curve36_00R,
        'curve37_00R': curve37_00R,
        'curve380_00R': curve380_00R,
        'curve38_00R': curve38_00R,
        'curve390_02R': curve390_02R,
        'curve39_00R': curve39_00R,
        'curve3_00R': curve3_00R,
        'curve401_82R': curve401_82R,
        'curve40_00R': curve40_00R,
        'curve413_00R': curve413_00R,
        'curve41_00R': curve41_00R,
        'curve423_36R': curve423_36R,
        'curve434_00R': curve434_00R,
        'curve43_00R': curve43_00R,
        'curve445_44R': curve445_44R,
        'curve459_00R': curve459_00R,
        'curve45_00R': curve45_00R,
        'curve46_00R': curve46_00R,
        'curve470_34R': curve470_34R,
        'curve47_00R': curve47_00R,
        'curve481_00R': curve481_00R,
        'curve48_00R': curve48_00R,
        'curve495_60R': curve495_60R,
        'curve49_00R': curve49_00R,
        'curve4_00R': curve4_00R,
        'curve506_00R': curve506_00R,
        'curve519_00R': curve519_00R,
        'curve51_00R': curve51_00R,
        'curve530_25R': curve530_25R,
        'curve53_00R': curve53_00R,
        'curve544_45R': curve544_45R,
        'curve556_00R': curve556_00R,
        'curve5572_00R': curve5572_00R,
        'curve567_55R': curve567_55R,
        'curve56_00R': curve56_00R,
        'curve582_00R': curve582_00R,
        'curve58_00R': curve58_00R,
        'curve597_00R': curve597_00R,
        'curve5_00R': curve5_00R,
        'curve610_00R': curve610_00R,
        'curve61_00R': curve61_00R,
        'curve625_00R': curve625_00R,
        'curve63_00R': curve63_00R,
        'curve641_00R': curve641_00R,
        'curve658_00R': curve658_00R,
        'curve66_00R': curve66_00R,
        'curve677_00R': curve677_00R,
        'curve692_00R': curve692_00R,
        'curve69_00R': curve69_00R,
        'curve6_00R': curve6_00R,
        'curve71_00R': curve71_00R,
        'curve721_00R': curve721_00R,
        'curve737_00R': curve737_00R,
        'curve73_00R': curve73_00R,
        'curve760_00R': curve760_00R,
        'curve76_00R': curve76_00R,
        'curve778_00R': curve778_00R,
        'curve7911_00R': curve7911_00R,
        'curve796_04R': curve796_04R,
        'curve79_00R': curve79_00R,
        'curve7_00R': curve7_00R,
        'curve81_00R': curve81_00R,
        'curve820_00R': curve820_00R,
        'curve83_00R': curve83_00R,
        'curve841_00R': curve841_00R,
        'curve86_00R': curve86_00R,
        'curve870_00R': curve870_00R,
        'curve888_00R': curve888_00R,
        'curve89_00R': curve89_00R,
        'curve8_00R': curve8_00R,
        'curve913_00R': curve913_00R,
        'curve91_00R': curve91_00R,
        'curve934_00R': curve934_00R,
        'curve93_00R': curve93_00R,
        'curve95_00R': curve95_00R,
        'curve968_00R': curve968_00R,
        'curve98_00R': curve98_00R}
    return profiles_dict

# XXX - FUNCTION TO UPDATE LOADSHAPES WITH OPTIMIZATION RESULTS
def profile_curves_update(hour,agt_results):
    j=0
    for i in range(0,n_agents):
        profile_name = agents_df['PROFILE'][i]
        if profile_name.endswith('R'):  # residential loadshapes
            profiles_path = r"data/profiles_edited/\residential"
            profiles_dict[profile_name][0][hour] = abs(agt_results['P_n'][i])/agents_df['BASE_KW'][i]
            df = pd.DataFrame(profiles_dict[profile_name])
            df.to_csv('%s\%s.csv' % (profiles_path,profile_name), sep=',', index=False, header=False)
        if profile_name.endswith('I'):  # industrial loadshapes
            profiles_path = r"data/profiles_edited/\industrial"
            profiles_dict[profile_name][0][hour] = abs(agt_results['P_n'][i])/agents_df['BASE_KW'][i]
            df = pd.DataFrame(profiles_dict[profile_name])
            df.to_csv('%s\%s.csv' % (profiles_path,profile_name), sep=',', index=False, header=False)
        if profile_name.endswith('C'):  # commercial loadshapes
            profiles_path = r"data/profiles_edited/\commercial"
            profiles_dict[profile_name][0][hour] = abs(agt_results['P_n'][i])/agents_df['BASE_KW'][i]
            df = pd.DataFrame(profiles_dict[profile_name])
            df.to_csv('%s\%s.csv' % (profiles_path,profile_name), sep=',', index=False, header=False)
        if profile_name.startswith('PV'):  # photovoltaic loadshapes
            profiles_path = r"data/profiles_edited/\DG"
            profiles_dict[profile_name][0][hour] = abs(agt_results['P_n'][i])/agents_df['BASE_KW'][i]
            df = pd.DataFrame(profiles_dict[profile_name])
            df.to_csv('%s\%s.csv' % (profiles_path,profile_name), sep=',', index=False, header=False)
        if profile_name.startswith('Battery'):  # storage loadshapes
            profiles_path = r"data/profiles_edited/\storage"
            # profiles_dict[profile_name][0][hour] = - agt_results['S_n'][i]/bat_capacity[j]
            profiles_dict[profile_name][0][hour] = - agt_results['S_n'][i]/agents_df['BASE_KW'][i]
            j = j+1
            df = pd.DataFrame(profiles_dict[profile_name])
            df.to_csv('%s\%s.csv' % (profiles_path,profile_name), sep=',', index=False, header=False)
    return profiles_dict

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

# XXX - FUNCTION TO FILTER COSTS INFORMATION
def costs_info(agents_df):
    agent_number = agents_df['AGENT']
    agent_name = agents_df['NAME']
    agent_type = agents_df['TYPE']
    a_doll_kw2 = []
    b_doll_kw = []
    cost_s = []
    inner_cost = []
    imp_cost = []
    exp_cost = []

    gen_costs = pd.read_csv(r"data/dss_data/PvList_Cost.csv", delimiter=',')
    load_costs = pd.read_csv(r"data/dss_data/LoadsList_Cost.csv", delimiter=',')
    mkt_costs = pd.read_csv(r"data/dss_data/00_Market_price_hourly_brasil.csv", delimiter=',')
    bat_costs = pd.read_csv(r"data/dss_data/BatteryList_Cost.csv", delimiter=',')

    for i in range(0,len(agent_number)):
        if agent_type[i]=='CONSUMER':
            index_val = load_costs[load_costs['NAME'] == agent_name[i]].index.values
            a_doll_kw2.append(load_costs['A_[R$/KW^2]'][index_val[0]])
            b_doll_kw.append(load_costs['B_[R$/KW]'][index_val[0]])
            cost_s.append(0.0)
            inner_cost.append(0.001)
            imp_cost.append(0.0)
            exp_cost.append(0.0)
        if agent_type[i]=='PRODUCER':
            index_val = gen_costs[gen_costs['NAME'] == agent_name[i]].index.values
            a_doll_kw2.append(gen_costs['A_[R$/KW^2]'][index_val[0]])
            b_doll_kw.append(gen_costs['B_[R$/KW]'][index_val[0]])
            cost_s.append(0.0)
            inner_cost.append(0.001)
            imp_cost.append(0.0)
            exp_cost.append(0.0)
        if agent_type[i]=='BATTERY':
            a_doll_kw2.append(0.0)
            b_doll_kw.append(0.0)
            cost_s.append(bat_costs['COST_S'][hour])
            inner_cost.append(0.001)
            imp_cost.append(0.0)
            exp_cost.append(0.0)
        if agent_type[i]=='EXT_CONSUMER':
            a_doll_kw2.append(0.0)
            b_doll_kw.append(0.0)
            cost_s.append(0.0)
            inner_cost.append(0.0)
            imp_cost.append(0.0)
            exp_cost.append(mkt_costs['EXPORT_PRICE(R$/MWh)'][hour]/1000)
        if agent_type[i]=='EXT_PRODUCER':
            a_doll_kw2.append(0.0)
            b_doll_kw.append(0.0)
            cost_s.append(0.0)
            inner_cost.append(0.0)
            imp_cost.append(mkt_costs['IMPORT_PRICE(R$/MWh)'][hour]/1000)
            exp_cost.append(0.0)

    costs_data = {'AGENT': agent_number, 'NAME': agent_name, 'TYPE': agent_type, 'A_[R$/KW^2]': a_doll_kw2,
                  'B_[R$/KW]': b_doll_kw, 'COST_S': cost_s, 'INNER_COST': inner_cost, 'IMP_COST': imp_cost, 'EXP_COST': exp_cost}
    costs_df = pd.DataFrame(data=costs_data, index=None)
    return costs_df

# XXX - FUNCTION FOR ENERGY MARKET OPTIMIZATION
def pyomo_opt(agents_df,costs_df,profiles_dict):
    ##############################################
    ### ...::: PYOMO OPTIMIZATION MODEL :::... ###
    ##############################################
    model = ConcreteModel("Energy_Collectives_Linearized")

    agent_range_set = []
    for i in range(0, n_agents):
        agent_range_set.append(i)
    community_set = []
    for i in range(0, n_communities - 1):  ## all communities except grid
        community_set.append(i)
    community_range_set = []
    for i in range(0, n_communities ** 2):
        community_range_set.append(i)

    if case==1 or case==2 or case==3 or case==4 or case==5:
        mat_bilateral = np.ones((n_communities, n_communities)) - np.eye((n_communities),(n_communities))
        import_cost = np.matrix([[0.0,costs_df['IMP_COST'].max()],
                                 [costs_df['IMP_COST'].max(),0.0]])
        export_cost = np.matrix([[0.0,costs_df['EXP_COST'].max()],
                                 [costs_df['EXP_COST'].max(),0.0]])
    if case==6:
        mat_bilateral = np.ones((n_communities, n_communities)) - np.eye((n_communities), (n_communities))
        import_cost = np.matrix([[0.0,0.1,0.1,costs_df['IMP_COST'].max()],
                                 [0.1,0.0,0.1,costs_df['IMP_COST'].max()],
                                 [0.1,0.1,0.0,costs_df['IMP_COST'].max()],
                                 [costs_df['IMP_COST'].max(),costs_df['IMP_COST'].max(),costs_df['IMP_COST'].max(),0.0]])
        export_cost = np.matrix([[0.0,0.05,0.05,costs_df['EXP_COST'].max()],
                                 [0.05,0.0,0.05,costs_df['EXP_COST'].max()],
                                 [0.05,0.05,0.0,costs_df['EXP_COST'].max()],
                                 [costs_df['EXP_COST'].max(),costs_df['EXP_COST'].max(),costs_df['EXP_COST'].max(),0.0]])
    if case==7:
        mat_bilateral = np.ones((n_communities, n_communities)) - np.eye((n_communities), (n_communities))
        import_cost = np.matrix([[0.0,0.1,0.1,0.1,0.1,costs_df['IMP_COST'].max()],
                                 [0.1,0.0,0.1,0.1,0.1,costs_df['IMP_COST'].max()],
                                 [0.1,0.1,0.0,0.1,0.1,costs_df['IMP_COST'].max()],
                                 [0.1,0.1,0.1,0.0,0.1,costs_df['IMP_COST'].max()],
                                 [0.1,0.1,0.1,0.1,0.0,costs_df['IMP_COST'].max()],
                                 [costs_df['IMP_COST'].max(),costs_df['IMP_COST'].max(),costs_df['IMP_COST'].max(),costs_df['IMP_COST'].max(),costs_df['IMP_COST'].max(),0.0]])
        export_cost = np.matrix([[0.0,0.05,0.05,0.05,0.05,costs_df['EXP_COST'].max()],
                                 [0.05,0.0,0.05,0.05,0.05,costs_df['EXP_COST'].max()],
                                 [0.05,0.05,0.0,0.05,0.05,costs_df['EXP_COST'].max()],
                                 [0.05,0.05,0.05,0.0,0.05,costs_df['EXP_COST'].max()],
                                 [0.05,0.05,0.05,0.05,0.0,costs_df['EXP_COST'].max()],
                                 [costs_df['EXP_COST'].max(),costs_df['EXP_COST'].max(),costs_df['EXP_COST'].max(),costs_df['EXP_COST'].max(),costs_df['EXP_COST'].max(),0.0]])

    imp_cost = np.reshape(np.multiply(-import_cost,mat_bilateral), [1, n_communities ** 2])
    exp_cost = np.reshape(np.multiply(export_cost,mat_bilateral), [1, n_communities ** 2])

    ### Declaring Optimization Variables
    model.P_n = Var(agent_range_set, domain=Reals)
    model.Q_n = Var(agent_range_set, domain=Reals)
    # model.Qn_pos = Var(agent_range_set, domain=NonNegativeReals)
    # model.Qn_neg = Var(agent_range_set, domain=NonPositiveReals)
    model.Alpha_n = Var(agent_range_set, domain=PositiveReals)
    model.Beta_n = Var(agent_range_set, domain=PositiveReals)
    model.Qimp_c = Var(community_range_set, domain=PositiveReals)
    model.Qexp_c = Var(community_range_set, domain=PositiveReals)
    model.QoS = Var(community_set, domain=(0, 1))
    if battery_size!=0:
        model.S_n = Var(agent_range_set, domain=Reals)
        model.Soc_n = Var(agent_range_set, domain=PositiveReals)

    ### Objective Function
    def objective_rule_linear(model):
        obj_function = 0
        for j in range(0, n_agents):
            if agents_df['TYPE'][j] == 'CONSUMER':
                obj_function = obj_function - (costs_df['B_[R$/KW]'][j] * model.P_n[j])
                obj_function = obj_function - (costs_df['INNER_COST'][j] * model.Q_n[j])
            if agents_df['TYPE'][j] == 'PRODUCER':
                obj_function = obj_function - (costs_df['B_[R$/KW]'][j] * model.P_n[j])
                obj_function = obj_function - (costs_df['INNER_COST'][j] * model.Q_n[j])
            if agents_df['TYPE'][j] == 'BATTERY':
                obj_function = obj_function + (costs_df['COST_S'][j] * model.S_n[j])
                obj_function = obj_function - (costs_df['INNER_COST'][j] * model.Q_n[j])
        for j in range(0, n_communities ** 2):
            obj_function = obj_function + (imp_cost[0, j] * model.Qimp_c[j])
            obj_function = obj_function + (exp_cost[0, j] * model.Qexp_c[j])

        return obj_function
    def objective_rule_quadratic(model):
        obj_function = 0
        for j in range(0, n_agents):
            if agents_df['TYPE'][j] == 'CONSUMER':
                obj_function = obj_function - (0.5*costs_df['A_[R$/KW^2]'][j]*model.P_n[j]*model.P_n[j] + costs_df['B_[R$/KW]'][j]*model.P_n[j])
                obj_function = obj_function - (costs_df['INNER_COST'][j] * model.Q_n[j])
            if agents_df['TYPE'][j] == 'PRODUCER':
                obj_function = obj_function - (0.5*costs_df['A_[R$/KW^2]'][j]*model.P_n[j]*model.P_n[j] + costs_df['B_[R$/KW]'][j]*model.P_n[j])
                obj_function = obj_function - (costs_df['INNER_COST'][j] * model.Q_n[j])
            if agents_df['TYPE'][j] == 'BATTERY':
                obj_function = obj_function + (costs_df['COST_S'][j] * model.S_n[j])
                obj_function = obj_function - (costs_df['INNER_COST'][j] * model.Q_n[j])
        for j in range(0, n_communities ** 2):
            obj_function = obj_function + (imp_cost[0, j] * model.Qimp_c[j])
            obj_function = obj_function + (exp_cost[0, j] * model.Qexp_c[j])

        return obj_function

    # model.OBJ = Objective(rule=objective_rule) # minimization - default
    # model.OBJ = Objective(rule=objective_rule_linear, sense=maximize)  # maximization
    model.OBJ = Objective(rule=objective_rule_quadratic, sense=maximize)  # maximization

    ### Optimization Constraints
    ## 1 - Equality constraints
    model.Equality_Cons = ConstraintList()

    ## 1.1 - Adding the balace equation for each agent
    inner_community_balance = []
    for j in range(0, n_agents):
        if battery_size==0:
            inner_community_balance.append(model.Equality_Cons.add(
                model.P_n[j] + model.Q_n[j] - model.Alpha_n[j] + model.Beta_n[j] == 0))
            # model.Equality_Cons.add(model.Q_n[j] == model.Qn_pos[j] + model.Qn_neg[j])
            if agents_df['TYPE'][j] == 'CONSUMER':  # consumer
                model.Equality_Cons.add(model.Beta_n[j] == 0)
            if agents_df['TYPE'][j] == 'PRODUCER':  # producer
                model.Equality_Cons.add(model.Alpha_n[j] == 0)
            if agents_df['TYPE'][j] == 'EXT_CONSUMER':  # external grid consumer
                model.Equality_Cons.add(model.Q_n[j] == 0)
                model.Equality_Cons.add(model.Beta_n[j] == 0)
            if agents_df['TYPE'][j] == 'EXT_PRODUCER':  # external grid producer
                # model.Equality_Cons.add(model.Q_n[j] == 0)
                model.Equality_Cons.add(model.Alpha_n[j] == 0)
        if battery_size!=0:
            inner_community_balance.append(model.Equality_Cons.add(
                model.P_n[j] + model.Q_n[j] - model.Alpha_n[j] + model.Beta_n[j] + model.S_n[j] == 0))
            # model.Equality_Cons.add(model.Q_n[j] == model.Qn_pos[j] + model.Qn_neg[j])
            if agents_df['TYPE'][j] == 'CONSUMER':  # consumer
                model.Equality_Cons.add(model.S_n[j] == 0)
                model.Equality_Cons.add(model.Soc_n[j] == 0)
                model.Equality_Cons.add(model.Beta_n[j] == 0)
            if agents_df['TYPE'][j] == 'PRODUCER':  # producer
                model.Equality_Cons.add(model.S_n[j] == 0)
                model.Equality_Cons.add(model.Soc_n[j] == 0)
                model.Equality_Cons.add(model.Alpha_n[j] == 0)
            if agents_df['TYPE'][j] == 'BATTERY':  # community battery
                model.Equality_Cons.add(model.P_n[j] == 0)
                model.Equality_Cons.add(model.Alpha_n[j] == 0)
                model.Equality_Cons.add(model.Beta_n[j] == 0)
            if agents_df['TYPE'][j] == 'EXT_CONSUMER':  # external grid consumer
                model.Equality_Cons.add(model.Q_n[j] == 0)
                model.Equality_Cons.add(model.S_n[j] == 0)
                model.Equality_Cons.add(model.Soc_n[j] == 0)
                model.Equality_Cons.add(model.Beta_n[j] == 0)
            if agents_df['TYPE'][j] == 'EXT_PRODUCER':  # external grid producer
                # model.Equality_Cons.add(model.Q_n[j] == 0)
                model.Equality_Cons.add(model.S_n[j] == 0)
                model.Equality_Cons.add(model.Soc_n[j] == 0)
                model.Equality_Cons.add(model.Alpha_n[j] == 0)

    community_connex_var = np.reshape(community_range_set, (n_communities, n_communities))
    for j in range(1, n_communities + 1):
        ## Determines the sum of Qs, Alphas and Betas for each community
        idx = np.where(agents_df['COMMUNITY_LOCATION'] == j)
        Sigma_Q_n = 0
        Sigma_Qimp_c = 0
        Sigma_Qexp_c = 0
        Sigma_Beta_n = 0
        Sigma_Alpha_n = 0
        for i in range(0, len(idx[0])):
            Sigma_Q_n = Sigma_Q_n + model.Q_n[idx[0][i]]
            Sigma_Alpha_n = Sigma_Alpha_n + model.Alpha_n[idx[0][i]]
            Sigma_Beta_n = Sigma_Beta_n + model.Beta_n[idx[0][i]]
        for i in range(0, n_communities):
            Sigma_Qimp_c = Sigma_Qimp_c + model.Qimp_c[community_connex_var[j - 1, i]]  # * mat_bilateral[j-1,i]
            Sigma_Qexp_c = Sigma_Qexp_c + model.Qexp_c[community_connex_var[j - 1, i]]  # * mat_bilateral[j-1,i]
        ## 1.2 - Adding equality constraints for each community
        model.Equality_Cons.add(Sigma_Q_n == 0)
        model.Equality_Cons.add(Sigma_Alpha_n == Sigma_Qimp_c)
        model.Equality_Cons.add(Sigma_Beta_n == Sigma_Qexp_c)

    outer_community_balance = []
    for j in range(0, n_communities):
        for i in range(0, n_communities):
            outer_community_balance.append(model.Equality_Cons.add(
                model.Qimp_c[community_connex_var[j, i]] == model.Qexp_c[community_connex_var[i, j]]))
            if i==j:
                model.Equality_Cons.add(model.Qimp_c[community_connex_var[j, i]] == 0)
    ## 1.3 - Adding state of charge equality constraints
    if battery_size!=0:
        if (day == 0 and hour == 0):  ### DEFINES THE STARTING STATE OF CHARGE AS 0.5
            idx = np.where(agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
            j = 0
            for i in range(0, n_agents):
                if (i == idx[0][:]).any():
                    model.Equality_Cons.add(model.Soc_n[i] == 0.5 * (1 - bat_autodischargerate[j]) + model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                    j = j + 1
        elif (day == n_days - 1 and hour == n_hours - 1):  ### DEFINES THE FINAL STATE OF CHARGE AS 0.5
            idx = np.where(agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
            j = 0
            for i in range(0, n_agents):
                if (i == idx[0][:]).any():
                    # model.Equality_Cons.add(model.Soc_n[i] == 0.5)  # agents with batteries start and end simulations at 50%
                    model.Equality_Cons.add(model.Soc_n[i] == agents_results[i][day][hour - 1]['Soc'] * (1 - bat_autodischargerate[j]) +
                                            model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                    j = j + 1
        elif (day != 0 and hour == 0):  ### DEFINES THE STATE OF CHARGE EQUATION FOR CHANGING DAYS
            idx = np.where(agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
            j = 0
            for i in range(0, n_agents):
                if (i == idx[0][:]).any():
                    model.Equality_Cons.add(model.Soc_n[i] == agents_results[i][day - 1][n_hours - 1]['Soc'] * (1 - bat_autodischargerate[j]) +
                                            model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                    j = j + 1
        else:  ### DEFINES THE STATE OF CHARGE EQUATION THROUGHOUT DAYS
            idx = np.where(agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
            j = 0
            for i in range(0, n_agents):
                if (i == idx[0][:]).any():
                    model.Equality_Cons.add(model.Soc_n[i] == agents_results[i][day][hour - 1]['Soc'] * (1 - bat_autodischargerate[j]) +
                                            model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                    j = j + 1

    ## 1.4 - Quality of Service equality constraint
    # for j in range(1, n_communities):
    #     idx = np.where(agents_df['COMMUNITY_LOCATION'] == j)
    #     Sigma_Abs_Qn = 0
    #     Sigma_Pow_Qn = 0
    #     for i in range(0, len(idx[0])):
    #         Sigma_Abs_Qn = Sigma_Abs_Qn + (model.Qn_pos[idx[0][i]] - model.Qn_neg[idx[0][i]])
    #         Sigma_Pow_Qn = Sigma_Pow_Qn + (model.Q_n[idx[0][i]]) ** 2
    #     model.Equality_Cons.add(model.QoS[j - 1] == ((Sigma_Abs_Qn) ** 2) / (len(idx[0]) * (Sigma_Pow_Qn + 1e-6)))

    ## 2 - Inequality constraints
    model.Inequality_Cons = ConstraintList()

    ## 2.1 - Battery constraints: rate of charge and discharge
    if battery_size!=0:
        idx = np.where(agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
        for i in range(0, len(idx[0])):
            model.Inequality_Cons.add(model.S_n[idx[0][i]] <= bat_capacity[i] * bat_chargerate[i])  # charging rate constraints of each battery
            model.Inequality_Cons.add(model.S_n[idx[0][i]] >= - bat_capacity[i] * bat_dischargerate[i])  # discharging rate constraints of each battery
        ## 2.2 - Battery constraints: amount of charge and discharge
        idx = np.where(agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
        for i in range(0, len(idx[0])):
            model.Inequality_Cons.add(model.S_n[idx[0][i]] * bat_chargeeff[i] <= bat_capacity[i] *
                                      (bat_socmax[i] - model.Soc_n[idx[0][i]]))  # charging amount constraints of each battery
            model.Inequality_Cons.add(model.S_n[idx[0][i]] * bat_dischargeeff[i] >= - bat_capacity[i] *
                                      (model.Soc_n[idx[0][i]] - bat_socmin[i]))  # discharging amount constraints of each battery

    ## 2.3 - Upper and lower boundaries constraints
    for i in range(0, n_agents):
        if agents_df['TYPE'][i] == 'CONSUMER':  ## consumer
            model.Inequality_Cons.add(model.P_n[i] <= 1.3*agents_df['BASE_KW'][i]*profiles_dict[agents_df['PROFILE'][i]][0][hour])  # upper boundary constraint
            model.Inequality_Cons.add(model.P_n[i] >= 0.7*agents_df['BASE_KW'][i]*profiles_dict[agents_df['PROFILE'][i]][0][hour])  # lower boundary constraint
            model.Inequality_Cons.add(model.Q_n[i] <= 0)
        if agents_df['TYPE'][i] == 'PRODUCER':  ## producer
            model.Inequality_Cons.add(model.P_n[i] <= -0.7*agents_df['BASE_KW'][i]*profiles_dict[agents_df['PROFILE'][i]][0][hour])  # upper boundary constraint
            model.Inequality_Cons.add(model.P_n[i] >= -1.3*agents_df['BASE_KW'][i]*profiles_dict[agents_df['PROFILE'][i]][0][hour])  # lower boundary constraint
            model.Inequality_Cons.add(model.Q_n[i] >= 0)
        # if agents_df['TYPE'][i]=='BATTERY':
        #     model.Inequality_Cons.add(model.P_n[i] <= 0)  # upper boundary constraint
        #     model.Inequality_Cons.add(model.P_n[i] >= 0)  # lower boundary constraint
        if agents_df['TYPE'][i]=='EXT_CONSUMER':
            model.Inequality_Cons.add(model.P_n[i] <= agents_df['BASE_KW'][i])  # upper boundary constraint
            model.Inequality_Cons.add(model.P_n[i] >= 0)  # lower boundary constraint
            model.Inequality_Cons.add(model.Q_n[i] <= 0)
        if agents_df['TYPE'][i]=='EXT_PRODUCER':
            model.Inequality_Cons.add(model.P_n[i] <= 0)  # upper boundary constraint
            model.Inequality_Cons.add(model.P_n[i] >= -agents_df['BASE_KW'][i])  # lower boundary constraint
            model.Inequality_Cons.add(model.Q_n[i] >= 0)
    ## 2.4 - QoS lower boundaries constraints
    # for j in range(0,n_communities-1):
    #     model.Equality_Cons.add(model.QoS[j] == qos_bound)

    model.dual = Suffix(direction=Suffix.IMPORT)
    # opt = SolverFactory('glpk')   # linear optimization
    opt = SolverFactory('ipopt')  # nonlinear optimization
    results = opt.solve(model, tee=False)
    print('Day:', day, 'Hour:', hour, '\n Solver Status:', results.solver.status, '\n Termination Condition:', results.solver.termination_condition)

    return model, results, inner_community_balance, outer_community_balance

# XXX - FUNCTION FOR OPTIMIZATION RESULTS REPORT
def opt_report(model, results, inner_community_balance, outer_community_balance):
    if (results.solver.status == SolverStatus.ok) and (
            results.solver.termination_condition == TerminationCondition.optimal):
        outer_market_clearing = 0
        inner_market_clearing = [0] * n_communities
        qos = [0] * (n_communities - 1)
        for i in range(0, len(outer_community_balance)):
            if model.dual[outer_community_balance[i]] >= outer_market_clearing:
                outer_market_clearing = model.dual[outer_community_balance[i]]
        for i in range(0, len(inner_community_balance)):
            if model.dual[inner_community_balance[i]] >= inner_market_clearing[int(agents_df['COMMUNITY_LOCATION'][i]) - 1]:
                inner_market_clearing[int(agents_df['COMMUNITY_LOCATION'][i]) - 1] = model.dual[inner_community_balance[i]]
        for i in range(0, len(qos)):
            qos[i] = model.QoS[i].value
        optimization_results[day][hour] = {
            'Objective': value(model.OBJ),
            'Outer Market Clearing': outer_market_clearing,
            'Inner Markets Clearing': inner_market_clearing,
            'QoS': qos
        }
        Qexp = []
        Qimp = []
        community_range_set = []
        for i in range(0, n_communities ** 2):
            community_range_set.append(i)
        for i in range(0, len(community_range_set)):
            Qexp.append(model.Qexp_c[i].value)
            Qimp.append(model.Qimp_c[i].value)
        Qexp = np.reshape(Qexp,(n_communities, n_communities))  ## separates the communities export trade results in a matrix
        Qimp = np.reshape(Qimp,(n_communities, n_communities))  ## separates the communities import trade results in a matrix
        total_Qexp = []
        total_Qimp = []
        for i in range(0, n_communities):  ## separates the total community trade results in a list
            total_Qexp.append(sum(Qexp[i][:]))
            total_Qimp.append(sum(Qimp[i][:]))
        if battery_size==0:
            for agent in range(0, n_agents):  ## saves agent optimization results in dictionary
                agents_results[agent][day][hour] = {
                    'P': model.P_n[agent].value,
                    'Q': model.Q_n[agent].value,
                    'Alpha': model.Alpha_n[agent].value,
                    'Beta': model.Beta_n[agent].value
                }
        if battery_size!=0:
            for agent in range(0, n_agents):  ## saves agent optimization results in dictionary
                agents_results[agent][day][hour] = {
                    'P': model.P_n[agent].value,
                    'Q': model.Q_n[agent].value,
                    'Alpha': model.Alpha_n[agent].value,
                    'Beta': model.Beta_n[agent].value,
                    'S': model.S_n[agent].value,
                    'Soc': model.Soc_n[agent].value
                }
        for community in range(1, n_communities + 1):  ## saves communities optimization results in dictionary
            communities_results[community][day][hour] = {
                'Qexp': total_Qexp[community - 1],
                'Qimp': total_Qimp[community - 1]
            }
    elif (results.solver.termination_condition == TerminationCondition.infeasible):
        optimization_results[day][hour] = {
            'Objective': 'nan',
            'Outer Market Clearing': 'nan',
            'Inner Markets Clearing': 'nan',
            'QoS': 'nan'
        }
        for agent in range(0, n_agents):  ## saves agent optimization results in dictionary
            agents_results[agent][day][hour] = {
                'P': 'nan',
                'Q': 'nan',
                'Alpha': 'nan',
                'Beta': 'nan'
            }
        for community in range(1, n_communities + 1):  ## saves communities optimization results in dictionary
            communities_results[community][day][hour] = {
                'Qexp': 'nan',
                'Qimp': 'nan'
            }

    # opt_results, agt_results, com_results = [], [], []
    # if day==0 and hour==16:
    opt_results = {
        'Social_Welfare': abs(optimization_results[day][hour]['Objective']),
        'QoS_1': optimization_results[day][hour]['QoS'][0],
        # 'QoS_2': optimization_results[day][hour]['QoS'][1],
        # 'QoS_3': optimization_results[day][hour]['QoS'][2],
        'Mkt_Clearing_Com1': optimization_results[day][hour]['Inner Markets Clearing'][0],
        # 'Mkt_Clearing_Com2': optimization_results[day][hour]['Inner Markets Clearing'][1],
        # 'Mkt_Clearing_Com3': optimization_results[day][hour]['Inner Markets Clearing'][2],
        'Outer_Mkt_Clearing': optimization_results[day][hour]['Outer Market Clearing']
    }
    opt_results = pd.DataFrame(data=opt_results, index=[0],
                               columns=['Social_Welfare', 'QoS_1', 'QoS_2', 'QoS_3', 'Mkt_Clearing_Com1',
                                        'Mkt_Clearing_Com2', 'Mkt_Clearing_Com3', 'Outer_Mkt_Clearing'])

    Agent, P_n, Q_n, Alpha_n, Beta_n, S_n, Soc_n = ([] for i in range(7))
    if battery_size==0:
        for agent in range(0, n_agents):
            Agent.append(agent)
            P_n.append(agents_results[agent][day][hour]['P'])
            Q_n.append(agents_results[agent][day][hour]['Q'])
            Alpha_n.append(agents_results[agent][day][hour]['Alpha'])
            Beta_n.append(agents_results[agent][day][hour]['Beta'])
    
        agt_results = pd.DataFrame(list(zip(Agent, P_n, Q_n, Alpha_n, Beta_n)),
                                    columns=['Agent', 'P_n', 'Q_n', 'Alpha_n', 'Beta_n'])
    if battery_size!=0:
        for agent in range(0, n_agents):
            Agent.append(agent)
            P_n.append(agents_results[agent][day][hour]['P'])
            Q_n.append(agents_results[agent][day][hour]['Q'])
            Alpha_n.append(agents_results[agent][day][hour]['Alpha'])
            Beta_n.append(agents_results[agent][day][hour]['Beta'])
            S_n.append(agents_results[agent][day][hour]['S'])
            Soc_n.append(agents_results[agent][day][hour]['Soc'])
    
        agt_results = pd.DataFrame(list(zip(Agent, P_n, Q_n, Alpha_n, Beta_n, S_n, Soc_n)),
                                   columns=['Agent', 'P_n', 'Q_n', 'Alpha_n', 'Beta_n', 'S_n', 'Soc_n'])
    
    com, qexp, qimp = ([] for i in range(3))
    for community in range(1, n_communities + 1):  ## saves communities optimization results in dictionary
        com.append(community)
        qexp.append(communities_results[community][day][hour]['Qexp'])
        qimp.append(communities_results[community][day][hour]['Qimp'])

    com_results = pd.DataFrame(list(zip(com, qexp, qimp)),
                               columns=['Community', 'Qexp', 'Qimp'])

    return opt_results, agt_results, com_results

# XXX - FUNCTION FOR OPEN DSS POWER FLOW
def opendss_powerflow():
    dss = pydss.DSSDLL()

    # ...::: IMPORTING NETWORK DATA :::...
    if battery_size==0:
        dss_file = r"data/MASTER_hourly_no_storage.dss"
    if battery_size!=0:
        dss_file = r"data/MASTER_hourly.dss"
        
    dss.text("compile {}".format(dss_file))
    
    if day==0 and hour == 0:
        for battery in bat_name:
            name = "Storage.%s" % battery
            dss.circuit_set_active_element(name)
            # dss.cktelement_all_property_names()
            # property_index = str(dss.cktelement_all_property_names().index("%stored") + 1)
            # dss.dssproperties_read_value(str(dss.cktelement_all_property_names().index("%stored") + 1))
            dss.text(f"edit {name} %stored=50")
    
    dss.solution_write_hour(hour)
    if battery_size==0:
        dss.text("set casename=case0%s_day%shour%s_no_storage" % (case,day,hour))
    if battery_size!=0:
        dss.text("set casename=case0%s_day%shour%s_with_storage%s" % (case,day,hour,battery_size))
    
    # ...::: SETTINGS FOR VOLTAGE AND OVERLOAD VIOLATIONS REPORTS - OBS => needs CloseDI after SOLVE:::...
    # dss.text("set DemandInterval=true") 
    # dss.text("set overloadreport=true")
    # dss.text("set voltexceptionreport=true")
    # dss.text("set DIVerbose=true")
    
    # ...::: POWER FLOW :::...
    # Solving Power Flow
    dss.solution_solve()
    # Closing Violation Reports
    # dss.text("CloseDI")
    
    # ...::: POWER FLOW REPORTS :::...
    
    # 1 - Community Buses Voltages
    for bus in community_buses:
        idx = np.where(lvbus_names == bus)
        dss.circuit_set_active_bus(bus)
        dss.circuit_all_bus_vmag_pu()
        if dss.bus_num_nodes()==1:
            vmag = dss.bus_vmag_angle()        
            community_bus_results[bus][day][hour] = {
                'Vmag': vmag
            }
        if dss.bus_num_nodes()==2:
            vmag = dss.bus_vmag_angle()
            vmag_min = min(vmag[0],vmag[2])
            vmag_max = max(vmag[0],vmag[2])
            if vmag_min < 0.95*lvbus_basekv[idx[0][0]]*1000:
                community_bus_results[bus][day][hour] = {
                    'Vmag': vmag_min
                }
            else:
                community_bus_results[bus][day][hour] = {
                    'Vmag': vmag_max
                }
        if dss.bus_num_nodes()==3:
            vmag = dss.bus_vmag_angle()
            vmag_min = min(vmag[0],vmag[2],vmag[4])
            vmag_max = max(vmag[0],vmag[2],vmag[4])
            if vmag_min < 0.95*lvbus_basekv[idx[0][0]]*1000:
                community_bus_results[bus][day][hour] = {
                    'Vmag': vmag_min
                }
            else:
                community_bus_results[bus][day][hour] = {
                    'Vmag': ('%s_3PH' % vmag_max)
                }
    
    for line in community_lines:
        dss.circuit_set_active_element("Line.%s" % line)
        current_mag = dss.cktelement_currents_mag_ang()
        current_base = float(dss.lines_read_norm_amps())
        line_phases = dss.lines_read_phases()
        if line_phases==1:
            current_mag = max(current_mag[0],current_mag[2])
        if line_phases==2:
            current_mag = max(current_mag[0],current_mag[2],
                              current_mag[4],current_mag[6])
        if line_phases==3:
            current_mag = max(current_mag[0],current_mag[2],
                              current_mag[4],current_mag[6],
                              current_mag[8],current_mag[10])
        community_lines_results[line][day][hour] = {
            'Imag': current_mag,
            'Imag_pu': current_mag/current_base
        }
        
    # dss.text("show voltages LN node")

    # dss.text("show Meters")
    # dss.text("export Meters")
    return

# XXX - FUNCTION FOR PANDAPOWER PLOT OF NETWORK
def pandapower_plot():
    # CREATING PANDAPOWER ELEMENTS AND COLLECTIONS
    net = pp.create_empty_network() # pandapower network creation
    hvbus_collection_list = []           # high voltage buses collection
    mvbus_collection_list = []           # medium voltage buses collection
    lvbus_collection_list = []           # low voltage buses collection
    mvlines_collection_list = []         # medium voltage lines collection
    lvlines_collection_list = []         # low voltage lines collection
    trafo_collection_list = []           # transformers collection
    load_collection_list = []            # loads collection
    gen_collection_list = []             # generators collection
    prosumer_collection_list = []        # prosumers collection

    for i in range(0,len(hvbus_data)): # creating high voltage buses
        pp.create_bus(net, vn_kv=hvbus_basekv[i], name=hvbus_names[i], geodata=hvbus_geodata[i])
        hvbus_index = pp.get_element_index(net, "bus", hvbus_names[i])
        hvbus_collection_list.append(hvbus_index)
    for i in range(0, len(mvbus_data)): # creating medium voltage buses
        pp.create_bus(net, vn_kv=mvbus_basekv[i], name=mvbus_names[i], geodata=mvbus_geodata[i])
        mvbus_index = pp.get_element_index(net, "bus", mvbus_names[i])
        mvbus_collection_list.append(mvbus_index)
    for i in range(0,len(lvbus_data)): # creating low voltage buses
        pp.create_bus(net, vn_kv=lvbus_basekv[i], name=lvbus_names[i], geodata=lvbus_geodata[i])
        lvbus_index = pp.get_element_index(net, "bus", lvbus_names[i])
        lvbus_collection_list.append(lvbus_index)
    for i in range(0,len(mvline_data)): # creating medium voltage lines
        from_bus = pp.get_element_index(net, "bus", mvline_from[i])
        to_bus = pp.get_element_index(net, "bus", mvline_to[i])
        pp.create_line(net, from_bus=from_bus, to_bus=to_bus, length_km=mvline_length[i]/1000, std_type='149-AL1/24-ST1A 10.0', name=mvline_names[i])
        mvlines_index = pp.get_element_index(net, "line", mvline_names[i])
        mvlines_collection_list.append(mvlines_index)
    for i in range(0,len(lvline_data)): # creating low voltage lines
        from_bus = pp.get_element_index(net, "bus", lvline_from[i])
        to_bus = pp.get_element_index(net, "bus", lvline_to[i])
        pp.create_line(net, from_bus=from_bus, to_bus=to_bus, length_km=lvline_length[i]/1000, std_type='149-AL1/24-ST1A 10.0', name=lvline_names[i])
        lvlines_index = pp.get_element_index(net, "line", lvline_names[i])
        lvlines_collection_list.append(lvlines_index)
    for i in range(0,len(trafo3w_data)): # creating substation - 3w transformer
        hv_bus = pp.get_element_index(net, "bus", trafo3w_hvbus[i])
        mv_bus = pp.get_element_index(net, "bus", trafo3w_mvbus[i])
        lv_bus = pp.get_element_index(net, "bus", trafo3w_lvbus[i])
        pp.create_transformer3w_from_parameters(net, hv_bus=hv_bus, mv_bus=mv_bus, lv_bus=lv_bus,
                                                vn_hv_kv=trafo3w_hvbasekv[i], vn_mv_kv=trafo3w_mvbasekv[i], vn_lv_kv=trafo3w_lvbasekv[i],
                                                sn_hv_mva=trafo3w_hvbasekva[i], sn_mv_mva=trafo3w_mvbasekva[i], sn_lv_mva=trafo3w_lvbasekva[i],
                                                vk_hv_percent=trafo3w_hvvsc[i], vk_mv_percent=trafo3w_hvvsc[i], vk_lv_percent=trafo3w_hvvsc[i],
                                                vkr_hv_percent=trafo3w_hvvscr[i], vkr_mv_percent=trafo3w_hvvscr[i], vkr_lv_percent=trafo3w_hvvscr[i],
                                                pfe_kw=0, i0_percent=0, name=trafo3w_names[i])
    for i in range(0,len(trafo_data)): # creating transformers
        hv_bus = pp.get_element_index(net, "bus", trafo_hvbus[i])
        lv_bus = pp.get_element_index(net, "bus", trafo_lvbus[i])
        pp.create_transformer_from_parameters(net, name=trafo_names[i], hv_bus=hv_bus, lv_bus=lv_bus,
                                              sn_mva=trafo_basekva[i], vn_hv_kv=trafo_hvbasekv[i], vn_lv_kv=trafo_lvbasekv[i],
                                              vkr_percent=trafo_vscr[i], vk_percent=trafo_vsc[i],
                                              pfe_kw=trafo_pfe[i], i0_percent=trafo_i0[i])
        trafo_index = pp.get_element_index(net, "trafo", trafo_names[i])
        trafo_collection_list.append(trafo_index)
    for i in range(0,len(load_data)): # creating loads
        load_loc_bus = pp.get_element_index(net, "bus", load_bus[i])
        pp.create_load(net, name=load_name[i], bus=load_loc_bus, p_mw=load_basekw[i]/1000)
        load_collection_list.append(load_loc_bus)
    for i in range(0,len(gen_data)): # creating loads
        gen_loc_bus = pp.get_element_index(net, "bus", gen_bus[i])
        pp.create_gen(net, name=gen_name[i], bus=gen_loc_bus, p_mw=gen_basekw[i]/1000)
        gen_collection_list.append(gen_loc_bus)
        if (gen_loc_bus in load_collection_list):
            prosumer_collection_list.append(gen_loc_bus)

    #  Creating External Grid
    sourcebus =  pp.get_element_index(net, "bus", 'SOURCEBUS')
    pp.create_ext_grid(net, bus=sourcebus, vm_pu=1.00, va_degree=0, name='External grid', in_service=True)

    # PANDAPOWER PLOTTING
    # Plotting Collections
    hvbus_collection = pp.plotting.create_bus_collection(net, buses=hvbus_collection_list, size=1.0, patch_type='rect', color='green')
    mvbus_collection = pp.plotting.create_bus_collection(net, buses=mvbus_collection_list, size=1.0, patch_type='poly3', color='red')
    lvbus_collection = pp.plotting.create_bus_collection(net, buses=lvbus_collection_list, size=1.0, patch_type='circle', color='blue')
    mvlines_collection = pp.plotting.create_line_collection(net, lines=mvlines_collection_list, use_bus_geodata=True, color='red')
    lvlines_collection = pp.plotting.create_line_collection(net, lines=lvlines_collection_list, use_bus_geodata=True, color='blue')
    # trafo_collection = pp.plotting.create_trafo_collection(net, trafos=trafo_collection_list, size=1.0, color='black')
    load_collection = pp.plotting.create_bus_collection(net, buses=load_collection_list, size=1.0, patch_type='poly3', color='cyan')
    gen_collection = pp.plotting.create_bus_collection(net, buses=gen_collection_list, size=1.0, patch_type='poly3', color='orange')
    prosumer_collection = pp.plotting.create_bus_collection(net, buses=prosumer_collection_list, size=1.0, patch_type='poly3', color='purple')

    collections = [hvbus_collection,mvbus_collection,lvbus_collection,mvlines_collection,lvlines_collection,load_collection,gen_collection,prosumer_collection]
    pp.plotting.draw_collections(collections=collections)
    # plt.savefig(r'data/dss_data/teste.svg')
    plt.show()

    # Plotting Network
    # simple_plot(net, respect_switches=False, line_width=1.0, bus_size=0.01, ext_grid_size=0.05, trafo_size=0.05,
    #             plot_loads=True, plot_sgens=True, load_size=0.05, sgen_size=0.05, scale_size=True,
    #             bus_color='b', line_color='grey', trafo_color='k', ext_grid_color='y')

    return


n_days = 1
n_hours = 24
n_agents = len(load_data) + len(gen_data) + 2 # two extra agents representing external_grid
if battery_size!=0:
    n_agents = len(load_data) + len(gen_data) + len(bat_data) + 2 #  one battery per community and two extra agents representing external_grid
n_communities = max(max(load_community),max(gen_community)) + 1 #  agent communities plus external grid community

optimization_results = {day: {hour: {} for hour in range(n_hours)} for day in range(n_days)} ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP
agents_results = {agent: {day: {hour: {} for hour in range(n_hours)} for day in range(n_days)} for agent in range(n_agents)} ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP
communities_results = {community: {day: {hour: {} for hour in range(n_hours)} for day in range(n_days)} for community in range(1,n_communities+1)} ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP

profiles_dict = profile_curves()
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
num_community_buses =  len(community_buses)
# num_all_lines = len(lvline_data) + len(mvline_data)
num_community_lines =  len(community_lines)

# all_bus_results = {bus: {day: {hour: {} for hour in range(n_hours)} for day in range(n_days)} for bus in range(num_all_buses)} ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP}
community_bus_results = {bus: {day: {hour: {} for hour in range(n_hours)} for day in range(n_days)} for bus in community_buses} ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP}
# community_bus_results = {bus: {day: {hour: {} for hour in range(n_hours)} for day in range(n_days)} for bus in range(num_community_buses)} ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP}
# all_lines_results = {line: {day: {hour: {} for hour in range(n_hours)} for day in range(n_days)} for line in range(num_all_lines)} ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP}
community_lines_results = {line: {day: {hour: {} for hour in range(n_hours)} for day in range(n_days)} for line in community_lines} ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP}

# Day-ahead market analysis considering case study players
for day in range(0,n_days):
    # day = 0
    # ...::: Market evaluation for each hour of the day ahead market :::...
    for hour in range(0,n_hours):
        # hour = 0
        costs_df = costs_info(agents_df)
        [model,results,inner_community_balance,outer_community_balance] = pyomo_opt(agents_df,costs_df,profiles_dict)
        [opt_results,agt_results,com_results] = opt_report(model,results,inner_community_balance,outer_community_balance)
        profiles_dict = profile_curves_update(hour, agt_results)
        # opendss_powerflow()
        # pandapower_plot()
        # if hour==0:
        #     sys.exit()


### Saving Results Dictionaries
# np.save(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_optimization_results.npy', optimization_results)
# np.save(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_agents_results.npy', agents_results)
# np.save(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_communities_results.npy', communities_results)
# np.save(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_community_bus_results.npy', community_bus_results)
# np.save(r'C:\Users\ppeters\Documents\Mestrado\OpenDSS_CostaRica_data\dict_community_lines_results.npy', community_lines_results)