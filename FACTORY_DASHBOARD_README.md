# Interactive Factory Simulation Dashboard

An interactive real-time dashboard for visualizing a comprehensive SimPy factory simulation. This project demonstrates discrete event simulation with multiple production lines, machines, workers, inventory management, and quality control.

## Features

### Simulation Components
- **Multiple Production Lines**: Configurable number of parallel production lines
- **Machine Resources**: Limited machines with breakdown and maintenance simulation
- **Worker Pool**: Shared worker resources across production lines
- **Inventory Management**:
  - Raw materials with automatic replenishment
  - Finished goods storage
- **Quality Control**: Random defect detection with configurable failure rates
- **Realistic Timing**: Variable processing times and random machine breakdowns

### Dashboard Features
- **Real-time Visualization**: Charts update as simulation runs
- **Key Metrics Cards**:
  - Products Completed
  - Quality Pass Rate
  - Average Cycle Time
  - Worker Utilization
- **Interactive Charts**:
  - Production Over Time (completed vs in-progress)
  - Inventory Levels (raw materials vs finished goods)
  - Quality Control (passed vs failed)
  - Machine Utilization (individual machine tracking)
- **Configurable Parameters**:
  - Simulation duration
  - Number of production lines
  - Number of machines
  - Number of workers

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Schmierer-Eng
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Dashboard (Recommended)

Start the interactive dashboard:
```bash
python dashboard.py
```

Then open your browser to: `http://127.0.0.1:8050`

**Dashboard Controls:**
1. Set your desired parameters (duration, production lines, machines, workers)
2. Click "Start Simulation"
3. Watch the real-time metrics and charts update
4. Run multiple simulations with different parameters to compare results

### Running Standalone Simulation

You can also run the simulation without the dashboard:
```bash
python factory_simulation.py
```

This will output summary statistics to the console.

## Simulation Details

### Production Flow
1. Raw materials are consumed from inventory
2. Product is assigned to an available machine
3. Worker is assigned to oversee production
4. Processing takes place (variable time)
5. Quality inspection is performed
6. Good products go to finished goods inventory
7. Defective products are scrapped

### Resource Constraints
- **Machines**: Limited number, can break down randomly, require maintenance
- **Workers**: Shared pool across all production lines
- **Raw Materials**: Auto-replenished when below 50% capacity
- **Finished Goods**: Limited storage capacity

### Configurable Parameters

You can modify `DEFAULT_CONFIG` in `factory_simulation.py`:

```python
DEFAULT_CONFIG = {
    # Inventory
    'raw_material_capacity': 1000,
    'initial_raw_materials': 500,
    'finished_goods_capacity': 500,

    # Resources
    'num_machines': 5,
    'num_workers': 10,
    'num_production_lines': 8,

    # Production
    'materials_per_product': 5,
    'min_processing_time': 2.0,
    'max_processing_time': 5.0,
    'defect_rate': 0.05,  # 5% defect rate

    # Supplier
    'supplier_interval': 10.0,
    'supplier_batch_size': 200,

    # Maintenance
    'min_time_to_breakdown': 30.0,
    'max_time_to_breakdown': 100.0,
    'min_maintenance_time': 3.0,
    'max_maintenance_time': 8.0,

    # Metrics
    'metrics_interval': 2.0
}
```

## Project Structure

```
.
├── factory_simulation.py      # Core SimPy simulation logic
├── dashboard.py               # Interactive Dash dashboard
├── requirements.txt           # Python dependencies
└── FACTORY_DASHBOARD_README.md  # This file
```

## Understanding the Metrics

### Products Completed
Total number of products that passed quality inspection and were stored in finished goods inventory.

### Quality Pass Rate
Percentage of products that passed quality inspection out of all inspected products.

### Average Cycle Time
Average time from when a product starts production until it's completed (only for successful products).

### Worker Utilization
Percentage of time workers are actively engaged in production (accounts for all workers).

### Machine Utilization
Individual utilization percentage for each machine, showing how much time each machine spends in production vs idle.

## Learning SimPy Concepts

This project demonstrates several key SimPy concepts:

1. **Resources** (`simpy.Resource`): Machines and workers are limited resources that processes must request
2. **Containers** (`simpy.Container`): Inventory storage with get/put operations
3. **Processes**: Production lines, suppliers, and maintenance are all concurrent processes
4. **Timeouts**: Simulate processing time, delays, and intervals
5. **Environment**: Central simulation clock and event scheduling

## Customization Ideas

- Add different product types with varying processing times
- Implement shift patterns for workers
- Add machine setup/changeover times
- Create a priority system for urgent orders
- Implement predictive maintenance instead of reactive
- Add cost tracking (labor, materials, downtime)
- Model energy consumption
- Add multiple suppliers with different lead times

## Troubleshooting

**Dashboard not loading:**
- Ensure port 8050 is not in use
- Check that all dependencies are installed
- Try accessing `http://localhost:8050` instead

**Simulation runs too fast/slow:**
- Adjust the `duration` parameter
- Modify `metrics_interval` for more/fewer data points
- Change processing times in the config

**Charts not updating:**
- Wait a few seconds for simulation to generate data
- Refresh the browser
- Check browser console for errors

## Requirements

- Python 3.7+
- SimPy 4.1.1
- Dash 2.14.2
- Plotly 5.18.0

## Author

Created by @Schmierer-Eng

Contact: schmierereng@gmail.com

## License

Feel free to use and modify for learning purposes!
