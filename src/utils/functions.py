import numpy as np
import os
from pandas import DataFrame

def mkdir_if_not_exists(default_save_path: str):
    if not os.path.exists(default_save_path):
        os.mkdir(default_save_path)


def find_file_extention(path, type: str = '.csv'):
    filenames = os.listdir(path)
    return [f"{path}/{filename}" for filename in filenames if filename.endswith(type)]

def return_matrix_case1to5(cost_df:DataFrame, n_communities):
    mat_bilateral = np.ones((n_communities, n_communities)) - np.eye((n_communities), (n_communities))
    import_cost = np.matrix([[0.0, cost_df['IMP_COST'].max()],
                             [cost_df['IMP_COST'].max(), 0.0]])
    export_cost = np.matrix([[0.0, cost_df['EXP_COST'].max()],
                             [cost_df['EXP_COST'].max(), 0.0]])

    return mat_bilateral, import_cost, export_cost


def return_matrix_case6(cost_df:DataFrame, n_communities):
    mat_bilateral = np.ones((n_communities, n_communities)) - np.eye((n_communities), (n_communities))
    import_cost = np.matrix([[0.0, 0.1, 0.1, cost_df['IMP_COST'].max()],
                             [0.1, 0.0, 0.1, cost_df['IMP_COST'].max()],
                             [0.1, 0.1, 0.0, cost_df['IMP_COST'].max()],
                             [cost_df['IMP_COST'].max(), cost_df['IMP_COST'].max(), cost_df['IMP_COST'].max(), 0.0]])
    export_cost = np.matrix([[0.0, 0.05, 0.05, cost_df['EXP_COST'].max()],
                             [0.05, 0.0, 0.05, cost_df['EXP_COST'].max()],
                             [0.05, 0.05, 0.0, cost_df['EXP_COST'].max()],
                             [cost_df['EXP_COST'].max(), cost_df['EXP_COST'].max(), cost_df['EXP_COST'].max(), 0.0]])
    return mat_bilateral, import_cost, export_cost


def return_matrix_case7(cost_df:DataFrame, n_communities):
    mat_bilateral = np.ones((n_communities, n_communities)) - np.eye((n_communities), (n_communities))
    import_cost = np.matrix([[0.0, 0.1, 0.1, 0.1, 0.1, cost_df['IMP_COST'].max()],
                             [0.1, 0.0, 0.1, 0.1, 0.1, cost_df['IMP_COST'].max()],
                             [0.1, 0.1, 0.0, 0.1, 0.1, cost_df['IMP_COST'].max()],
                             [0.1, 0.1, 0.1, 0.0, 0.1, cost_df['IMP_COST'].max()],
                             [0.1, 0.1, 0.1, 0.1, 0.0, cost_df['IMP_COST'].max()],
                             [cost_df['IMP_COST'].max(), cost_df['IMP_COST'].max(), cost_df['IMP_COST'].max(),
                              cost_df['IMP_COST'].max(), cost_df['IMP_COST'].max(), 0.0]])
    export_cost = np.matrix([[0.0, 0.05, 0.05, 0.05, 0.05, cost_df['EXP_COST'].max()],
                             [0.05, 0.0, 0.05, 0.05, 0.05, cost_df['EXP_COST'].max()],
                             [0.05, 0.05, 0.0, 0.05, 0.05, cost_df['EXP_COST'].max()],
                             [0.05, 0.05, 0.05, 0.0, 0.05, cost_df['EXP_COST'].max()],
                             [0.05, 0.05, 0.05, 0.05, 0.0, cost_df['EXP_COST'].max()],
                             [cost_df['EXP_COST'].max(), cost_df['EXP_COST'].max(), cost_df['EXP_COST'].max(),
                              cost_df['EXP_COST'].max(), cost_df['EXP_COST'].max(), 0.0]])

    return mat_bilateral, import_cost, export_cost
