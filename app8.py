import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from sklearn.datasets import make_blobs
import numpy as np
import dash_table


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Label('Seed:'),
        dcc.Input(id='seed-input', type='number', value=0)
    ]),
    html.Div([
        html.Label('Plane:'),
        dcc.Dropdown(
            id='plane-dropdown',
            options=[{'label': i, 'value': i} for i in ['XY', 'XZ', 'YZ']],
            value='XY'
        )
    ]),
    dcc.Graph(id='3d-graph'),
    dcc.Graph(id='scatter-plot-1'),
    dcc.Graph(id='scatter-plot-2'),
    html.Button('Toggle Selected Data', id='print-button', n_clicks=0),
    html.Button('Generate Polygon', id='generate-button', n_clicks=0),
    html.Div(id='selected-data'),
    dcc.Graph(id='mesh-plot'),
    html.Div(id='error-message')
])

@app.callback(
    [Output('3d-graph', 'figure'),
     Output('scatter-plot-1', 'figure'),
     Output('scatter-plot-2', 'figure')],
    [Input('seed-input', 'value'),
     Input('plane-dropdown', 'value')]
)
def update_graphs(seed, plane):
    np.random.seed(seed)
    outer_blob, _ = make_blobs(n_samples=500, centers=[(0,0,0)], n_features=3, random_state=seed)
    inner_blob, _ = make_blobs(n_samples=500, centers=[(0,0,0)], n_features=3, cluster_std=0.5, random_state=seed)

    fig_3d = go.Figure(data=[go.Scatter3d(x=outer_blob[:, 0], y=outer_blob[:, 1], z=outer_blob[:, 2], mode='markers', marker=dict(color='red'), name='Outer'),
                             go.Scatter3d(x=inner_blob[:, 0], y=inner_blob[:, 1], z=inner_blob[:, 2], mode='markers', marker=dict(color='blue'), name='Inner')])

    planes = {'XY': (0, 1), 'XZ': (0, 2), 'YZ': (1, 2)}
    x_axis, y_axis = planes[plane]
    z_axis = 3 - x_axis - y_axis  # the remaining axis

    fig_scatter_1 = go.Figure(data=[go.Scatter(x=outer_blob[:, x_axis], y=outer_blob[:, y_axis], mode='markers', marker=dict(color='red'), name='Outer', customdata=outer_blob[:, z_axis], hovertemplate='%{customdata}', selectedpoints=[], unselected={'marker': {'opacity': 0.3}}),
                                    go.Scatter(x=inner_blob[:, x_axis], y=inner_blob[:, y_axis], mode='markers', marker=dict(color='blue'), name='Inner', customdata=inner_blob[:, z_axis], hovertemplate='%{customdata}', selectedpoints=[], unselected={'marker': {'opacity': 0.3}})])

    fig_scatter_2 = go.Figure(data=[go.Scatter(x=outer_blob[:250, x_axis], y=outer_blob[:250, y_axis], mode='markers', marker=dict(color='red'), name='Outer', customdata=outer_blob[:250, z_axis], hovertemplate='%{customdata}', selectedpoints=[], unselected={'marker': {'opacity': 0.3}}),
                                    go.Scatter(x=inner_blob[:250, x_axis], y=inner_blob[:250, y_axis], mode='markers', marker=dict(color='blue'), name='Inner', customdata=inner_blob[:250, z_axis], hovertemplate='%{customdata}', selectedpoints=[], unselected={'marker': {'opacity': 0.3}})])

    return fig_3d, fig_scatter_1, fig_scatter_2

@app.callback(
    [Output('selected-data', 'children'),
     Output('mesh-plot', 'figure'),
     Output('error-message', 'children')],
    [Input('print-button', 'n_clicks'),
     Input('generate-button', 'n_clicks')],
    [State('scatter-plot-1', 'selectedData'),
     State('scatter-plot-2', 'selectedData'),
     State('3d-graph', 'figure')]
)
def handle_button_clicks(print_clicks, generate_clicks, selected_data_1, selected_data_2, fig_3d):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    fig_mesh = go.Figure(data=fig_3d['data']) if fig_3d else go.Figure()

    data_1 = pd.DataFrame(selected_data_1['points']) if selected_data_1 else pd.DataFrame()
    data_2 = pd.DataFrame(selected_data_2['points']) if selected_data_2 else pd.DataFrame()

    if trigger_id == 'print-button':
        data_display = 'No data selected.'
        error_message = None
    elif trigger_id == 'generate-button':
        if not data_1.empty and not data_2.empty:
            try:
                fig_mesh.add_trace(go.Mesh3d(x=pd.concat([data_1['x'], data_2['x']]), y=pd.concat([data_1['y'], data_2['y']]), z=pd.concat([data_1['customdata'], data_2['customdata']]), color='purple', opacity=0.5, name='Polygon'))
                data_display = 'Polygon generated successfully.'
                error_message = None
            except Exception as e:
                data_display = 'No data selected.'
                error_message = f"Error generating polygon: {e}"
        else:
            data_display = 'No data selected.'
            error_message = None
    else:
        data_display = 'No data selected.'
        error_message = None

    return data_display, fig_mesh, error_message

if __name__ == '__main__':
    app.run_server(debug=True)
