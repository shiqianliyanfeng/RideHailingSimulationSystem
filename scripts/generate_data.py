import argparse
import os
import csv
import random

def gen_vehicles(n, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['vid','x','y'])
        for i in range(n):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            w.writerow([i, x, y])

def gen_orders(n, out_path, duration_hours=24):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['oid','x_from','y_from','x_to','y_to','request_time'])
        for i in range(n):
            x1 = random.uniform(0, 100)
            y1 = random.uniform(0, 100)
            x2 = random.uniform(0, 100)
            y2 = random.uniform(0, 100)
            t = random.uniform(0, duration_hours * 3600)
            w.writerow([i, x1, y1, x2, y2, t])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--vehicles', type=int, default=500)
    parser.add_argument('--orders', type=int, default=50000)
    parser.add_argument('--outdir', type=str, default='data')
    args = parser.parse_args()
    gen_vehicles(args.vehicles, os.path.join(args.outdir, 'vehicles.csv'))
    gen_orders(args.orders, os.path.join(args.outdir, 'orders.csv'))
