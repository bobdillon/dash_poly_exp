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
        html.Label('Slice Axis:'),
        dcc.Dropdown(
            id='axis-dropdown',
            options=[{'label': i, 'value': i} for i in ['x', 'y', 'z']],
            value='z'
        )
    ]),
    dcc.Graph(id='3d-graph'),
    dcc.Graph(id='scatter-plot-1'),
    dcc.Graph(id='scatter-plot-2'),
    html.Button('Toggle Selected Data', id='print-button', n_clicks=0),
    html.Div(id='selected-data-table-container'),
    dcc.Graph(id='3d-graph-slices'),
    html.Div(id='error-message')
])

@app.callback(
    [Output('3d-graph', 'figure'),
     Output('scatter-plot-1', 'figure'),
     Output('scatter-plot-2', 'figure'),
     Output('3d-graph-slices', 'figure'),
     Output('error-message', 'children')],
    [Input('seed-input', 'value'),
     Input('axis-dropdown', 'value'),
     Input('print-button', 'n_clicks')],
    [State('scatter-plot-1', 'selectedData'),
     State('scatter-plot-2', 'selectedData')]
)
def update_graphs(seed, axis, n_clicks, selected_data_1, selected_data_2):
    try:
        np.random.seed(seed)
        outer_blob, _ = make_blobs(n_samples=500, centers=[(0,0,0)], n_features=3, random_state=seed)
        inner_blob, _ = make_blobs(n_samples=500, centers=[(0,0,0)], n_features=3, cluster_std=0.5, random_state=seed)

        fig_3d = go.Figure(data=[go.Scatter3d(x=outer_blob[:, 0], y=outer_blob[:, 1], z=outer_blob[:, 2], mode='markers', marker=dict(color='red'), name='Outer'),
                                 go.Scatter3d(x=inner_blob[:, 0], y=inner_blob[:, 1], z=inner_blob[:, 2], mode='markers', marker=dict(color='blue'), name='Inner')])

        fig_3d_slices = go.Figure(data=[go.Scatter3d(x=outer_blob[:, 0], y=outer_blob[:, 1], z=outer_blob[:, 2], mode='markers', marker=dict(color='red'), name='Outer'),
                                        go.Scatter3d(x=inner_blob[:, 0], y=inner_blob[:, 1], z=inner_blob[:, 2], mode='markers', marker=dict(color='blue'), name='Inner')])

        if axis == 'x':
            fig_scatter_1, fig_scatter_2 = update_scatter_plots(outer_blob, inner_blob, 1, 2, 0)
        elif axis == 'y':
            fig_scatter_1, fig_scatter_2 = update_scatter_plots(outer_blob, inner_blob, 0, 2, 1)
        else:
            fig_scatter_1, fig_scatter_2 = update_scatter_plots(outer_blob, inner_blob, 0, 1, 2)

        fig_3d.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))

        if n_clicks % 2 == 1 and selected_data_1 and selected_data_2:
            data_1 = pd.DataFrame(selected_data_1['points'])
            data_2 = pd.DataFrame(selected_data_2['points'])
            fig_3d_slices.add_trace(go.Scatter3d(x=data_1['x'], y=data_1['y'], z=[0]*len(data_1), mode='markers', marker=dict(color='green', size=5, line=dict(color='black', width=2)), name='Selected 1'))
            fig_3d_slices.add_trace(go.Scatter3d(x=data_2['x'], y=data_2['y'], z=[0]*len(data_2), mode='markers', marker=dict(color='purple', size=5, line=dict(color='black', width=2)), name='Selected 2'))

        fig_3d_slices.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))

        return fig_3d, fig_scatter_1, fig_scatter_2, fig_3d_slices, ""

    except Exception as e:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure(), f"An error occurred: {e}"

def update_scatter_plots(outer_blob, inner_blob, axis1, axis2, unused_axis):
    fig_scatter_1 = generate_scatter_plot(outer_blob, inner_blob, axis1, axis2, unused_axis)
    fig_scatter_2 = generate_scatter_plot(outer_blob, inner_blob, axis1, unused_axis, unused_axis)

    return fig_scatter_1, fig_scatter_2

def generate_scatter_plot(outer_blob, inner_blob, x_axis, y_axis, unused_axis):
    z_values_outter = outer_blob[:, unused_axis]
    z_values_inner = inner_blob[:, unused_axis]
    fig_scatter = go.Figure(data=[go.Scatter(x=outer_blob[:, x_axis], y=outer_blob[:, y_axis], mode='markers', marker=dict(color='red'), name='Outer'),
                                  go.Scatter(x=inner_blob[:, x_axis], y=inner_blob[:, y_axis], mode='markers', marker=dict(color='blue'), name='Inner')])
    if x_axis==0:
        x_axis='X'
    elif x_axis==1:
        x_axis='Y'
    else:
        x_axis='Z'
        
    if y_axis==0:
        y_axis='X'
    elif y_axis==1:
        y_axis='Y'
    else:
        y_axis='Z'
    
    fig_scatter.update_layout(xaxis_title=f'{x_axis} Axis', yaxis_title=f'{y_axis} Axis')

    return fig_scatter

@app.callback(
    Output('selected-data-table-container', 'children'),
    [Input('print-button', 'n_clicks')],
    [State('scatter-plot-1', 'selectedData'),
     State('scatter-plot-2', 'selectedData')]
)
def update_selected_data_table(n_clicks, selected_data_1, selected_data_2):
    if n_clicks % 2 == 1 and selected_data_1 and selected_data_2:
        data_1 = pd.DataFrame(selected_data_1['points'])
        data_2 = pd.DataFrame(selected_data_2['points'])
        selected_data = pd.concat([data_1, data_2])
        table = dash_table.DataTable(
            data=selected_data.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in selected_data.columns]
        )
        return table
    else:
        return ""

if __name__ == '__main__':
    app.run_server(debug=True)
