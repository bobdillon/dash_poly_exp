import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

# initialize the Dash app
app = dash.Dash(__name__)

# Sample 3D data
N = 100
x, y, z = np.random.rand(3, N)
df_3d = pd.DataFrame({"x": x, "y": y, "z": z})

# Define the layout
app.layout = html.Div([
    html.H1("3D Data Viewer"),
    dcc.Graph(id='3d-plot'),
    html.Label('Select Z-coordinate for 2D slice 1:'),
    dcc.Slider(id='z-slider-1', min=min(z), max=max(z), step=0.1, value=min(z)),
    html.Label('Select Z-coordinate for 2D slice 2:'),
    dcc.Slider(id='z-slider-2', min=min(z), max=max(z), step=0.1, value=min(z) + 0.5),
    dcc.Graph(id='2d-plot-1'),
    dcc.Graph(id='2d-plot-2'),
    dcc.Graph(id='2d-overlay-plot')
])

@app.callback(
    Output('3d-plot', 'figure'),
    [Input('z-slider-1', 'value'),
    Input('z-slider-2', 'value')]
)
def update_3d_plot(z_value1, z_value2):
    fig = go.Figure(data=[go.Scatter3d(x=df_3d['x'], 
                                       y=df_3d['y'], 
                                       z=df_3d['z'], 
                                       mode='markers')])
    fig.update_layout(scene_aspectmode='cube')
    return fig

@app.callback(
    Output('2d-plot-1', 'figure'),
    [Input('z-slider-1', 'value')]
)
def update_2d_slice_1(z_value):
    df_2d = df_3d[df_3d['z'] < z_value]
    if df_2d.empty:
        fig = go.Figure()
    else:
        fig = px.scatter(df_2d, x="x", y="y")
    return fig

@app.callback(
    Output('2d-plot-2', 'figure'),
    [Input('z-slider-2', 'value')]
)
def update_2d_slice_2(z_value):
    df_2d = df_3d[df_3d['z'] < z_value]
    if df_2d.empty:
        fig = go.Figure()
    else:
        fig = px.scatter(df_2d, x="x", y="y")
    return fig

@app.callback(
    Output('2d-overlay-plot', 'figure'),
    [Input('2d-plot-1', 'selectedData'),
     Input('2d-plot-2', 'selectedData'),
     Input('z-slider-1', 'value'),
     Input('z-slider-2', 'value')]
)
def update_2d_overlay_plot(selectedData1, selectedData2, z_value_1, z_value_2):
    # create empty figure
    fig = go.Figure()
    fig.update_layout(scene_aspectmode='cube')

    xmin, xmax = df_3d['x'].min(), df_3d['x'].max()
    ymin, ymax = df_3d['y'].min(), df_3d['y'].max()

    for z_value in [z_value_1, z_value_2]:
        # Add bounding box
        fig.add_trace(go.Scatter3d(x=[xmin, xmax, xmax, xmin, xmin],
                                   y=[ymin, ymin, ymax, ymax, ymin],
                                   z=[z_value]*5,
                                   mode='lines',
                                   line=dict(color='black')))

        # add 2D slices to the figure
        for selectedData, color in zip([selectedData1, selectedData2], ['red', 'blue']):
            if selectedData is not None:
                df_selected = pd.DataFrame(selectedData['points'])
                fig.add_trace(go.Scatter3d(x=df_selected['x'],
                                           y=df_selected['y'],
                                           z=[z_value]*len(df_selected),
                                           mode='markers',
                                           marker=dict(size=3, color=color)))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
