from pyomo.environ import *
from src.processing import PreProcessingData
from src.report import Report
from src.utils.functions import *
from src.dss_config import DSSConfig
from src.powerflow import Powerflow

class Optmizer(PreProcessingData):
    def __init__(self, args, day, hour, optimization_results, agents_results, communities_results):
        super(Optmizer, self).__init__(args=args)
        self.model = ConcreteModel(args.model_name)
        self.hour = hour
        self.day = day
        #(day, hour[hour])
        self.optimization_results = optimization_results
        # (agent, day ,hour[hour])
        self.agents_results = agents_results
        # (comm, day ,hour[hour])
        self.communities_results = communities_results


        self.agent_range_set = range(self.args.n_agents)
        self.community_set = range(self.args.n_communities - 1)
        self.community_range_set = range(self.args.n_communities**2)


        self.model.P_n = Var(self.agent_range_set, domain=Reals, bounds=self.PBoundery)
        self.model.Q_n = Var(self.agent_range_set, domain=Reals, bounds=self.QBoundery)
        # model.Qn_pos = Var(agent_range_set, domain=NonNegativeReals)
        # model.Qn_neg = Var(agent_range_set, domain=NonPositiveReals)
        self.model.Alpha_n = Var(self.agent_range_set, domain=PositiveReals)
        self.model.Beta_n = Var(self.agent_range_set, domain=PositiveReals)
        self.model.Qimp_c = Var(self.community_range_set, domain=PositiveReals)
        self.model.Qexp_c = Var(self.community_range_set, domain=PositiveReals)
        self.model.QoS = Var(self.community_set, domain=(0, 1))
        if self.args.battery_size != 0:
            self.model.S_n = Var(self.agent_range_set, domain=Reals)
            self.model.Soc_n = Var(self.agent_range_set, domain=PositiveReals)

        self.inner_community_balance = []
        self.outer_community_balance = []

    def PBoundery(self, model, i):
        #consumer
        agent_data = self.agents_data[i]
        if agent_data['type'] == 'CONSUMER':
            return (0.7 * agent_data['kw_base'] * self.profiles[agent_data['profile']][self.hour], 1.3 * agent_data['kw_base'] * self.profiles[agent_data['profile']][self.hour])
        elif agent_data['type'] == 'PRODUCER':
            return (-1.3 * agent_data['kw_base'] * self.profiles[agent_data['profile']][self.hour],
                    -0.7 * agent_data['kw_base'] * self.profiles[agent_data['profile']][self.hour])
        elif agent_data['type'] == 'BATERRY':
            return (0, 0)
        elif agent_data['type'] == 'EXT_CONSUMER':
            return (0 , agent_data['kw_base'])
        elif agent_data['type'] == 'EXT_PRODUCER':
            return (-agent_data['kw_base'], 0)

    def QBoundery(self, model, i):
        agent_data = self.agents_data[i]
        if agent_data['type'] == 'CONSUMER':
            return (None,0)
        if agent_data['type'] == 'PRODUCER':
            return (0,None)
        elif agent_data['type'] == 'EXT_CONSUMER':

            return (None , 0)
        elif agent_data['type'] == 'EXT_PRODUCER':
            return (0, None)


    def obj_fn_quadratic(self, model):
        r"""
            A função cria a fob do problema. Para cada uum dos agentes, verifica se é consumidor, produtor ou se é bateria
            A FOB pode ser descrita como:
            ..math::
                \zeta = \sum^{N_{agents}}_{j\gets1}-\left(0.5AP_j+BP_j - C^{in}_jQ_j \right ) +\left( C^{s}_jS_j - C^{in}_jQ_j\right)
                +\sum^{N_{co}^2}_{j\gets1}\left(C^{imp}_{j}Q^{imp}_j - C^{exp}_jQ^{exp}_j \right ),

        Args:
            model (pyomo.ConcreteModel): modelo do Pyomo
        :return SumExpression
        """
        obj_function = 0
        for j, row in self.agents_df.iterrows():
            if row['type'] == 'CONSUMER' or row['type'] == 'PRODUCER':
                obj_function -= (0.5 * self.cost_df['A_[R$/KW^2]'][j] * model.P_n[j] * model.P_n[j] + self.cost_df['B_[R$/KW]'][j] * model.P_n[j])
                obj_function -= (self.cost_df['INNER_COST'][j] * model.Q_n[j])
            # elif row['type'] == 'PRODUCER':
            #     obj_function -= (0.5 * self.cost_df['A_[R$/KW^2]'][j] * model.P_n[j] * model.P_n[j] + self.cost_df['B_[R$/KW]'][j] * model.P_n[j])
            #     obj_function -= (self.cost_df['INNER_COST'][j] * model.Q_n[j])
            elif row['type'] == 'BATTERY':
                obj_function += (self.cost_df['COST_S'][j] * model.S_n[j])
                obj_function -= (self.cost_df['INNER_COST'][j] * model.Q_n[j])
            else:
                Exception(f"[!] {row['type']} type not found. Please, verify your agents data!")
        for j in range(0, self.args.n_communities ** 2):
            obj_function += (self.imp_cost[0, j] * model.Qimp_c[j])
            obj_function -= (self.exp_cost[0, j] * model.Qexp_c[j])

        return obj_function

    def defineInequalityCons(self, day, hour):
        self.model.Inequality_Cons = ConstraintList()
        bat_dict = self.data[f'BatteryList_Caso0{self.args.case}']
        bat_capacity = bat_dict['NOMINAL_CAPACITY_[KWH]']
        bat_autodischargerate = bat_dict['AUTODISCHARGE_RATE']
        bat_chargerate = bat_dict['CHARGE_RATE']
        bat_dischargerate = bat_dict['DISCHARGE_RATE']
        bat_socmax = bat_dict['SOC_MAX']
        bat_socmin = bat_dict['SOC_MIN']
        bat_socinit = bat_dict['SOC_INIT']
        bat_chargeeff = bat_dict['CHARGE_EFF']
        bat_dischargeeff = bat_dict['DISCHARGE_EFF']

        ## 2.1 - Battery constraints: rate of charge and discharge
        if self.args.battery_size != 0:
            idx = np.where(self.agents_df['type'][:] == 'BATTERY')[0]  # batteries locations -> batteries as agents
            for i, _id in enumerate(idx):
                self.model.Inequality_Cons.add(self.model.S_n[_id] <= bat_capacity[i] * bat_chargerate[i])  # charging rate constraints of each battery
                self.model.Inequality_Cons.add(self.model.S_n[_id] >= - bat_capacity[i] * bat_dischargerate[i])  # discharging rate constraints of each battery
            ## 2.2 - Battery constraints: amount of charge and discharge
                self.model.Inequality_Cons.add(self.model.S_n[_id] * bat_chargeeff[i] <= bat_capacity[i] * (bat_socmax[i] - self.model.Soc_n[_id]))  # charging amount constraints of each battery
                self.model.Inequality_Cons.add(self.model.S_n[_id] * bat_dischargeeff[i] >= - bat_capacity[i] * (self.model.Soc_n[_id] - bat_socmin[i]))  # discharging amount constraints of each battery
        ## 2.3 - Upper and lower boundaries constraints
        #TODO{colocar como funções de bounderies na Var}
        # for i, row in self.agents_df.iterrows():
        #     if self.agents_df['type'][i] == 'CONSUMER':  ## consumer
        #         self.model.Inequality_Cons.add(self.model.P_n[i] <= 1.3*row['kw_base']*self.profiles[row['profile']][hour])  # upper boundary constraint
        #         self.model.Inequality_Cons.add(self.model.P_n[i] >= 0.7*row['kw_base']*self.profiles[row['profile']][hour])  # lower boundary constraint
        #         self.model.Inequality_Cons.add(self.model.Q_n[i] <= 0)
        #     if self.agents_df['type'][i] == 'PRODUCER':  ## producer
        #         self.model.Inequality_Cons.add(self.model.P_n[i] <= -0.7*row['kw_base']*self.profiles[row['profile']][hour])  # upper boundary constraint
        #         self.model.Inequality_Cons.add(self.model.P_n[i] >= -1.3*row['kw_base']*self.profiles[row['profile']][hour])  # lower boundary constraint
        #         self.model.Inequality_Cons.add(self.model.Q_n[i] >= 0)
        #     if self.agents_df['type'][i]=='BATTERY':
        #         self.model.Inequality_Cons.add(self.model.P_n[i] <= 0)  # upper boundary constraint
        #         self.model.Inequality_Cons.add(self.model.P_n[i] >= 0)  # lower boundary constraint
        #     if self.agents_df['type'][i]=='EXT_CONSUMER':
        #         self.model.Inequality_Cons.add(self.model.P_n[i] <= row['kw_base'])  # upper boundary constraint
        #         self.model.Inequality_Cons.add(self.model.P_n[i] >= 0)  # lower boundary constraint
        #         self.model.Inequality_Cons.add(self.model.Q_n[i] <= 0)
        #     if self.agents_df['type'][i]=='EXT_PRODUCER':
        #         self.model.Inequality_Cons.add(self.model.P_n[i] <= 0)  # upper boundary constraint
        #         self.model.Inequality_Cons.add(self.model.P_n[i] >= -row['kw_base'])  # lower boundary constraint
        #         self.model.Inequality_Cons.add(self.model.Q_n[i] >= 0)
        ## 2.4 - QoS lower boundaries constraints
        # for j in range(0,n_communities-1):
        #     model.Equality_Cons.add(model.QoS[j] == qos_bound)
        self.model.dual = Suffix(direction=Suffix.IMPORT)
        # opt = SolverFactory('glpk')   # linear optimization

    def defineEqualityCons(self, day, hour):
        r"""
            Caso não tenha bateria no sisma, então Cnstraint de igualdade para cada componente, seguindo a formulação
            \sum^{N_{agents}}_{j\gets 1} \left(P_j + Q_j + \alpha_j + \beta_j + S_j\right) = 0
            Caso contrário:
                Se consumidor ou produtor, então:
                    S_j = 0, \forall 1..j {N_{agents}}
                    Soc_j = 0, \forall 1..j {N_{agents}}
                    Se consumidor, então
                        \beta_j = 0, \forall 1..j {N_{agents}}
                    Se produtor, então
                        \alpha_j = 0, \forall 1..j {N_{agents}}
                Se bateria, então:
                    P_j= 0, \forall 1..j {N_{agents}}
                    \alpha_j = 0, \forall 1..j {N_{agents}}
                    \beta_j = 0, \forall 1..j {N_{agents}}
                Se importador, então:
                    Q_j = 0 \forall 1..j {N_{agents}}
                    S_j = 0 \forall 1..j {N_{agents}}
                    Soc_j = \forall 1..j {N_{agents}}
                    \beta_j = 0, \forall 1..j {N_{agents}}
                Se exportador, então:
                    S_j = 0, \forall 1..j {N_{agents}}
                    Soc_j = 0, \forall 1..j {N_{agents}}
                    \alpha_j = 0, \forall 1..j {N_{agents}}

        """

        self.model.Equality_Cons = ConstraintList()

        for j, row in self.agents_df.iterrows():
            summation = self.model.P_n[j] + self.model.Q_n[j] - self.model.Alpha_n[j] + self.model.Beta_n[j]
            if self.args.battery_size == 0:
                self.inner_community_balance.append(self.model.Equality_Cons.add(summation== 0))
                # model.Equality_Cons.add(model.Q_n[j] == model.Qn_pos[j] + model.Qn_neg[j])
                if row['type'] == 'CONSUMER':  # consumer
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['type'] == 'PRODUCER':  # producer
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
                if row['type'] == 'EXT_CONSUMER':  # external grid consumer
                    self.model.Equality_Cons.add(self.model.Q_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['type'] == 'EXT_PRODUCER':  # external grid producer
                    # model.Equality_Cons.add(model.Q_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
            else:
                summation += self.model.S_n[j]
                self.inner_community_balance.append(self.model.Equality_Cons.add(summation  == 0))
                # model.Equality_Cons.add(model.Q_n[j] == model.Qn_pos[j] + model.Qn_neg[j])
                if row['type'] == 'CONSUMER':  # consumer
                    self.model.Equality_Cons.add(self.model.S_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Soc_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['type'] == 'PRODUCER':  # producer
                    self.model.Equality_Cons.add(self.model.S_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Soc_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
                if row['type'] == 'BATTERY':  # community battery
                    self.model.Equality_Cons.add(self.model.P_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['type'] == 'EXT_CONSUMER':  # external grid consumer
                    self.model.Equality_Cons.add(self.model.Q_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.S_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Soc_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['type'] == 'EXT_PRODUCER':  # external grid producer
                    # model.Equality_Cons.add(model.Q_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.S_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Soc_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
        community_connex_var = np.reshape(self.community_range_set, (self.args.n_communities, self.args.n_communities))
        for j in range(1, self.args.n_communities + 1):
            ## Determines the sum of Qs, Alphas and Betas for each community
            idx = np.where(self.agents_df['community_location'] == j)[0]
            Sigma_Q_n = 0
            Sigma_Qimp_c = 0
            Sigma_Qexp_c = 0
            Sigma_Beta_n = 0
            Sigma_Alpha_n = 0
            for _id in idx:
                Sigma_Q_n = Sigma_Q_n + self.model.Q_n[_id]
                Sigma_Alpha_n = Sigma_Alpha_n + self.model.Alpha_n[_id]
                Sigma_Beta_n = Sigma_Beta_n + self.model.Beta_n[_id]
            for i in range(0, self.args.n_communities):
                Sigma_Qimp_c = Sigma_Qimp_c + self.model.Qimp_c[community_connex_var[j - 1, i]]  # * mat_bilateral[j-1,i]
                Sigma_Qexp_c = Sigma_Qexp_c + self.model.Qexp_c[community_connex_var[j - 1, i]]  # * mat_bilateral[j-1,i]
            ## 1.2 - Adding equality constraints for each community
            self.model.Equality_Cons.add(Sigma_Q_n == 0)
            self.model.Equality_Cons.add(Sigma_Alpha_n == Sigma_Qimp_c)
            self.model.Equality_Cons.add(Sigma_Beta_n == Sigma_Qexp_c)

        for j in range(0, self.args.n_communities):
            for i in range(0, self.args.n_communities):
                self.outer_community_balance.append(self.model.Equality_Cons.add(
                    self.model.Qimp_c[community_connex_var[j, i]] == self.model.Qexp_c[community_connex_var[i, j]]))
                if i==j:
                    self.model.Equality_Cons.add(self.model.Qimp_c[community_connex_var[j, i]] == 0)
        ## 1.3 - Adding state of charge equality constraints
        bat_dict = self.data[f'BatteryList_Caso0{self.args.case}']
        bat_capacity = bat_dict['NOMINAL_CAPACITY_[KWH]']
        bat_autodischargerate = bat_dict['AUTODISCHARGE_RATE']

        if self.args.battery_size!=0:
            if (day == 0 and hour == 0):  ### DEFINES THE STARTING STATE OF CHARGE AS 0.5
                # batteries locations -> batteries as agents
                idx = np.where(self.agents_df['type'][:] == 'BATTERY')[0]
                j = 0
                for i in range(0, self.args.n_agents):
                    if (i in idx):
                        self.model.Equality_Cons.add(self.model.Soc_n[i] == 0.5 * (1 - bat_autodischargerate[j]) + self.model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                        j = j + 1
            elif (day == self.args.day - 1 and hour == self.args.hour - 1):  ### DEFINES THE FINAL STATE OF CHARGE AS 0.5
                idx = np.where(self.agents_df['TYPE'][:] == 'BATTERY')[0]  # batteries locations -> batteries as agents
                j = 0
                for i in range(0, self.args.n_agents):
                    if (i in idx):
                        # model.Equality_Cons.add(model.Soc_n[i] == 0.5)  # agents with batteries start and end simulations at 50%
                        self.model.Equality_Cons.add(self.model.Soc_n[i] == self.agents_results[i][day][hour - 1]['Soc']['Soc'] * (1 - bat_autodischargerate[j]) +
                                                self.model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                        j = j + 1
            elif (day != 0 and hour == 0):  ### DEFINES THE STATE OF CHARGE EQUATION FOR CHANGING DAYS
                idx = np.where(self.agents_df['type'][:] == 'BATTERY')[0]  # batteries locations -> batteries as agents
                j = 0
                for i in range(0, self.args.n_agents):
                    if (i in idx):
                        self.model.model.Equality_Cons.add(self.model.Soc_n[i] == self.agents_results[i][day][hour - 1]['Soc']['Soc'] * (1 - bat_autodischargerate[j]) +
                                                self.model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                        j = j + 1
            else:  ### DEFINES THE STATE OF CHARGE EQUATION THROUGHOUT DAYS
                idx = np.where(self.agents_df['type'][:] == 'BATTERY')[0]  # batteries locations -> batteries as agents
                j = 0
                for i in range(0, self.args.n_agents):
                    if (i in idx):
                        # (agent, day ,hour[hour])
                        self.model.Equality_Cons.add(self.model.Soc_n[i] == self.agents_results[i][day][hour - 1]['Soc'] * (1 - bat_autodischargerate[j]) + self.model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                        j = j + 1

    def minimize(self, hour, day, cost_df):
        self.cost_df = cost_df
        self.case_dict = {
            1: return_matrix_case1to5(cost_df=self.cost_df, n_communities=self.args.n_communities),
            2: return_matrix_case1to5(cost_df=self.cost_df, n_communities=self.args.n_communities),
            3: return_matrix_case1to5(cost_df=self.cost_df, n_communities=self.args.n_communities),
            4: return_matrix_case1to5(cost_df=self.cost_df, n_communities=self.args.n_communities),
            5: return_matrix_case1to5(cost_df=self.cost_df, n_communities=self.args.n_communities),
            6: return_matrix_case6(cost_df=self.cost_df, n_communities=self.args.n_communities),
            7: return_matrix_case7(cost_df=self.cost_df, n_communities=self.args.n_communities)
        }

        mat_bilateral, import_cost, export_cost = self.case_dict[self.args.case]

        self.imp_cost = np.reshape(np.multiply(-import_cost, mat_bilateral), [1, self.args.n_communities ** 2])
        self.exp_cost = np.reshape(np.multiply(export_cost, mat_bilateral), [1, self.args.n_communities ** 2])

        self.opt = SolverFactory('ipopt')  # nonlinear optimization
        self.model.obj = Objective(rule=self.obj_fn_quadratic, sense=minimize)
        self.defineEqualityCons(day=day, hour=hour)
        self.defineInequalityCons(day=day, hour=hour)

        self.results = self.opt.solve(self.model, tee=False)
        print(f'Day: {day}', f'|Hour:{hour}', f'|FOB: {value(self.model.obj)}', f'|Solver Status: {self.results.solver.status}', f'|Termination Condition: {self.results.solver.termination_condition}')
        return self.model, self.results, self.inner_community_balance, self.outer_community_balance


class OptimizationData:
    def __init__(self, args):
        self.args = args
        self.dssConfig = DSSConfig(root_dir=args.root_dir, battery_size=args.battery_size, study_case=args.case, profiles=args.profiles)

        self.opt_logger = [{hour: {} for hour in range(self.args.hour)}for day in range(self.args.day)]
        #(day, hour[hour])
        self.optimization_results = [{hour: {} for hour in range(self.args.hour)}for day in range(self.args.day)]  ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP
        # (agent, day ,hour[hour])
        # day: list, bus: list, hour: dict
        self.community_bus_results = []
        # day: list, line: list, hour: dict
        self.community_lines_results = []


    def updateResults(self, agents_results, communities_results, optimization_results):
        self.agents_results = agents_results
        self.communities_results = communities_results
        self.optimization_results = optimization_results

    def studyCase(self):
        preprocess = PreProcessingData(args=self.args)
        self.agents_results = [[{hour: {} for hour in range(self.args.hour)} for day in range(self.args.day)] for agent in range(self.args.n_agents)]
        # (comm, day ,hour[hour])
        self.communities_results = [[{hour: {} for hour in range(self.args.hour)} for day in range(self.args.day)] for com in range(self.args.n_communities)] ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP
        for day in range(self.args.day):
            for hour in range(self.args.hour):
                preprocess = PreProcessingData(args=self.args)
                self.cost_df = preprocess.costInfo(hour=hour)
                opt = Optmizer(args=self.args,
                               day=day,
                               hour=hour,
                               optimization_results=self.optimization_results, agents_results=self.agents_results,
                               communities_results=self.communities_results)
                self.model, self.results, self.inner_community_balance, self.outer_community_balance = opt.minimize(hour=hour, day=day, cost_df=self.cost_df)
                self.opt_logger[day][hour] = {'fob': value(self.model.obj), 'solver_status': self.results.solver.status,
                                             'condition': self.results.solver.termination_condition,
                                             'opt_model': self.model, 'results': self.results}
                report = Report(n_communities=self.args.n_communities, agents_df=preprocess.agents_df, day=day, hour=hour,
                                battery_size=self.args.battery_size, n_agents=self.args.n_agents,
                                agents_results=opt.agents_results, communities_results=opt.communities_results,
                                optimization_results=opt.optimization_results)
                report.set_report(model=self.model, results=self.results,
                                  inner_community_balance=self.inner_community_balance,
                                  outer_community_balance=self.outer_community_balance)
                self.updateResults(agents_results=report.agents_results, communities_results=report.communities_results,
                                   optimization_results=report.optimization_results)
                preprocess.updateProfiles(hour=hour, agt_results=report.agt_results)

                powerflow = Powerflow(battery_size=self.args.battery_size,
                                      case=self.args.case,
                                      hour=hour,
                                      day=day,
                                      bat_list=preprocess.data[f'BatteryList_Caso0{self.args.case}']['NAME'],
                                      lv_bus_list=preprocess.data['BusListLV']['NAME'],
                                      lvbus_basekv_list=preprocess.data['BusListLV']['BASE_KV'])
                bus_results, line_results = powerflow.calcDSSPowerflow(master_file=self.dssConfig.masterfile,
                                           community_buses=preprocess.community_buses,
                                           community_lines=preprocess.community_lines)

                self.community_bus_results.append(bus_results)
                self.community_lines_results.append(line_results)
                os.chdir(self.args.root_dir)
                del powerflow, opt, preprocess
