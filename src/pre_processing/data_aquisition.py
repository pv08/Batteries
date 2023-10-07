import pandas as pd
import os
import glob
from tqdm import tqdm

class DataAquisition:
    def __init__(self, path):
        self.path = path
    def dssDataCatch(self):
        csv_files = glob.glob(f"{self.path}/*.csv")
        self.data = {}
        for file in tqdm(csv_files, total=len(csv_files)):
            name = file.split('\\')[-1].replace('.csv', '')
            self.data[name] = pd.read_csv(file, delimiter=',')

class DefaultGridData(DataAquisition):
    def __init__(self, args):
        super(DefaultGridData, self).__init__(path=args.data_path)
        self.args = args
        self.dssDataCatch()
        self.paramConstruction()
        self.preprocessAgent()

        self.community_buses = self.agent_df.head(self.args['n_agents'] - 2)['BUS'].unique()
        self.community_lines = []
        for i in range(0, self.args['n_agents'] - 2):
            bus = self.agent_df['BUS'][i]
            if bus in self.data['LinesListLV']['BUS_FROM'].values:
                idx = [i for i, j in enumerate(self.data['LinesListLV']['BUS_FROM']) if j == bus]
                for i in range(0, len(idx)):
                    self.community_lines.append(self.data['LinesListLV']['NAME'][idx[i]])
            if bus in self.data['LinesListLV']['BUS_TO']:
                idx = [i for i, j in enumerate(self.data['LinesListLV']['BUS_TO']) if j == bus]
                for i in range(0, len(idx)):
                    self.community_lines.append(self.data['LinesListLV']['NAME'][idx[i]])
            self.community_lines = list(set(self.community_lines))

        self.num_community_buses = len(self.community_buses)
        self.num_community_lines = len(self.community_lines)

    def paramConstruction(self):
        self.len_load = self.data[f'LoadsList_Caso0{self.args.case}'].shape[0]
        self.len_gen = self.data[f'PvList_Caso0{self.args.case}'].shape[0]
        self.len_bat = self.data[f'BatteryList_Caso0{self.args.case}'].shape[0]

        load_comm_list = self.data[f'LoadsList_Caso0{self.args.case}']['COMMUNITY']
        gen_comm_list = self.data[f'PvList_Caso0{self.args.case}']['COMMUNITY']
        self.args['n_communities'] = max(max(load_comm_list), max(gen_comm_list)) + 1  # agent communities plus external grid community

        if self.args.battery_size != 0:
            self.args['n_agents'] = self.len_load + self.len_gen + self.len_bat + 2  # one battery per community and two extra agents representing external_grid
        else:
            self.args['n_agents'] = self.len_load + self.len_gen + 2
    def preprocessAgent(self):
        agents_name = self.data[f'LoadsList_Caso0{self.args.case}']['NAME'] + self.data[f'PvList_Caso0{self.args.case}']['NAME']
        agents_type = ['CONSUMER'] * self.len_load
        agents_type += ['PRODUCER'] * self.len_gen

        agents_bus = self.data[f'LoadsList_Caso0{self.args.case}']['BUS'] + \
                        self.data[f'PvList_Caso0{self.args.case}']['BUS']

        agents_basekw = self.data[f'LoadsList_Caso0{self.args.case}']['BASE_KW'] + \
                        self.data[f'PvList_Caso0{self.args.case}']['BASE_KW']

        community_location = self.data[f'LoadsList_Caso0{self.args.case}']['COMMUNITY'] + \
                            self.data[f'PvList_Caso0{self.args.case}']['COMMUNITY']

        agent_profile = self.data[f'LoadsList_Caso0{self.args.case}']['LOADSHAPE'] + \
                            self.data[f'PvList_Caso0{self.args.case}']['LOADSHAPE']



        if self.args.battery_size != 0:
            agents_name += self.data[f'BatteryList_Caso0{self.args.case}']['NAME']
            agents_type += ['BATTERY'] * self.len_bat
            agents_bus += self.data[f'BatteryList_Caso0{self.args.case}']['BUS']
            agents_basekw += self.data[f'BatteryList_Caso0{self.args.case}']['BASE_KW']
            community_location += self.data[f'BatteryList_Caso0{self.args.case}']['COMMUNITY']
            agent_profile += self.data[f'BatteryList_Caso0{self.args.case}']['LOADSHAPE']

        agents_name += ['EXTERNAL_GRID'] * 2

        agents_type.append('EXT_CONSUMER')
        agents_type.append('EXT_PRODUCER')

        agents_bus += ['SOURCEBUS'] * 2

        agents_basekw += [999999] * 2

        community_location += [self.args['n_communities']] * 2
        agent_profile += [''] * 2

        self.agent_df = pd.DataFrame(
            {'AGENT': [range(self.args['n_agenst'])],
             'NAME': agents_name,
             'TYPE': agents_type,
             'BUS': agents_bus,
             'BASE_KW': agents_basekw,
             'COMMUNITY_LOCATION': community_location,
             'PROFILE': agent_profile}
        )
class DefaultOptData(DataAquisition):
    def __init__(self, args):
        super(DefaultOptData, self).__init__(path=args.data_path)
        pass