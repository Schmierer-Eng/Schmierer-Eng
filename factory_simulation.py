"""
SimPy Factory Simulation
A comprehensive factory simulation with multiple production lines, machines, and workers.
"""

import simpy
import random
from dataclasses import dataclass, field
from typing import List, Dict
import json


@dataclass
class SimulationMetrics:
    """Track all simulation metrics for the dashboard"""
    time: List[float] = field(default_factory=list)
    products_completed: List[int] = field(default_factory=list)
    products_in_progress: List[int] = field(default_factory=list)
    raw_materials: List[int] = field(default_factory=list)
    finished_goods: List[int] = field(default_factory=list)
    machine_utilization: Dict[str, List[float]] = field(default_factory=dict)
    worker_utilization: List[float] = field(default_factory=list)
    quality_passed: List[int] = field(default_factory=list)
    quality_failed: List[int] = field(default_factory=list)
    average_cycle_time: List[float] = field(default_factory=list)

    def to_dict(self):
        """Convert metrics to dictionary for JSON serialization"""
        return {
            'time': self.time,
            'products_completed': self.products_completed,
            'products_in_progress': self.products_in_progress,
            'raw_materials': self.raw_materials,
            'finished_goods': self.finished_goods,
            'machine_utilization': self.machine_utilization,
            'worker_utilization': self.worker_utilization,
            'quality_passed': self.quality_passed,
            'quality_failed': self.quality_failed,
            'average_cycle_time': self.average_cycle_time
        }


class Factory:
    """Main factory simulation class"""

    def __init__(self, env: simpy.Environment, config: dict):
        self.env = env
        self.config = config

        # Resources
        self.raw_material_inventory = simpy.Container(
            env,
            capacity=config['raw_material_capacity'],
            init=config['initial_raw_materials']
        )
        self.finished_goods_inventory = simpy.Container(
            env,
            capacity=config['finished_goods_capacity'],
            init=0
        )

        # Machines (limited resources that can break down)
        self.machines = {
            f"Machine_{i}": simpy.Resource(env, capacity=1)
            for i in range(config['num_machines'])
        }

        # Workers
        self.workers = simpy.Resource(env, capacity=config['num_workers'])

        # Tracking
        self.products_completed = 0
        self.products_in_progress = 0
        self.quality_passed = 0
        self.quality_failed = 0
        self.cycle_times = []

        # Machine stats
        self.machine_busy_time = {name: 0 for name in self.machines.keys()}
        self.machine_last_start = {name: 0 for name in self.machines.keys()}

        # Worker stats
        self.worker_busy_time = 0
        self.worker_last_start = 0

        # Metrics for dashboard
        self.metrics = SimulationMetrics()

    def record_metrics(self):
        """Record current state metrics"""
        self.metrics.time.append(self.env.now)
        self.metrics.products_completed.append(self.products_completed)
        self.metrics.products_in_progress.append(self.products_in_progress)
        self.metrics.raw_materials.append(int(self.raw_material_inventory.level))
        self.metrics.finished_goods.append(int(self.finished_goods_inventory.level))
        self.metrics.quality_passed.append(self.quality_passed)
        self.metrics.quality_failed.append(self.quality_failed)

        # Calculate machine utilization
        for machine_name in self.machines.keys():
            if machine_name not in self.metrics.machine_utilization:
                self.metrics.machine_utilization[machine_name] = []

            if self.env.now > 0:
                utilization = (self.machine_busy_time[machine_name] / self.env.now) * 100
                self.metrics.machine_utilization[machine_name].append(utilization)
            else:
                self.metrics.machine_utilization[machine_name].append(0)

        # Calculate worker utilization
        if self.env.now > 0:
            worker_util = (self.worker_busy_time / (self.env.now * self.config['num_workers'])) * 100
            self.metrics.worker_utilization.append(worker_util)
        else:
            self.metrics.worker_utilization.append(0)

        # Average cycle time
        if self.cycle_times:
            avg_cycle = sum(self.cycle_times) / len(self.cycle_times)
            self.metrics.average_cycle_time.append(avg_cycle)
        else:
            self.metrics.average_cycle_time.append(0)


class Product:
    """Represents a product being manufactured"""

    product_counter = 0

    def __init__(self, env: simpy.Environment):
        Product.product_counter += 1
        self.id = Product.product_counter
        self.env = env
        self.start_time = env.now
        self.end_time = None

    def get_cycle_time(self):
        """Get the total cycle time for this product"""
        if self.end_time:
            return self.end_time - self.start_time
        return None


def production_line(env: simpy.Environment, factory: Factory, line_id: int):
    """
    Simulates a production line that:
    1. Consumes raw materials
    2. Uses a machine to process
    3. Requires worker oversight
    4. Performs quality check
    5. Stores finished goods
    """

    while True:
        # Wait for raw materials
        yield env.timeout(random.uniform(0.5, 1.5))  # Time to start new product

        # Check if we have raw materials
        if factory.raw_material_inventory.level < factory.config['materials_per_product']:
            yield env.timeout(2)  # Wait for materials
            continue

        # Create new product
        product = Product(env)
        factory.products_in_progress += 1

        # Consume raw materials
        yield factory.raw_material_inventory.get(factory.config['materials_per_product'])

        # Select a random machine
        machine_name = random.choice(list(factory.machines.keys()))
        machine = factory.machines[machine_name]

        # Request machine and worker
        with machine.request() as machine_req, factory.workers.request() as worker_req:
            # Wait for both machine and worker
            factory.machine_last_start[machine_name] = env.now
            factory.worker_last_start = env.now

            yield machine_req & worker_req

            # Processing time
            processing_time = random.uniform(
                factory.config['min_processing_time'],
                factory.config['max_processing_time']
            )
            yield env.timeout(processing_time)

            # Update utilization tracking
            factory.machine_busy_time[machine_name] += env.now - factory.machine_last_start[machine_name]
            factory.worker_busy_time += env.now - factory.worker_last_start

        # Quality check
        quality_passed = random.random() > factory.config['defect_rate']

        if quality_passed:
            factory.quality_passed += 1

            # Try to store finished goods
            if factory.finished_goods_inventory.level < factory.finished_goods_inventory.capacity:
                yield factory.finished_goods_inventory.put(1)
                factory.products_completed += 1
                product.end_time = env.now
                factory.cycle_times.append(product.get_cycle_time())
        else:
            factory.quality_failed += 1

        factory.products_in_progress -= 1


def raw_material_supplier(env: simpy.Environment, factory: Factory):
    """Periodically replenishes raw materials"""

    while True:
        yield env.timeout(factory.config['supplier_interval'])

        # Add materials if below threshold
        current_level = factory.raw_material_inventory.level
        capacity = factory.raw_material_inventory.capacity

        if current_level < capacity * 0.5:  # Reorder point at 50%
            amount = min(
                factory.config['supplier_batch_size'],
                capacity - current_level
            )
            yield factory.raw_material_inventory.put(amount)


def machine_maintenance(env: simpy.Environment, factory: Factory, machine_name: str):
    """Simulates random machine breakdowns and maintenance"""

    while True:
        # Random time until next breakdown
        time_to_breakdown = random.uniform(
            factory.config['min_time_to_breakdown'],
            factory.config['max_time_to_breakdown']
        )
        yield env.timeout(time_to_breakdown)

        # Machine breaks down - request it to take it offline
        machine = factory.machines[machine_name]
        with machine.request() as req:
            yield req

            # Maintenance time
            maintenance_time = random.uniform(
                factory.config['min_maintenance_time'],
                factory.config['max_maintenance_time']
            )
            yield env.timeout(maintenance_time)


def metrics_collector(env: simpy.Environment, factory: Factory):
    """Collects metrics at regular intervals for the dashboard"""

    while True:
        factory.record_metrics()
        yield env.timeout(factory.config['metrics_interval'])


def run_simulation(config: dict, duration: float = 100):
    """
    Run the factory simulation

    Args:
        config: Configuration dictionary
        duration: Simulation duration in time units

    Returns:
        SimulationMetrics object
    """

    # Create environment
    env = simpy.Environment()

    # Create factory
    factory = Factory(env, config)

    # Start production lines
    for i in range(config['num_production_lines']):
        env.process(production_line(env, factory, i))

    # Start raw material supplier
    env.process(raw_material_supplier(env, factory))

    # Start machine maintenance processes
    for machine_name in factory.machines.keys():
        env.process(machine_maintenance(env, factory, machine_name))

    # Start metrics collector
    env.process(metrics_collector(env, factory))

    # Run simulation
    env.run(until=duration)

    # Record final metrics
    factory.record_metrics()

    return factory.metrics


# Default configuration
DEFAULT_CONFIG = {
    # Inventory
    'raw_material_capacity': 1000,
    'initial_raw_materials': 500,
    'finished_goods_capacity': 500,

    # Resources
    'num_machines': 5,
    'num_workers': 10,
    'num_production_lines': 8,

    # Production parameters
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


if __name__ == "__main__":
    print("Running Factory Simulation...")
    print("=" * 50)

    metrics = run_simulation(DEFAULT_CONFIG, duration=100)

    print(f"\nSimulation Complete!")
    print(f"Total Products Completed: {metrics.products_completed[-1]}")
    print(f"Quality Passed: {metrics.quality_passed[-1]}")
    print(f"Quality Failed: {metrics.quality_failed[-1]}")
    print(f"Final Raw Materials: {metrics.raw_materials[-1]}")
    print(f"Final Finished Goods: {metrics.finished_goods[-1]}")

    if metrics.average_cycle_time[-1] > 0:
        print(f"Average Cycle Time: {metrics.average_cycle_time[-1]:.2f}")

    print("\nMachine Utilization:")
    for machine_name, util_data in metrics.machine_utilization.items():
        if util_data:
            print(f"  {machine_name}: {util_data[-1]:.2f}%")

    if metrics.worker_utilization:
        print(f"Worker Utilization: {metrics.worker_utilization[-1]:.2f}%")
