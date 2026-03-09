# Factory Simulation Project - Claude Context

## Project Overview

This repository contains a comprehensive factory simulation system built with SimPy (discrete event simulation library). The project demonstrates manufacturing process modeling with interactive visualization and static reporting capabilities.

**Purpose:** Educational simulation project for learning SimPy and discrete event simulation concepts, with practical applications in manufacturing process analysis and optimization.

## Project Structure

```
.
├── factory_simulation.py          # Core SimPy simulation engine
├── dashboard.py                   # Interactive Dash web dashboard
├── generate_pdf_report.py         # Static PDF report generator
├── requirements.txt               # Python dependencies
├── run_dashboard.sh              # Quick launch script for dashboard
├── README.md                     # Main project documentation
├── FACTORY_DASHBOARD_README.md   # Detailed dashboard documentation
└── CLAUDE.md                     # This file
```

## Core Components

### 1. Factory Simulation (`factory_simulation.py`)

**Purpose:** SimPy-based discrete event simulation modeling a factory with multiple production lines.

**Key Classes:**
- `SimulationMetrics` - Dataclass storing all time-series metrics for analysis
- `Factory` - Main factory class managing resources and tracking
- `Product` - Individual product with cycle time tracking

**Key Processes:**
- `production_line()` - Simulates individual production line workflow
- `raw_material_supplier()` - Manages inventory replenishment
- `machine_maintenance()` - Simulates random breakdowns and repairs
- `metrics_collector()` - Records metrics at regular intervals

**Simulation Features:**
- Multiple parallel production lines (configurable)
- Limited machine resources with random breakdowns
- Shared worker pool across lines
- Raw material and finished goods inventory with capacity limits
- Quality control with configurable defect rates
- Comprehensive metrics collection

**Configuration:** All parameters in `DEFAULT_CONFIG` dict including:
- Resource counts (machines, workers, production lines)
- Processing times (min/max ranges)
- Inventory capacities
- Quality defect rates
- Maintenance schedules

### 2. Interactive Dashboard (`dashboard.py`)

**Purpose:** Real-time web-based visualization using Dash and Plotly.

**Features:**
- Live updating charts during simulation
- Configurable simulation parameters via UI
- Four main visualizations:
  - Production over time (completed vs in-progress)
  - Inventory levels (raw materials vs finished goods)
  - Quality control (passed vs failed)
  - Machine utilization (per-machine tracking)
- KPI cards showing key metrics
- Runs simulation in background thread

**Usage:** `python dashboard.py` then open http://127.0.0.1:8050

**Color Scheme:**
- Completed/Passed: #27ae60 (green)
- In Progress: #f39c12 (orange)
- Raw Materials: #3498db (blue)
- Finished Goods: #9b59b6 (purple)
- Failed: #e74c3c (red)

### 3. PDF Report Generator (`generate_pdf_report.py`)

**Purpose:** Generate static, professional PDF reports from simulation runs.

**Features:**
- Command-line interface with full configuration options
- Four matplotlib charts matching dashboard styling
- Multi-page PDF layout using reportlab
- KPI summary tables
- Configuration documentation
- Detailed machine performance breakdown
- Automated insights generation

**Usage:**
```bash
python generate_pdf_report.py --duration 100 --machines 5 --workers 10
```

**Output:** Professional 4-page PDF report with:
- Page 1: Executive summary, KPIs, configuration
- Page 2: Production and inventory charts
- Page 3: Quality and machine utilization charts
- Page 4: Detailed statistics and machine breakdown

## Development Guidelines

### When Working on This Project

1. **Don't Modify Core Simulation:**
   - `factory_simulation.py` is the foundation - changes here affect both dashboard and PDF generator
   - `SimulationMetrics` dataclass is the contract between simulation and visualization
   - Test both dashboard and PDF generator after any simulation changes

2. **Maintain Visual Consistency:**
   - Use the defined color scheme across all visualizations
   - Match chart styles between dashboard and PDF reports
   - Keep metric calculations consistent

3. **Configuration Changes:**
   - Update `DEFAULT_CONFIG` in `factory_simulation.py`
   - Document new parameters in all three READMEs
   - Ensure CLI arguments in PDF generator match available config

4. **Testing Checklist:**
   - Run standalone simulation: `python factory_simulation.py`
   - Test dashboard: `python dashboard.py`
   - Generate PDF report: `python generate_pdf_report.py`
   - Verify metrics consistency across all three

### Common Tasks

**Add New Metric:**
1. Add to `SimulationMetrics` dataclass
2. Update `metrics_collector()` to record it
3. Add visualization to dashboard callbacks
4. Add chart to PDF generator
5. Update documentation

**Modify Simulation Logic:**
1. Edit relevant process function in `factory_simulation.py`
2. Test with standalone run
3. Verify dashboard still works
4. Regenerate PDF to verify compatibility
5. Update DEFAULT_CONFIG if needed

**Add New Visualization:**
1. Create chart in dashboard (Plotly)
2. Create corresponding matplotlib version for PDF
3. Match colors and styling
4. Update README with description

### Dependencies

**Core:**
- `simpy>=4.1.1` - Discrete event simulation framework

**Dashboard:**
- `dash>=2.14.2` - Web application framework
- `plotly>=5.18.0` - Interactive plotting library

**PDF Reports:**
- `matplotlib>=3.8.2` - Static plotting library
- `reportlab>=4.1.0` - PDF generation library
- `Pillow>=10.2.0` - Image processing for embedding charts

## SimPy Concepts Demonstrated

This project showcases several key SimPy patterns:

1. **Resources** - Limited machines and workers that processes must request
2. **Containers** - Inventory storage with get/put operations
3. **Processes** - Concurrent production lines, suppliers, maintenance
4. **Environment** - Central simulation clock and event scheduling
5. **Timeouts** - Delays for processing, maintenance, delivery
6. **Resource Requests** - Using `with resource.request()` pattern

## Troubleshooting

**Import Errors:**
```bash
pip install -r requirements.txt
```

**Dashboard Won't Start:**
- Check if port 8050 is available
- Try `http://localhost:8050` instead of 127.0.0.1
- Ensure all dependencies installed

**PDF Generation Fails:**
- Verify matplotlib, reportlab, Pillow are installed
- Check output path is writable
- Run with `--duration 10` for quick test

**Metrics Don't Match:**
- Ensure using same configuration in all tools
- Check simulation completed fully
- Verify metrics_interval is appropriate

## Performance Notes

- **Small simulations** (duration < 50): Very fast, good for testing
- **Medium simulations** (duration 100-200): Typical use case, 2-5 seconds
- **Large simulations** (duration > 500): May take 10+ seconds

- Dashboard updates every 1 second while running
- PDF generation includes chart rendering time (~2-3 seconds)
- Metrics are collected at configurable intervals (default: every 2 time units)

## Future Enhancement Ideas

- Export to Excel format
- Comparative analysis (multiple simulation runs)
- Parameter optimization using genetic algorithms
- Cost modeling (materials, labor, downtime)
- Energy consumption tracking
- Shift patterns and scheduling
- Multiple product types with different requirements
- Supply chain modeling (multiple suppliers)
- Predictive maintenance instead of reactive
- Statistical process control (SPC) charts

## Contact & Learning

**Author:** @Schmierer-Eng
**Email:** schmierereng@gmail.com

**Learning Resources:**
- SimPy Documentation: https://simpy.readthedocs.io/
- Dash Documentation: https://dash.plotly.com/
- Discrete Event Simulation: https://en.wikipedia.org/wiki/Discrete-event_simulation

## Version History

- **v1.0** - Initial interactive dashboard with SimPy simulation
- **v1.1** - Added PDF report generation capability

---

*This file provides context for Claude Code sessions. It helps Claude understand the project structure, dependencies, and development patterns when assisting with code changes or new features.*
