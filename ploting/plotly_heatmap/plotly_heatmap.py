import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import os
from datetime import datetime

# Function to load and aggregate data
def load_and_aggregate_data(file_path, aggregation_factor=32):
    # Load the data
    df = pd.read_csv(file_path)
    
    # Extract frequency and time columns
    frequency = df.iloc[:, 0].values
    time_data = df.iloc[:, 1:].values
    
    # Ensure the data length is compatible with the aggregation factor
    n_rows = time_data.shape[0]
    n_cols = time_data.shape[1]
    trimmed_length = (n_rows // aggregation_factor) * aggregation_factor
    
    trimmed_data = time_data[:trimmed_length, :]
    reshaped_data = trimmed_data.reshape(-1, aggregation_factor, n_cols)
    median_data = np.median(reshaped_data, axis=1)
    
    # Create a new DataFrame with the aggregated data
    aggregated_df = pd.DataFrame(median_data, columns=df.columns[1:])
    aggregated_df.insert(0, 'Frequency (GHz)', frequency[:len(median_data)])
    
    return aggregated_df

# Function to create heatmap
def create_heatmap(df):
    fig = px.imshow(df.iloc[:, 1:], 
                    labels=dict(x="Time", y="Frequency (GHz)", color="Signal Strength"),
                    x=df.columns[1:], 
                    y=df['Frequency (GHz)'],
                    color_continuous_scale='viridis')
    
    # Adjust the layout to make the graph taller
    fig.update_layout(
        title="Heatmap of Signal Strength Over Time",
        height=800
    )
    
    # Reduce the number of time stamps shown on the x-axis
    fig.update_xaxes(nticks=10)
    
    return fig

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.DatePickerSingle(
                id='date-picker',
                min_date_allowed=datetime(2020, 1, 1),
                max_date_allowed=datetime(2024, 12, 31),
                initial_visible_month=datetime(2024, 1, 1),
                date=datetime(2024, 1, 1)
            )
        ], width=4)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='heatmap')
        ], width=12)
    ])
])

@app.callback(
    Output('heatmap', 'figure'),
    Input('date-picker', 'date')
)
def update_heatmap(selected_date):
    if selected_date:
        date_str = selected_date.replace("-", "")
        year = selected_date.split("-")[0]
        file_path = f"/mnt/4tbssd/time_series_matrix_data/sh1/{year}/{date_str}_matrix.csv"
        if os.path.exists(file_path):
            aggregated_data = load_and_aggregate_data(file_path)
            fig = create_heatmap(aggregated_data)
            return fig
    return {}

if __name__ == '__main__':
    app.run_server(debug=True)
