import os
from argparse import ArgumentParser
from src.optmizer import OptimizationData
from src.processing import PreProcessingData
def main():
    parser = ArgumentParser()
    parser.add_argument('--path', type=str, default='data/')
    parser.add_argument('--root_dir', type=str, default=os.path.dirname(__file__))
    parser.add_argument('--profiles', type=list, default=['commercial', 'DG', 'industrial', 'residential', 'storage'])
    parser.add_argument('--model_name', type=str, default='Energy_Collectives_Linearized')
    parser.add_argument('--case', type=int, default=4)
    parser.add_argument('--battery_size', type=int, default=1)
    parser.add_argument('--battery_allocation', type=bool, default=False)
    parser.add_argument('--hour', type=int, default=24)
    parser.add_argument('--day', type=int, default=1)

    args = parser.parse_args()
    preprocess = PreProcessingData(args=args)
    no_storage_simulation_results = OptimizationData(args=args,
                                         bus_list=preprocess.agents_df['bus'].to_list(),
                                         battery_allocation=False).optNoStorage(day_range=args.day, hour_range=args.hour,
                                                                                n_agents=preprocess.n_agents,
                                                                                n_communities=preprocess.n_communities)
    print(no_storage_simulation_results)
    # #lista para saber as baterias alocadas
    located_bus = []
    # # lista total de baterias
    bus_list = preprocess.data['BusListLV']['NAME'].to_list()
    for bus_i, bus in enumerate(bus_list):
        located_bus.append({'name': f'BAT1FFLX{bus_i:02}', 'bus': bus})
        #faz a otimização com a lista de baterias alocadas
        with_storage_simulation_results = OptimizationData(args=args,
                         bus_list=preprocess.agents_df['bus'].to_list(),
                         battery_allocation=True, bat_bus_location=located_bus).optWithStorage(day_range=args.day, hour_range=args.hour,
                                                                n_agents=preprocess.n_agents + len(located_bus),
                                                                n_communities=preprocess.n_communities, bat_bus_location=located_bus)
        #se tiver violação, coloco a bateria onde teve maior violação
        print(with_storage_simulation_results)

        #se não tiver, tiro a bateria a última e coloco outra (próxima iteração)

if __name__ == "__main__":
    main()