import csv
import matplotlib.pyplot as plt
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: plot_metrics.py path/to/metrics.csv')
        sys.exit(1)
    path = sys.argv[1]
    hrs = []
    avg_wait = None
    with open(path, 'r') as f:
        r = csv.reader(f)
        headers = next(r)
        for row in r:
            if row[0] == 'avg_wait_s':
                avg_wait = float(row[1]) if row[1] else None
    print('avg_wait_s =', avg_wait)
