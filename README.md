RideHailingSimulationSystem

简要说明：这是一个基于 PRD 的网约车调度仿真系统最小可运行原型。

快速开始：
1. 创建 Python 3.10+ 虚拟环境并安装依赖：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 生成示例数据并运行仿真：

```bash
python scripts/generate_data.py --vehicles 500 --orders 5000 --outdir data/
python -m ridehailing.cli --config sample_config.yaml
```

输出：JSONL 日志（`logs/`）、指标 CSV（`output/metrics.csv`）和 Matplotlib 图像。

实现说明：
- 支持两种调度策略：KM（基于 SciPy 的匈牙利实现）与 nearest（最近优先贪心）。
- 地图为合成二维平面，使用欧氏距离与速度缩放计算预计时间。
- 仿真为离线批处理，支持 YAML 配置文件。
