from argparse import ArgumentParser
from src.processing import PreProcessingData
def main():
    parser = ArgumentParser()
    parser.add_argument('--path', type=str, default='data/dss_data')
    parser.add_argument('--case', type=int, default=6)
    parser.add_argument('--battery_size', type=int, default=10)
    parser.add_argument('--hour', type=int, default=24)
    parser.add_argument('--day', type=int, default=1)

    args = parser.parse_args()
    PreProcessingData(args=args)

if __name__ == "__main__":
    main()