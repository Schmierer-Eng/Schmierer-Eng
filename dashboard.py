"""
Interactive Dashboard for Factory Simulation
Uses Dash and Plotly for real-time visualization
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import threading
import time
from factory_simulation import run_simulation, DEFAULT_CONFIG
import copy

# Global variable to store simulation results
simulation_data = None
simulation_lock = threading.Lock()
simulation_thread = None
simulation_running = False


def run_simulation_thread(config, duration):
    """Run simulation in a separate thread"""
    global simulation_data, simulation_running

    simulation_running = True
    metrics = run_simulation(config, duration)

    with simulation_lock:
        simulation_data = metrics.to_dict()

    simulation_running = False


# Initialize the Dash app
app = dash.Dash(__name__, update_title=None)
app.title = "Factory Simulation Dashboard"

# Define the layout
app.layout = html.Div([
    html.Div([
        html.H1("🏭 Factory Simulation Dashboard",
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Real-time monitoring of SimPy factory simulation",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '30px'})
    ]),

    # Control Panel
    html.Div([
        html.Div([
            html.Label("Simulation Duration:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(id='duration-input', type='number', value=100, min=10, max=1000, step=10,
                      style={'marginRight': '20px', 'padding': '5px'}),

            html.Label("Production Lines:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(id='production-lines-input', type='number', value=8, min=1, max=20, step=1,
                      style={'marginRight': '20px', 'padding': '5px'}),

            html.Label("Machines:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(id='machines-input', type='number', value=5, min=1, max=10, step=1,
                      style={'marginRight': '20px', 'padding': '5px'}),

            html.Label("Workers:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Input(id='workers-input', type='number', value=10, min=1, max=50, step=1,
                      style={'marginRight': '20px', 'padding': '5px'}),

            html.Button('Start Simulation', id='start-button', n_clicks=0,
                        style={'backgroundColor': '#27ae60', 'color': 'white', 'padding': '10px 20px',
                               'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer',
                               'fontWeight': 'bold'})
        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center',
                  'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px',
                  'marginBottom': '20px'})
    ]),

    # Status indicator
    html.Div(id='status-indicator', style={'textAlign': 'center', 'marginBottom': '20px',
                                            'fontSize': '16px', 'fontWeight': 'bold'}),

    # Key Metrics Cards
    html.Div([
        html.Div([
            html.H3(id='products-completed', children='0', style={'color': '#27ae60', 'fontSize': '36px', 'margin': '0'}),
            html.P('Products Completed', style={'color': '#7f8c8d', 'margin': '5px'})
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '10px',
                  'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'}),

        html.Div([
            html.H3(id='quality-rate', children='0%', style={'color': '#3498db', 'fontSize': '36px', 'margin': '0'}),
            html.P('Quality Pass Rate', style={'color': '#7f8c8d', 'margin': '5px'})
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '10px',
                  'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'}),

        html.Div([
            html.H3(id='avg-cycle-time', children='0', style={'color': '#e74c3c', 'fontSize': '36px', 'margin': '0'}),
            html.P('Avg Cycle Time', style={'color': '#7f8c8d', 'margin': '5px'})
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '10px',
                  'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'}),

        html.Div([
            html.H3(id='worker-utilization', children='0%', style={'color': '#f39c12', 'fontSize': '36px', 'margin': '0'}),
            html.P('Worker Utilization', style={'color': '#7f8c8d', 'margin': '5px'})
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '10px',
                  'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

    # Main Charts
    html.Div([
        # Production Over Time
        html.Div([
            dcc.Graph(id='production-chart')
        ], style={'flex': '1', 'margin': '10px'}),

        # Inventory Levels
        html.Div([
            dcc.Graph(id='inventory-chart')
        ], style={'flex': '1', 'margin': '10px'})
    ], style={'display': 'flex'}),

    html.Div([
        # Quality Chart
        html.Div([
            dcc.Graph(id='quality-chart')
        ], style={'flex': '1', 'margin': '10px'}),

        # Machine Utilization
        html.Div([
            dcc.Graph(id='machine-utilization-chart')
        ], style={'flex': '1', 'margin': '10px'})
    ], style={'display': 'flex'}),

    # Update interval
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every 1 second
        n_intervals=0
    ),

    # Store for simulation data
    dcc.Store(id='simulation-store')

], style={'padding': '20px', 'backgroundColor': '#f5f6fa', 'fontFamily': 'Arial, sans-serif'})


@app.callback(
    Output('status-indicator', 'children'),
    Output('status-indicator', 'style'),
    Input('start-button', 'n_clicks'),
    Input('interval-component', 'n_intervals'),
    State('duration-input', 'value'),
    State('production-lines-input', 'value'),
    State('machines-input', 'value'),
    State('workers-input', 'value')
)
def start_simulation(n_clicks, n_intervals, duration, prod_lines, machines, workers):
    """Start simulation when button is clicked"""
    global simulation_thread, simulation_running

    ctx = dash.callback_context
    if not ctx.triggered:
        return "Ready to start simulation", {'textAlign': 'center', 'marginBottom': '20px',
                                               'fontSize': '16px', 'fontWeight': 'bold', 'color': '#7f8c8d'}

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'start-button' and n_clicks > 0:
        if not simulation_running:
            # Create custom config
            config = copy.deepcopy(DEFAULT_CONFIG)
            config['num_production_lines'] = prod_lines
            config['num_machines'] = machines
            config['num_workers'] = workers

            # Start simulation in a thread
            simulation_thread = threading.Thread(
                target=run_simulation_thread,
                args=(config, duration)
            )
            simulation_thread.start()

            return "Simulation Running...", {'textAlign': 'center', 'marginBottom': '20px',
                                              'fontSize': '16px', 'fontWeight': 'bold', 'color': '#27ae60'}

    if simulation_running:
        return "Simulation Running...", {'textAlign': 'center', 'marginBottom': '20px',
                                          'fontSize': '16px', 'fontWeight': 'bold', 'color': '#27ae60'}
    elif simulation_data is not None:
        return "Simulation Complete", {'textAlign': 'center', 'marginBottom': '20px',
                                        'fontSize': '16px', 'fontWeight': 'bold', 'color': '#3498db'}
    else:
        return "Ready to start simulation", {'textAlign': 'center', 'marginBottom': '20px',
                                               'fontSize': '16px', 'fontWeight': 'bold', 'color': '#7f8c8d'}


@app.callback(
    Output('production-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_production_chart(n):
    """Update production over time chart"""
    with simulation_lock:
        data = simulation_data

    if data is None or not data['time']:
        # Empty chart
        return {
            'data': [],
            'layout': go.Layout(
                title='Production Over Time',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Count'},
                hovermode='closest'
            )
        }

    traces = [
        go.Scatter(
            x=data['time'],
            y=data['products_completed'],
            mode='lines+markers',
            name='Completed',
            line={'color': '#27ae60', 'width': 2}
        ),
        go.Scatter(
            x=data['time'],
            y=data['products_in_progress'],
            mode='lines+markers',
            name='In Progress',
            line={'color': '#f39c12', 'width': 2}
        )
    ]

    layout = go.Layout(
        title='Production Over Time',
        xaxis={'title': 'Simulation Time'},
        yaxis={'title': 'Number of Products'},
        hovermode='closest',
        plot_bgcolor='#fff',
        paper_bgcolor='#fff'
    )

    return {'data': traces, 'layout': layout}


@app.callback(
    Output('inventory-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_inventory_chart(n):
    """Update inventory levels chart"""
    with simulation_lock:
        data = simulation_data

    if data is None or not data['time']:
        return {
            'data': [],
            'layout': go.Layout(
                title='Inventory Levels',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Units'}
            )
        }

    traces = [
        go.Scatter(
            x=data['time'],
            y=data['raw_materials'],
            mode='lines+markers',
            name='Raw Materials',
            line={'color': '#3498db', 'width': 2},
            fill='tozeroy'
        ),
        go.Scatter(
            x=data['time'],
            y=data['finished_goods'],
            mode='lines+markers',
            name='Finished Goods',
            line={'color': '#9b59b6', 'width': 2},
            fill='tozeroy'
        )
    ]

    layout = go.Layout(
        title='Inventory Levels',
        xaxis={'title': 'Simulation Time'},
        yaxis={'title': 'Units in Inventory'},
        hovermode='closest',
        plot_bgcolor='#fff',
        paper_bgcolor='#fff'
    )

    return {'data': traces, 'layout': layout}


@app.callback(
    Output('quality-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_quality_chart(n):
    """Update quality control chart"""
    with simulation_lock:
        data = simulation_data

    if data is None or not data['time']:
        return {
            'data': [],
            'layout': go.Layout(
                title='Quality Control',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Count'}
            )
        }

    traces = [
        go.Scatter(
            x=data['time'],
            y=data['quality_passed'],
            mode='lines+markers',
            name='Passed',
            line={'color': '#27ae60', 'width': 2}
        ),
        go.Scatter(
            x=data['time'],
            y=data['quality_failed'],
            mode='lines+markers',
            name='Failed',
            line={'color': '#e74c3c', 'width': 2}
        )
    ]

    layout = go.Layout(
        title='Quality Control',
        xaxis={'title': 'Simulation Time'},
        yaxis={'title': 'Product Count'},
        hovermode='closest',
        plot_bgcolor='#fff',
        paper_bgcolor='#fff'
    )

    return {'data': traces, 'layout': layout}


@app.callback(
    Output('machine-utilization-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_machine_utilization(n):
    """Update machine utilization chart"""
    with simulation_lock:
        data = simulation_data

    if data is None or not data.get('machine_utilization'):
        return {
            'data': [],
            'layout': go.Layout(
                title='Machine Utilization',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Utilization (%)'}
            )
        }

    traces = []
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']

    for idx, (machine_name, utilization_data) in enumerate(data['machine_utilization'].items()):
        traces.append(
            go.Scatter(
                x=data['time'][:len(utilization_data)],
                y=utilization_data,
                mode='lines',
                name=machine_name,
                line={'color': colors[idx % len(colors)], 'width': 2}
            )
        )

    layout = go.Layout(
        title='Machine Utilization Over Time',
        xaxis={'title': 'Simulation Time'},
        yaxis={'title': 'Utilization (%)', 'range': [0, 100]},
        hovermode='closest',
        plot_bgcolor='#fff',
        paper_bgcolor='#fff'
    )

    return {'data': traces, 'layout': layout}


@app.callback(
    Output('products-completed', 'children'),
    Output('quality-rate', 'children'),
    Output('avg-cycle-time', 'children'),
    Output('worker-utilization', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    """Update key metric cards"""
    with simulation_lock:
        data = simulation_data

    if data is None or not data['time']:
        return '0', '0%', '0', '0%'

    # Products completed
    products = data['products_completed'][-1] if data['products_completed'] else 0

    # Quality rate
    passed = data['quality_passed'][-1] if data['quality_passed'] else 0
    failed = data['quality_failed'][-1] if data['quality_failed'] else 0
    total_checked = passed + failed
    quality_rate = (passed / total_checked * 100) if total_checked > 0 else 0

    # Average cycle time
    avg_cycle = data['average_cycle_time'][-1] if data['average_cycle_time'] else 0

    # Worker utilization
    worker_util = data['worker_utilization'][-1] if data['worker_utilization'] else 0

    return (
        f"{products:,}",
        f"{quality_rate:.1f}%",
        f"{avg_cycle:.2f}",
        f"{worker_util:.1f}%"
    )


if __name__ == '__main__':
    print("Starting Factory Simulation Dashboard...")
    print("Open your browser to http://127.0.0.1:8050")
    print("=" * 50)
    app.run_server(debug=True, host='0.0.0.0', port=8050)
