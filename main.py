from argparse import ArgumentParser
from src.optmizer import OptimizationData
def main():
    parser = ArgumentParser()
    parser.add_argument('--path', type=str, default='data/')
    parser.add_argument('--profiles', type=list, default=['commercial', 'DG', 'industrial', 'residential', 'storage'])
    parser.add_argument('--model_name', type=str, default='Energy_Collectives_Linearized')
    parser.add_argument('--case', type=int, default=6)
    parser.add_argument('--battery_size', type=int, default=10)
    parser.add_argument('--hour', type=int, default=24)
    parser.add_argument('--day', type=int, default=1)

    args = parser.parse_args()
    OptimizationData(args).studyCase()

if __name__ == "__main__":
    main()