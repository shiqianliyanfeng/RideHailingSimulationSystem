RideHailingSimulationSystem

Overview: This repository contains a minimal runnable prototype of a ride-hailing dispatch simulation built from the project's PRD.

Quick start:
1. Create a Python 3.10+ virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Generate example data and run the simulation:

```bash
python scripts/generate_data.py --vehicles 500 --orders 5000 --outdir data/
python -m ridehailing.cli --config sample_config.json
```

Outputs: JSONL event logs (`logs/`), metrics CSV (`output/metrics.csv`), and a Matplotlib PNG (`output/avg_wait.png`).

Implementation notes:
- Two scheduling strategies are supported: `km` (Hungarian algorithm via SciPy) and `nearest` (greedy by closest distance).
- The simulated map is a synthetic 2D plane; travel times are computed from Euclidean distances with a speed scaling factor to model traffic.
- The simulation runs as an offline batch process driven by an event queue and a YAML/JSON configuration file.

Files of interest:
- `ridehailing/scheduler.py` — matching algorithms (KM and nearest)
- `ridehailing/simulator.py` — event-driven simulator and state transitions
- `ridehailing/models.py` — vehicle and order data models and states
- `scripts/generate_data.py` — generates synthetic vehicles and orders CSVs

If you want a quick smoke-run using a small dataset:

```bash
python scripts/generate_data.py --vehicles 10 --orders 50 --outdir data
python -m ridehailing.cli --config sample_config.json
```

If you prefer YAML configuration, use `sample_config.yaml` instead of `sample_config.json` (requires PyYAML).
