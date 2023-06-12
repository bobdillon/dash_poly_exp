import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Generate random data
np.random.seed(42)
n_points = 100
x = np.random.uniform(low=-10, high=10, size=n_points)
y = np.random.uniform(low=-10, high=10, size=n_points)
z = np.random.uniform(low=-10, high=10, size=n_points)

# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='scatter-plot'),
    dcc.Slider(
        id='z-slider',
        min=min(z),
        max=max(z),
        step=0.1,
        value=0,
        marks={str(z_val): str(z_val) for z_val in z}
    ),
    html.Div(id='selected-points')
])

@app.callback(
    Output('selected-points', 'children'),
    Input('z-slider', 'value')
)
def update_selected_points(z_value):
    selected_indices = np.where(np.isclose(z, z_value))[0]
    selected_points = [(x[i], y[i], z[i]) for i in selected_indices]
    return html.Pre('\n'.join([f'({point[0]:.2f}, {point[1]:.2f}, {point[2]:.2f})' for point in selected_points]))

@app.callback(
    Output('scatter-plot', 'figure'),
    Input('z-slider', 'value')
)
def update_scatter_plot(z_value):
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=4,
            color=z,
            colorscale='Viridis',
            opacity=0.8
        )
    ))
    fig.update_layout(scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ))
    fig.update_layout(height=600)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
