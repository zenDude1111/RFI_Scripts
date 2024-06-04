import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Define the paths
input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh1/2021/20210101_matrix.csv'

# Read the CSV file
data = pd.read_csv(input_csv_path, index_col='Frequency (GHz)')

# Function to convert timestamps to hours since midnight
def hours_since_midnight(s):
    return (pd.to_datetime(s).hour + pd.to_datetime(s).minute / 60 + pd.to_datetime(s).second / 3600)

# Convert the column headers (timestamps) to hours since midnight
time_stamps = [hours_since_midnight(ts) for ts in data.columns]

# Bin the frequency channels into smaller ranges
bin_size = 250  # Number of frequency channels per bin
num_bins = int(np.ceil(len(data.index) / bin_size))
bins = [data.index[i*bin_size:(i+1)*bin_size] for i in range(num_bins)]

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("20240516_anritsu"), className="text-center my-3")),
    dbc.Row(dbc.Col(dcc.Dropdown(
        id='bin-selector',
        options=[{'label': f'Bin {i+1}', 'value': i} for i in range(num_bins)],
        value=0,
        clearable=False
    ))),
    dbc.Row(dbc.Col(dcc.Graph(id='contour-plot', style={'height': '80vh'}))),
    dcc.Interval(
        id='interval-component',
        interval=60*60*1000,  # in milliseconds (1 hour)
        n_intervals=0
    )
])

@app.callback(
    dash.dependencies.Output('contour-plot', 'figure'),
    [dash.dependencies.Input('bin-selector', 'value'),
     dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_graph(selected_bin, n):
    bin_range = bins[selected_bin]
    
    # Create meshgrid for the current bin
    F, T = np.meshgrid(bin_range, time_stamps)
    power_readings = data.loc[bin_range].values.T
    
    # Create the contour plot for the current bin
    fig = go.Figure(data=go.Contour(
        z=power_readings,
        x=bin_range,
        y=time_stamps,
        colorscale='Cividis',
        contours=dict(
            start=-110,
            end=-20,
            size=3
        )
    ))
    
    fig.update_layout(
        title=f'20240516_anritsu Bin {selected_bin+1}',
        xaxis_title='Frequency (GHz)',
        yaxis_title='Time since midnight (hours)',
        height=800,  # Adjust the height here as needed
        coloraxis_colorbar=dict(
            title='Power (dBm)'
        )
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

