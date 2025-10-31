import argparse
from .simulator import Simulator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', required=True, help='path to YAML config')
    args = parser.parse_args()
    sim = Simulator(args.config)
    sim.load_data(sim.cfg['data']['vehicles_csv'], sim.cfg['data']['orders_csv'])
    sim.run()

if __name__ == '__main__':
    main()
