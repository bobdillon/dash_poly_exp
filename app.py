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
    html.Div(id='selected-data-table-container'),
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
    [Output('selected-data-table-container', 'children'),
     Output('error-message', 'children')],
    [Input('print-button', 'n_clicks')],
    [State('scatter-plot-1', 'selectedData'),
     State('scatter-plot-2', 'selectedData')]
)
def update_selected_data_table(print_clicks, selected_data_1, selected_data_2):
    if print_clicks % 2 == 1:
        data_1 = pd.DataFrame(selected_data_1['points']) if selected_data_1 else pd.DataFrame()
        data_2 = pd.DataFrame(selected_data_2['points']) if selected_data_2 else pd.DataFrame()
        
        if not data_1.empty and not data_2.empty:
            selected_data = pd.concat([data_1, data_2])
            table = dash_table.DataTable(
                data=selected_data.to_dict('records'),
                columns=[{'name': col, 'id': col} for col in selected_data.columns],
                style_table={'maxHeight': '300px', 'overflowY': 'scroll'},
                style_cell={'textAlign': 'center'},
                selected_rows=[],
                editable=False
            )
            error_message = None
        else:
            table = None
            error_message = 'No data selected.'
        
        return table, error_message
    
    return None, None

@app.callback(
    Output('mesh-plot', 'figure'),
    [Input('generate-button', 'n_clicks')],
    [State('scatter-plot-1', 'selectedData'),
     State('scatter-plot-2', 'selectedData'),
     State('3d-graph', 'figure')]
)
def generate_polygon(generate_clicks, selected_data_1, selected_data_2, fig_3d):
    if generate_clicks % 2 == 1:
        data_1 = pd.DataFrame(selected_data_1['points']) if selected_data_1 else pd.DataFrame()
        data_2 = pd.DataFrame(selected_data_2['points']) if selected_data_2 else pd.DataFrame()

        if not data_1.empty and not data_2.empty:
            fig_mesh = go.Figure(data=fig_3d['data']) if fig_3d else go.Figure()
            try:
                fig_mesh.add_trace(go.Mesh3d(x=pd.concat([data_1['x'], data_2['x']]), y=pd.concat([data_1['y'], data_2['y']]), z=pd.concat([data_1['customdata'], data_2['customdata']]), color='purple', opacity=0.5, name='Polygon'))
            except Exception as e:
                fig_mesh = go.Figure()
                error_message = f"Error generating polygon: {e}"
            else:
                error_message = None
        else:
            fig_mesh = go.Figure()
            error_message = 'No data selected.'
        
        return fig_mesh

    return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
