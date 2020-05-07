import dash
import dash_html_components as html
import dash_core_components as dcc
import scipy.stats
import numpy as np
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Slider(
        id='mu',
        min=-3,
        max=3,
        step=0.2,
        value=1.2,
    ),
    dcc.Slider(
        id='sig',
        min=0,
        max=4,
        step=0.5,
        value=2,
    ),
    dcc.Graph(id='gra')
])


@app.callback(
    Output('gra', 'figure'),
    [Input('mu', 'value'),Input('sig','value')]
    )
def update_figure(mu,sig):
    x = np.linspace(-10,10,100)
    y = scipy.stats.norm(mu,sig).pdf(x)
    title = "Mu is " + str(mu) + " and sigma is " + str(sig)
    return {
            'data': [
                {'x': x, 'y': y, 'type': 'line'},
            ],
            'layout': {
                'title': title
            }
            }

if __name__ == '__main__':
    app.run_server(debug=True)