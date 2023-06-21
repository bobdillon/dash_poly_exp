import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# Generate x, y data
x = np.linspace(0, 10, 100)
y = np.sin(x)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='3d-plot'),
    dcc.RangeSlider(
        id='depth-slider',
        min=1,
        max=10,
        value=[3, 7],
        step=1,
        marks={i: str(i) for i in range(11)}
    )
])

@app.callback(
    Output('3d-plot', 'figure'),
    Input('depth-slider', 'value')
)
def update_3d_plot(z_range):
    # Generate a 2D array of z-values, repeating the y-values at two different z-positions
    z = np.array([y + z_val for z_val in z_range])

    surface = go.Surface(x=x, y=np.array(z_range), z=z)

    layout = go.Layout(
        scene=dict(
            xaxis=dict(title='X-axis'),
            yaxis=dict(title='Z-axis'),
            zaxis=dict(title='Y-axis'),
        ),
        title='3D surface plot from 2D data'
    )

    return go.Figure(data=[surface], layout=layout)

if __name__ == '__main__':
    app.run_server(debug=True)
