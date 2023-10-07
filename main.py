from argparse import ArgumentParser
from src.pre_processing.data_aquisition import DefaultGridData
def main():
    parser = ArgumentParser()
    parser.add_argument('--data_path', type=str, default='data/dss_data')
    parser.add_argument('--n_days', type=int, default=1)
    parser.add_argument('--n_hours', type=int, default=24)
    parser.add_argument('--case', type=int, default=6)
    parser.add_argument('--battery_size', type=int, default=10)
    args = parser.parse_args()
    DefaultGridData(args=args)


if __name__ == "__main__":
    main()