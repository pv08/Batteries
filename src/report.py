import numpy as np
import pandas as pd
from pyomo.environ import *
from pandas import DataFrame
class Report:
    def __init__(self, n_communities, agents_df, day, hour, battery_size, n_agents, agents_results, communities_results, optimization_results):
        self.n_communities = n_communities
        self.communities_results = communities_results
        self.optimization_results = optimization_results
        self.agents_results = agents_results
        self.n_agents = n_agents
        self.battery_size = battery_size
        self.day = day
        self.hour = hour
        self.agents_df = agents_df



    def set_report(self, model, results, inner_community_balance, outer_community_balance):
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            outer_market_clearing = 0
            inner_market_clearing = [0] * self.n_communities
            qos = [0] * (self.n_communities - 1)
            for i in range(0, len(outer_community_balance)):
                if model.dual[outer_community_balance[i]] >= outer_market_clearing:
                    outer_market_clearing = model.dual[outer_community_balance[i]]
            for i in range(0, len(inner_community_balance)):
                if model.dual[inner_community_balance[i]] >= inner_market_clearing[int(self.agents_df['COMMUNITY_LOCATION'][i]) - 1]:
                    inner_market_clearing[int(self.agents_df['COMMUNITY_LOCATION'][i]) - 1] = model.dual[inner_community_balance[i]]
            for i in range(0, len(qos)):
                qos[i] = model.QoS[i].value
            self.optimization_results[self.day][self.hour] = {
                'Objective': value(model.OBJ),
                'Outer Market Clearing': outer_market_clearing,
                'Inner Markets Clearing': inner_market_clearing,
                'QoS': qos
            }
            Qexp = []
            Qimp = []
            community_range_set = []
            for i in range(0, self.n_communities ** 2):
                community_range_set.append(i)
            for i in range(0, len(community_range_set)):
                Qexp.append(model.Qexp_c[i].value)
                Qimp.append(model.Qimp_c[i].value)
            Qexp = np.reshape(Qexp, (self.n_communities, self.n_communities))  ## separates the communities export trade results in a matrix
            Qimp = np.reshape(Qimp, (self.n_communities, self.n_communities))  ## separates the communities import trade results in a matrix
            total_Qexp = []
            total_Qimp = []
            for i in range(0, self.n_communities):  ## separates the total community trade results in a list
                total_Qexp.append(sum(Qexp[i][:]))
                total_Qimp.append(sum(Qimp[i][:]))
            if self.battery_size == 0:
                for agent in range(0, self.n_agents):  ## saves agent optimization results in dictionary
                    self.agents_results[agent][self.day][self.hour] = {
                        'P': model.P_n[agent].value,
                        'Q': model.Q_n[agent].value,
                        'Alpha': model.Alpha_n[agent].value,
                        'Beta': model.Beta_n[agent].value
                    }
            if self.battery_size != 0:
                for agent in range(0, self.n_agents):  ## saves agent optimization results in dictionary
                    self.agents_results[agent][self.day][self.hour] = {
                        'P': model.P_n[agent].value,
                        'Q': model.Q_n[agent].value,
                        'Alpha': model.Alpha_n[agent].value,
                        'Beta': model.Beta_n[agent].value,
                        'S': model.S_n[agent].value,
                        'Soc': model.Soc_n[agent].value
                    }
            for community in range(1, self.n_communities + 1):  ## saves communities optimization results in dictionary
                self.communities_results[community][self.day][self.hour] = {
                    'Qexp': total_Qexp[community - 1],
                    'Qimp': total_Qimp[community - 1]
                }
        elif (results.solver.termination_condition == TerminationCondition.infeasible):
            self.optimization_results[self.day][self.hour] = {
                'Objective': 'nan',
                'Outer Market Clearing': 'nan',
                'Inner Markets Clearing': 'nan',
                'QoS': 'nan'
            }
            for agent in range(0, self.n_agents):  ## saves agent optimization results in dictionary
                self.agents_results[agent][self.day][self.hour] = {
                    'P': 'nan',
                    'Q': 'nan',
                    'Alpha': 'nan',
                    'Beta': 'nan'
                }
            for community in range(1, self.n_communities + 1):  ## saves communities optimization results in dictionary
                self.communities_results[community][self.day][self.hour] = {
                    'Qexp': 'nan',
                    'Qimp': 'nan'
                }
        # self.opt_results, self.agt_results, self.com_results = [], [], []
        # if day==0 and hour==16:
        self.opt_results = {
            'Social_Welfare': abs(self.optimization_results[self.day][self.hour]['Objective']),
            'QoS_1': self.optimization_results[self.day][self.hour]['QoS'][0],
            # 'QoS_2': optimization_results[day][hour]['QoS'][1],
            # 'QoS_3': optimization_results[day][hour]['QoS'][2],
            'Mkt_Clearing_Com1': self.optimization_results[self.day][self.hour]['Inner Markets Clearing'][0],
            # 'Mkt_Clearing_Com2': optimization_results[day][hour]['Inner Markets Clearing'][1],
            # 'Mkt_Clearing_Com3': optimization_results[day][hour]['Inner Markets Clearing'][2],
            'Outer_Mkt_Clearing': self.optimization_results[self.day][self.hour]['Outer Market Clearing']
        }
        self.opt_results = pd.DataFrame(data=self.opt_results, index=[0],
                                   columns=['Social_Welfare', 'QoS_1', 'QoS_2', 'QoS_3', 'Mkt_Clearing_Com1',
                                            'Mkt_Clearing_Com2', 'Mkt_Clearing_Com3', 'Outer_Mkt_Clearing'])

        Agent, P_n, Q_n, Alpha_n, Beta_n, S_n, Soc_n = ([] for i in range(7))
        if self.battery_size == 0:
            for agent in range(0, self.n_agents):
                Agent.append(agent)
                P_n.append(self.agents_results[agent][self.day][self.hour]['P'])
                Q_n.append(self.agents_results[agent][self.day][self.hour]['Q'])
                Alpha_n.append(self.agents_results[agent][self.day][self.hour]['Alpha'])
                Beta_n.append(self.agents_results[agent][self.day][self.hour]['Beta'])

            self.agt_results = pd.DataFrame(list(zip(Agent, P_n, Q_n, Alpha_n, Beta_n)),
                                       columns=['Agent', 'P_n', 'Q_n', 'Alpha_n', 'Beta_n'])
        if self.battery_size != 0:
            for agent in range(0, self.n_agents):
                Agent.append(agent)
                P_n.append(self.agents_results[agent][self.day][self.hour]['P'])
                Q_n.append(self.agents_results[agent][self.day][self.hour]['Q'])
                Alpha_n.append(self.agents_results[agent][self.day][self.hour]['Alpha'])
                Beta_n.append(self.agents_results[agent][self.day][self.hour]['Beta'])
                S_n.append(self.agents_results[agent][self.day][self.hour]['S'])
                Soc_n.append(self.agents_results[agent][self.day][self.hour]['Soc'])

            self.agt_results = pd.DataFrame(list(zip(Agent, P_n, Q_n, Alpha_n, Beta_n, S_n, Soc_n)),
                                       columns=['Agent', 'P_n', 'Q_n', 'Alpha_n', 'Beta_n', 'S_n', 'Soc_n'])

        com, qexp, qimp = ([] for i in range(3))
        for community in range(1, self.n_communities + 1):  ## saves communities optimization results in dictionary
            com.append(community)
            qexp.append(self.communities_results[community][self.day][self.hour]['Qexp'])
            qimp.append(self.communities_results[community][self.day][self.hour]['Qimp'])

        self.com_results = pd.DataFrame(list(zip(com, qexp, qimp)),
                                   columns=['Community', 'Qexp', 'Qimp'])

        return self.opt_results, self.agt_results, self.com_results

