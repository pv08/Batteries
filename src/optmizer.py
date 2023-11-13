from pyomo.environ import *
from src.processing import PreProcessingData
from src.utils.functions import *

class Optmizer(PreProcessingData):
    def __init__(self, args):
        super(Optmizer, self).__init__(args=args)
        self.model = ConcreteModel(args.model_name)

        self.optimization_results = {day: {hour: {} for hour in range(self.args.hour)} for day in range(self.args.day)}  ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP
        self.agents_results = {agent: {day: {hour: {} for hour in range(self.args.hour)} for day in range(self.args.day)} for agent in range(self.args.n_agents)}  ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP
        self.communities_results = {community: {day: {hour: {} for hour in range(self.args.hour)} for day in range(self.args.day)} for community in range(1, self.args.n_communities + 1)}  ## RESULTS DICTIONARY - MUST BE DECLARED BEFORE OPTIMIZATION LOOP

        self.agent_range_set = range(self.args.n_agents)
        self.community_set = range(self.args.n_communities - 1)
        self.community_range_set = range(self.args.n_communities**2)

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

        self.model.P_n = Var(self.agent_range_set, domain=Reals)
        self.model.Q_n = Var(self.agent_range_set, domain=Reals)
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

    def obj_fn_quadratic(self, model):
        obj_function = 0
        for j in range(0, self.args.n_agents):
            if self.agents_df['TYPE'][j] == 'CONSUMER':
                obj_function = obj_function - (
                            0.5 * self.cost_df['A_[R$/KW^2]'][j] * model.P_n[j] * model.P_n[j] + self.cost_df['B_[R$/KW]'][j] *
                            model.P_n[j])
                obj_function = obj_function - (self.cost_df['INNER_COST'][j] * model.Q_n[j])
            if self.agents_df['TYPE'][j] == 'PRODUCER':
                obj_function = obj_function - (
                            0.5 * self.cost_df['A_[R$/KW^2]'][j] * model.P_n[j] * model.P_n[j] + self.cost_df['B_[R$/KW]'][j] *
                            model.P_n[j])
                obj_function = obj_function - (self.cost_df['INNER_COST'][j] * model.Q_n[j])
            if self.agents_df['TYPE'][j] == 'BATTERY':
                obj_function = obj_function + (self.cost_df['COST_S'][j] * model.S_n[j])
                obj_function = obj_function - (self.cost_df['INNER_COST'][j] * model.Q_n[j])
        for j in range(0, self.args.n_communities ** 2):
            obj_function = obj_function + (self.imp_cost[0, j] * model.Qimp_c[j])
            obj_function = obj_function + (self.exp_cost[0, j] * model.Qexp_c[j])

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
            idx = np.where(self.agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
            for i in range(0, len(idx[0])):
                self.model.Inequality_Cons.add(self.model.S_n[idx[0][i]] <= bat_capacity[i] * bat_chargerate[
                    i])  # charging rate constraints of each battery
                self.model.Inequality_Cons.add(self.model.S_n[idx[0][i]] >= - bat_capacity[i] * bat_dischargerate[
                    i])  # discharging rate constraints of each battery
            ## 2.2 - Battery constraints: amount of charge and discharge
            idx = np.where(self.agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
            for i in range(0, len(idx[0])):
                self.model.Inequality_Cons.add(self.model.S_n[idx[0][i]] * bat_chargeeff[i] <= bat_capacity[i] *
                                          (bat_socmax[i] - self.model.Soc_n[
                                              idx[0][i]]))  # charging amount constraints of each battery
                self.model.Inequality_Cons.add(self.model.S_n[idx[0][i]] * bat_dischargeeff[i] >= - bat_capacity[i] *
                                          (self.model.Soc_n[idx[0][i]] - bat_socmin[
                                              i]))  # discharging amount constraints of each battery
        ## 2.3 - Upper and lower boundaries constraints
        for i in range(0, self.args.n_agents):
            if self.agents_df['TYPE'][i] == 'CONSUMER':  ## consumer
                self.model.Inequality_Cons.add(self.model.P_n[i] <= 1.3*self.agents_df['BASE_KW'][i]*self.profiles[self.agents_df['PROFILE'][i]][0][hour])  # upper boundary constraint
                self.model.Inequality_Cons.add(self.model.P_n[i] >= 0.7*self.agents_df['BASE_KW'][i]*self.profiles[self.agents_df['PROFILE'][i]][0][hour])  # lower boundary constraint
                self.model.Inequality_Cons.add(self.model.Q_n[i] <= 0)
            if self.agents_df['TYPE'][i] == 'PRODUCER':  ## producer
                self.model.Inequality_Cons.add(self.model.P_n[i] <= -0.7*self.agents_df['BASE_KW'][i]*self.profiles[self.agents_df['PROFILE'][i]][0][hour])  # upper boundary constraint
                self.model.Inequality_Cons.add(self.model.P_n[i] >= -1.3*self.agents_df['BASE_KW'][i]*self.profiles[self.agents_df['PROFILE'][i]][0][hour])  # lower boundary constraint
                self.model.Inequality_Cons.add(self.model.Q_n[i] >= 0)
            # if agents_df['TYPE'][i]=='BATTERY':
            #     model.Inequality_Cons.add(model.P_n[i] <= 0)  # upper boundary constraint
            #     model.Inequality_Cons.add(model.P_n[i] >= 0)  # lower boundary constraint
            if self.agents_df['TYPE'][i]=='EXT_CONSUMER':
                self.model.Inequality_Cons.add(self.model.P_n[i] <= self.agents_df['BASE_KW'][i])  # upper boundary constraint
                self.model.Inequality_Cons.add(self.model.P_n[i] >= 0)  # lower boundary constraint
                self.model.Inequality_Cons.add(self.model.Q_n[i] <= 0)
            if self.agents_df['TYPE'][i]=='EXT_PRODUCER':
                self.model.Inequality_Cons.add(self.model.P_n[i] <= 0)  # upper boundary constraint
                self.model.Inequality_Cons.add(self.model.P_n[i] >= -self.agents_df['BASE_KW'][i])  # lower boundary constraint
                self.model.Inequality_Cons.add(self.model.Q_n[i] >= 0)
        ## 2.4 - QoS lower boundaries constraints
        # for j in range(0,n_communities-1):
        #     model.Equality_Cons.add(model.QoS[j] == qos_bound)
        self.model.dual = Suffix(direction=Suffix.IMPORT)
        # opt = SolverFactory('glpk')   # linear optimization
        opt = SolverFactory('ipopt')  # nonlinear optimization
        results = opt.solve(self.model, tee=False)
        print('Day:', day, 'Hour:', hour, '\n Solver Status:', results.solver.status, '\n Termination Condition:',
              results.solver.termination_condition)

        return self.model, results, self.inner_community_balance, self.outer_community_balance

    def defineEqualityCons(self, day, hour):
        self.model.Equality_Cons = ConstraintList()
        self.inner_community_balance = []

        for j, row in self.agents_df.iterrows():
            summation = self.model.P_n[j] + self.model.Q_n[j] - self.model.Alpha_n[j] + self.model.Beta_n[j]
            if self.args.battery_size == 0:
                self.inner_community_balance.append(self.model.Equality_Cons.add(summation== 0))
                # model.Equality_Cons.add(model.Q_n[j] == model.Qn_pos[j] + model.Qn_neg[j])
                if row['TYPE'] == 'CONSUMER':  # consumer
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['TYPE'] == 'PRODUCER':  # producer
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
                if row['TYPE'] == 'EXT_CONSUMER':  # external grid consumer
                    self.model.Equality_Cons.add(self.model.Q_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['TYPE'] == 'EXT_PRODUCER':  # external grid producer
                    # model.Equality_Cons.add(model.Q_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
            else:
                summation += self.model.S_n[j]
                self.inner_community_balance.append(self.model.Equality_Cons.add(summation  == 0))
                # model.Equality_Cons.add(model.Q_n[j] == model.Qn_pos[j] + model.Qn_neg[j])
                if row['TYPE'] == 'CONSUMER':  # consumer
                    self.model.Equality_Cons.add(self.model.S_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Soc_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['TYPE'] == 'PRODUCER':  # producer
                    self.model.Equality_Cons.add(self.model.S_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Soc_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
                if row['TYPE'] == 'BATTERY':  # community battery
                    self.model.Equality_Cons.add(self.model.P_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['TYPE'] == 'EXT_CONSUMER':  # external grid consumer
                    self.model.Equality_Cons.add(self.model.Q_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.S_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Soc_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Beta_n[j] == 0)
                if row['TYPE'] == 'EXT_PRODUCER':  # external grid producer
                    # model.Equality_Cons.add(model.Q_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.S_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Soc_n[j] == 0)
                    self.model.Equality_Cons.add(self.model.Alpha_n[j] == 0)
        community_connex_var = np.reshape(self.community_range_set, (self.args.n_communities, self.args.n_communities))
        for j in range(1, self.args.n_communities + 1):
            ## Determines the sum of Qs, Alphas and Betas for each community
            idx = np.where(self.agents_df['COMMUNITY_LOCATION'] == j)
            Sigma_Q_n = 0
            Sigma_Qimp_c = 0
            Sigma_Qexp_c = 0
            Sigma_Beta_n = 0
            Sigma_Alpha_n = 0
            for i in range(0, len(idx[0])):
                Sigma_Q_n = Sigma_Q_n + self.model.Q_n[idx[0][i]]
                Sigma_Alpha_n = Sigma_Alpha_n + self.model.Alpha_n[idx[0][i]]
                Sigma_Beta_n = Sigma_Beta_n + self.model.Beta_n[idx[0][i]]
            for i in range(0, self.args.n_communities):
                Sigma_Qimp_c = Sigma_Qimp_c + self.model.Qimp_c[community_connex_var[j - 1, i]]  # * mat_bilateral[j-1,i]
                Sigma_Qexp_c = Sigma_Qexp_c + self.model.Qexp_c[community_connex_var[j - 1, i]]  # * mat_bilateral[j-1,i]
            ## 1.2 - Adding equality constraints for each community
            self.model.Equality_Cons.add(Sigma_Q_n == 0)
            self.model.Equality_Cons.add(Sigma_Alpha_n == Sigma_Qimp_c)
            self.model.Equality_Cons.add(Sigma_Beta_n == Sigma_Qexp_c)
        self.outer_community_balance = []
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
            if (self.args.day == 0 and self.args.hour == 0):  ### DEFINES THE STARTING STATE OF CHARGE AS 0.5
                idx = np.where(self.agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
                j = 0
                for i in range(0, self.args.n_agents):
                    if (i == idx[0][:]).any():
                        self.model.Equality_Cons.add(self.model.Soc_n[i] == 0.5 * (1 - bat_autodischargerate[j]) + self.model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                        j = j + 1
            elif (self.args.day == self.args.n_days - 1 and hour == self.args.n_hours - 1):  ### DEFINES THE FINAL STATE OF CHARGE AS 0.5
                idx = np.where(self.agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
                j = 0
                for i in range(0, self.args.n_agents):
                    if (i == idx[0][:]).any():
                        # model.Equality_Cons.add(model.Soc_n[i] == 0.5)  # agents with batteries start and end simulations at 50%
                        self.model.Equality_Cons.add(self.model.Soc_n[i] == self.agents_results[i][day][hour - 1]['Soc'] * (1 - bat_autodischargerate[j]) +
                                                self.model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                        j = j + 1
            elif (day != 0 and hour == 0):  ### DEFINES THE STATE OF CHARGE EQUATION FOR CHANGING DAYS
                idx = np.where(self.agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
                j = 0
                for i in range(0, self.args.n_agents):
                    if (i == idx[0][:]).any():
                        self.model.model.Equality_Cons.add(self.model.Soc_n[i] == self.agents_results[i][day - 1][self.args.n_hours - 1]['Soc'] * (1 - bat_autodischargerate[j]) +
                                                self.model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                        j = j + 1
            else:  ### DEFINES THE STATE OF CHARGE EQUATION THROUGHOUT DAYS
                idx = np.where(self.agents_df['TYPE'][:] == 'BATTERY')  # batteries locations -> batteries as agents
                j = 0
                for i in range(0, self.n_agents):
                    if (i == idx[0][:]).any():
                        self.model.Equality_Cons.add(self.model.Soc_n[i] == self.agents_results[i][day][hour - 1]['Soc'] * (1 - bat_autodischargerate[j]) +
                                                self.model.S_n[i] / bat_capacity[j])  # agents with batteries start and end simulations at 50%
                        j = j + 1

    def minimize(self, hour, day):
        self.model.obj = Objective(rule=self.obj_fn_quadratic, sense=minimize)
        self.defineEqualityCons(day=day, hour=hour)
        self.defineInequalityCons(day=day, hour=hour)
class OptimizationData(Optmizer):
    def __init__(self, args):
        super(OptimizationData, self).__init__(args=args)

    def studyCase(self):
        for day in range(self.args.day):
            for hour in range(self.args.hour):
                self.minimize(hour=hour, day=day)

