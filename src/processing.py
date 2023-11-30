import pandas as pd
import glob
from tqdm import tqdm
from src.utils.functions import find_file_extention
class DataAquisition:
    def __init__(self, args, path):
        self.args = args
        self.path = path
        self.data = {}
    def findData(self):
        files = find_file_extention(path=f'{self.path}/dss_data/', type='.csv')
        for file in tqdm(files, total=len(files)):
            name = file.split('//')[-1].replace('.csv', '')
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
        self.agents_data = [
            {'agent_id': id, 'name': name, 'type': type, 'bus': bus, 'kw_base': base, 'community_location': location, 'profile': profile}
            for id, name, type, bus, base, location, profile in zip(agent_number, agent_name, agent_type, agent_bus, agent_basekw, community_location, agent_profile)
        ]
        self.agents_df = pd.DataFrame(self.agents_data)

    def createProfiles(self):
        self.profiles = {}
        for profile in self.args.profiles:
            files = glob.glob(f'{self.path}/profiles_edited/{profile}/*.txt')
            for file in files:
                name = file.split('\\')[-1].replace('.txt', '')
                self.profiles[name] = list(pd.read_csv(file, header=None)[0].values)
        self.profiles['BatteryProfile'] = [-x for x in self.profiles['BatteryProfile']]

    def exportProfiles(self):
        def exportCSV(**kwargs):
            df = pd.DataFrame(kwargs['data'])
            df.to_csv(kwargs['path'], sep=',', index=False, header=False)

        print(f"[+] - Exporting profiles dictionary")
        for profile, data in tqdm(zip(self.profiles.keys(), self.profiles.values()), total=len(self.profiles.values())):
            if profile.endswith('R'):
                exportCSV(path=f'data/profiles_edited/residential/{profile}.csv', data=data)
            elif profile.endswith('I'):
                exportCSV(path=f'data/profiles_edited/industrial/{profile}.csv', data=data)
            elif profile.endswith('C'):
                exportCSV(path=f'data/profiles_edited/commercial/{profile}.csv', data=data)
            elif profile.startswith('PV'):
                exportCSV(path=f'data/profiles_edited/DG/{profile}.csv', data=data)
            elif profile.startswith('Battery'):
                exportCSV(path=f'data/profiles_edited/storage/{profile}.csv', data=data)
            else:
                raise Exception(f'[!] - Profile not found while trying to export. Verify your profile dictionary!')


    def updateProfiles(self, hour, agt_results):
        j = 0
        for i in range(0, self.args.n_agents):
            profile_name = self.agents_df['profile'][i]
            if profile_name != '':
                self.profiles[profile_name][hour] = abs(agt_results['P_n'][i]) / self.agents_df['kw_base'][i]
            if profile_name.startswith('Battery'):  # storage loadshapes
                # profiles_dict[profile_name][0][hour] = - agt_results['S_n'][i]/bat_capacity[j]
                self.profiles[profile_name][hour] = - agt_results['S_n'][i] / self.agents_df['kw_base'][i]
                j = j + 1
        self.exportProfiles()


    @staticmethod
    def consumerProducerInfo(data: pd.DataFrame, **kwargs):
        index_val = data[data['NAME'] == kwargs['name']].index.values
        a_doll_kw2 = data['A_[R$/KW^2]'][index_val[0]]
        b_doll_kw = data['B_[R$/KW]'][index_val[0]]
        cost_s = 0.0
        inner_cost = 0.001
        imp_cost = 0.0
        exp_cost = 0.0
        return a_doll_kw2, b_doll_kw, cost_s, inner_cost, imp_cost, exp_cost

    @staticmethod
    def batteryInfo(data: pd.DataFrame, **kwargs):
        a_doll_kw2 = 0.0
        b_doll_kw = 0.0
        cost_s = data['COST_S'][kwargs['hour']]
        inner_cost = 0.001
        imp_cost = 0.0
        exp_cost = 0.0
        return a_doll_kw2, b_doll_kw, cost_s, inner_cost, imp_cost, exp_cost
    @staticmethod
    def extConsumerInfo(data: pd.DataFrame, **kwargs):
        a_doll_kw2 = 0.0
        b_doll_kw = 0.0
        cost_s = 0.0
        inner_cost = 0.001
        imp_cost = 0.0
        exp_cost = data['EXPORT_PRICE(R$/MWh)'][kwargs['hour']]/1000
        return a_doll_kw2, b_doll_kw, cost_s, inner_cost, imp_cost, exp_cost

    @staticmethod
    def extConsumerInfo(data: pd.DataFrame, **kwargs):

        a_doll_kw2 = 0.0
        b_doll_kw = 0.0
        cost_s = 0.0
        inner_cost = 0.001
        imp_cost = 0.0
        exp_cost = data['EXPORT_PRICE(R$/MWh)'][kwargs['hour']]/1000
        return a_doll_kw2, b_doll_kw, cost_s, inner_cost, imp_cost, exp_cost

    @staticmethod
    def extProducerInfo(data: pd.DataFrame, **kwargs):
        a_doll_kw2 = 0.0
        b_doll_kw = 0.0
        cost_s = 0.0
        inner_cost = 0.001
        imp_cost = data['IMPORT_PRICE(R$/MWh)'][kwargs['hour']]/1000
        exp_cost = 0.0
        return a_doll_kw2, b_doll_kw, cost_s, inner_cost, imp_cost, exp_cost

    def costInfo(self, hour):
        costs_data = []
        fn_dict = {
            'CONSUMER': (self.consumerProducerInfo, self.data['LoadsList_Cost']),
            'PRODUCER': (self.consumerProducerInfo, self.data['PvList_Cost']),
            'BATTERY': self.batteryInfo(self.data['BatteryList_Cost'], hour=hour),
            'EXT_CONSUMER': self.extConsumerInfo(self.data['00_Market_price_hourly_brasil'], hour=hour),
            'EXT_PRODUCER': self.extProducerInfo(self.data['00_Market_price_hourly_brasil'], hour=hour),
        }
        for i, row in self.agents_df.iterrows():
            if type(fn_dict[row['type']]) is tuple and len(fn_dict[row['type']]) == 2:
                fn, data = fn_dict[row['type']]
                a_doll_kw2, b_doll_kw, cost_s, inner_cost, imp_cost, exp_cost = fn(data, name=row['name'])
            else:
                a_doll_kw2, b_doll_kw, cost_s, inner_cost, imp_cost, exp_cost = fn_dict[row['type']]
            costs_data.append({'AGENT': i, 'NAME': row['name'], 'TYPE': row['type'], 'A_[R$/KW^2]': a_doll_kw2,
                  'B_[R$/KW]': b_doll_kw, 'COST_S': cost_s, 'INNER_COST': inner_cost, 'IMP_COST': imp_cost, 'EXP_COST': exp_cost})
        self.cost_df = pd.DataFrame(costs_data, index=None)
        return self.cost_df
class PreProcessingData(DataAquisition):
    def __init__(self, args):
        super(PreProcessingData, self).__init__(args=args, path=args.path)
        self.findData()
        self.createParams()
        self.createDefaultDf()
        self.createProfiles()

        self.community_buses = list(self.agents_df.head(self.args.n_agents - 2)['bus'].unique())
        community_lines = []
        for bus in self.community_buses:
            if bus in self.data['LinesListLV']['BUS_FROM'].values:
                idx = list(self.data['LinesListLV']['BUS_FROM'].values).index(bus)
                community_lines.append(self.data['LinesListLV']['NAME'].values[idx])

            if bus in self.data['LinesListLV']['BUS_TO'].values:
                idx = list(self.data['LinesListLV']['BUS_TO'].values).index(bus)
                community_lines.append(self.data['LinesListLV']['NAME'].values[idx])
        self.community_lines = list(dict.fromkeys(community_lines))
        print(community_lines)

