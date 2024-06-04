import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Define the paths
input_csv_path = '/mnt/4tbssd/anritsu/anritsu/20240516_matrix.csv'

# Read the CSV file
data = pd.read_csv(input_csv_path, index_col='Frequency (GHz)')

# Function to convert timestamps to hours since midnight
def hours_since_midnight(s):
    return (pd.to_datetime(s).hour + pd.to_datetime(s).minute / 60 + pd.to_datetime(s).second / 3600)

# Convert the column headers (timestamps) to hours since midnight
time_stamps = [hours_since_midnight(ts) for ts in data.columns]

# Create meshgrid for frequencies and times
F, T = np.meshgrid(data.index, time_stamps)

# Transpose the data to align with the meshgrid
power_readings = data.values.T

# Determine the range of your data for contour levels
levels = np.linspace(-110, -20, 25)  # Adjust number of levels as needed

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("20240516_anritsu"), className="text-center my-3")),
    dbc.Row(dbc.Col(dcc.Graph(id='contour-plot', style={'height': '80vh'}))),
    dcc.Interval(
        id='interval-component',
        interval=60*60*1000,  # in milliseconds (1 hour)
        n_intervals=0
    )
])

@app.callback(
    dash.dependencies.Output('contour-plot', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    fig = go.Figure(data=go.Contour(
        z=power_readings,
        x=data.index,
        y=time_stamps,
        colorscale='Cividis',
        contours=dict(
            start=-110,
            end=-20,
            size=3
        )
    ))
    
    fig.update_layout(
        title='20240516_anritsu',
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

