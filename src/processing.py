import pandas as pd
import glob
from tqdm import tqdm
class DataAquisition:
    def __init__(self, args, path):
        self.args = args
        self.path = path
        self.data = {}
    def findData(self):
        files = glob.glob(f'{self.path}/*.csv')
        for file in tqdm(files, total=len(files)):
            name = file.split('\\')[-1].replace('.csv', '')
            param = pd.read_csv(file, delimiter=',')
            self.data[name] = param

    def createParams(self):
        self.len_load = self.data[f"LoadsList_Caso0{self.args.case}"].shape[0]
        self.len_gen = self.data[f"PvList_Caso0{self.args.case}"].shape[0]
        self.len_bat = self.data[f"BatteryList_Caso0{self.args.case}"].shape[0]
        self.load_community = max(self.data[f"LoadsList_Caso0{self.args.case}"]['COMMUNITY'])
        self.gen_community = max(self.data[f"PvList_Caso0{self.args.case}"]['COMMUNITY'])

        if self.args.battery_size != 0:
            self.args.n_agents = self.len_load + self.len_gen + self.len_bat + 2
        else:
            self.args.n_agents = self.len_load + self.len_gen + 2

        self.args.n_communities = max(self.load_community, self.gen_community) + 1

    def createDefaultDf(self):
        agent_number = list(range(self.args.n_agents))
        agent_name = list(self.data[f"LoadsList_Caso0{self.args.case}"]['NAME']) + list(self.data[f"PvList_Caso0{self.args.case}"]['NAME'])
        agent_type = (['CONSUMER'] * self.len_load) + (['PRODUCER'] * self.len_gen)
        agent_bus = list(self.data[f"LoadsList_Caso0{self.args.case}"]['BUS']) + list(self.data[f"PvList_Caso0{self.args.case}"]['BUS'])
        agent_basekw = list(self.data[f"LoadsList_Caso0{self.args.case}"]['BASE_KW']) + list(
            self.data[f"PvList_Caso0{self.args.case}"]['BASE_KW'])
        community_location = list(self.data[f"LoadsList_Caso0{self.args.case}"]['COMMUNITY']) + list(
            self.data[f"PvList_Caso0{self.args.case}"]['COMMUNITY'])
        agent_profile = list(self.data[f"LoadsList_Caso0{self.args.case}"]['LOADSHAPE']) + list(
            self.data[f"PvList_Caso0{self.args.case}"]['GEN_SHAPE'])

        if self.args.battery_size != 0:
            agent_name += list(self.data[f"BatteryList_Caso0{self.args.case}"]['NAME'])
            agent_type += ['BATTERY'] * self.len_bat
            agent_bus += list(self.data[f"BatteryList_Caso0{self.args.case}"]['BUS'])
            agent_basekw += list(self.data[f"BatteryList_Caso0{self.args.case}"]['BASE_KW'])
            community_location += list(self.data[f"BatteryList_Caso0{self.args.case}"]['COMMUNITY'])
            agent_profile += list(self.data[f"BatteryList_Caso0{self.args.case}"]['LOADSHAPE'])

        agent_name += ['EXTERNAL_GRID'] * 2
        agent_type.append('EXT_CONSUMER')
        agent_type.append('EXT_PRODUCER')
        agent_bus += ['SOURCEBUS'] * 2
        agent_basekw += [999999] * 2
        community_location += [self.args.n_communities] * 2
        agent_profile += [''] * 2

        self.agents_df = pd.DataFrame({
            'AGENT': agent_number, 'NAME': agent_name, 'TYPE': agent_type, 'BUS': agent_bus,
            'BASE_KW': agent_basekw,
            'COMMUNITY_LOCATION': community_location, 'PROFILE': agent_profile
        })

class PreProcessingData(DataAquisition):
    def __init__(self, args):
        super(PreProcessingData, self).__init__(args=args, path=args.path)
        self.findData()
        self.createParams()
        self.createDefaultDf()

        community_buses = list(self.agents_df.head(self.args.n_agents - 2)['BUS'].unique())
        community_lines = []
        for bus in community_buses:
            if bus in self.data['LinesListLV']['BUS_FROM'].values:
                idx = list(self.data['LinesListLV']['BUS_FROM'].values).index(bus)
                community_lines.append(self.data['LinesListLV']['NAME'].values[idx])

            if bus in self.data['LinesListLV']['BUS_TO'].values:
                idx = list(self.data['LinesListLV']['BUS_TO'].values).index(bus)
                community_lines.append(self.data['LinesListLV']['NAME'].values[idx])
        community_lines = list(dict.fromkeys(community_lines))
        print(community_lines)

class OptimizationData(DataAquisition):
    def __init__(self, args):
        super(OptimizationData, self).__init__(args=args, path=args.path)