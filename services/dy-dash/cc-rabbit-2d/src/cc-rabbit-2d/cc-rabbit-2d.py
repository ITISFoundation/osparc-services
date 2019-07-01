# -*- coding: utf-8 -*-
import os
from pathlib import Path
import asyncio

import numpy as np
import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
from plotly import tools


DEVEL_MODE = False
if DEVEL_MODE:
    WORKDIR = Path(Path(os.path.dirname(os.path.realpath(__file__))).parent).parent
else:
    WORKDIR = Path('/home/jovyan')
INPUT_DIR = WORKDIR / 'input'


base_pathname = os.environ.get('SIMCORE_NODE_BASEPATH', "/")
if not base_pathname.endswith("/"):
    base_pathname = base_pathname + "/"
if not base_pathname.startswith("/"):
    base_pathname = "/" + base_pathname
print('url_base_pathname', base_pathname)

server = flask.Flask(__name__)
app = dash.Dash(__name__,
    server=server,
    url_base_pathname=base_pathname
)
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


osparc_style = {
    'color': '#bfbfbf',
    'backgroundColor': '#202020',
    'gridColor': '#444',
}
dcc_input = {
    'color': osparc_style['color'],
    'backgroundColor': osparc_style['gridColor']
}
dcc_input_button = {
    'height': '40px',
    'width': '100%',
    'color': dcc_input['color'],
    'backgroundColor': dcc_input['backgroundColor']
}

GRAPH_HEIGHT = 400

def give_fig_osparc_style2(fig):
    margin = 10
    y_label_padding = 50
    x_label_padding = 30
    fig['layout']['margin'].update(
        l=margin+y_label_padding,
        r=margin,
        b=margin+x_label_padding,
        t=margin,
    )

    fig['layout'].update(
        autosize=True,
        height=GRAPH_HEIGHT,
        showlegend=False,
        plot_bgcolor=osparc_style['backgroundColor'],
        paper_bgcolor=osparc_style['backgroundColor'],
        font=dict(
            color=osparc_style['color']
        )
    )
    return fig

def give_fig_osparc_style(fig, xLabels=['x'], yLabels=['y']):
    for idx, xLabel in enumerate(xLabels):
        suffix = str(idx)
        if idx is 0:
            suffix = ''
        fig['layout']['xaxis'+suffix].update(
            title=xLabel,
            gridcolor=osparc_style['gridColor']
        )
    for idx, yLabel in enumerate(yLabels):
        suffix = str(idx)
        if idx is 0:
            suffix = ''
        fig['layout']['yaxis'+suffix].update(
            title=yLabel,
            gridcolor=osparc_style['gridColor']
        )
    fig = give_fig_osparc_style2(fig)
    return fig

def get_empty_graph(xLabel='x', yLabel='y'):
    fig = go.Figure(data=[], layout={})
    fig = give_fig_osparc_style(fig, [xLabel], [yLabel])
    return fig


empty_graph_1 = get_empty_graph()

app.layout = html.Div(children=[
    html.Button('Reload', id='reload-button', style=dcc_input_button),
    dcc.Graph(id='graph-1', figure=empty_graph_1)
], style=osparc_style)


def create_graph(data_frame, title=None, x_axis_title=None, y_axis_title=None):
    data = [
            go.Scatter(
                x=data_frame[data_frame.columns[0]],
                y=data_frame[data_frame.columns[i]],
                name=str(data_frame.columns[i])
            )
            for i in range(1,data_frame.columns.size)
    ]

    fig = get_empty_graph(x_axis_title, y_axis_title)
    layout = go.Layout(fig['layout'])
    fig = go.Figure(data=data, layout=layout)
    return fig

def plot_ECG():
    # data_path_a = await PORTS.inputs[0].get()
    data_path_a = INPUT_DIR / 'ECGs.txt'
    data_frame_a = pd.read_csv(data_path_a, sep="\t", header=None)

    axis_colums = [0,1]
    plot_1 = data_frame_a.filter(items=[data_frame_a.columns[i] for i in axis_colums])
    fig = create_graph(data_frame=plot_1, x_axis_title='Time (sec)', y_axis_title='ECGs')
    return fig

# When pressing 'Load' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
    [
        Output('graph-1', 'figure')
    ],
    [
        Input('reload-button', 'n_clicks')
    ]
)
def read_input_files(_n_clicks):
    figs = [
        plot_ECG()
    ]
    return figs


class AnyThreadEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """Event loop policy that allows loop creation on any thread."""

    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        try:
            return super().get_event_loop()
        except (RuntimeError, AssertionError):
            # "There is no current event loop in thread %r"
            loop = self.new_event_loop()
            self.set_event_loop(loop)
            return loop

if __name__ == '__main__':
    # the following line is needed for async calls
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    app.run_server(debug=DEVEL_MODE, port=8888, host="0.0.0.0")
