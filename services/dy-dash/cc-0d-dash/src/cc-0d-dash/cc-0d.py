# -*- coding: utf-8 -*-
import os
from pathlib import Path
import subprocess
import asyncio

import numpy as np
import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
from plotly import tools


DEVEL_MODE = False
if DEVEL_MODE:
    WORKDIR = str(Path(os.path.dirname(os.path.realpath(__file__))).parent)
else:
    WORKDIR = '/home/jovyan'
OUTPUT_DIR = WORKDIR + '/output'


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
GRAPH_HEIGHT = 600

def get_empty_input_graph(xLabel, yLabel):
    fig = go.Figure(data=[], layout={})

    fig['layout']['xaxis'].update(
        title=xLabel,
        gridcolor=osparc_style['gridColor']
    )
    fig['layout']['yaxis'].update(
        title=yLabel,
        gridcolor=osparc_style['gridColor']
    )
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

def get_empty_cols_graphs(labelPairs):
    fig = tools.make_subplots(rows=1,
                            cols=len(labelPairs),
                            shared_xaxes=True,
                            vertical_spacing=0.05
    )

    for idx, labelPair in enumerate(labelPairs):
        suffix = str(idx)
        if idx is 0:
            suffix = ''
        fig['layout']['xaxis'+suffix].update(
            title=labelPair[0],
            gridcolor=osparc_style['gridColor']
        )
        fig['layout']['yaxis'+suffix].update(
            title=labelPair[1],
            gridcolor=osparc_style['gridColor']
        )
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

def get_empty_rows_graphs(xLabel, yLabels):
    fig = tools.make_subplots(rows=len(yLabels),
                            cols=1,
                            shared_xaxes=True,
                            horizontal_spacing=0.05
    )

    fig['layout']['xaxis'].update(
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


empty_graph_1 = get_empty_input_graph("time (sec)", "Membrane Potential")
empty_graph_2 = get_empty_input_graph("time (sec)", "Ica (pA/pF)")
empty_graph_3 = get_empty_cols_graphs([["time (sec)", "[Ca]SRT (mM)"], ["time (sec)", "Ca Dyad (uM)"], ["time (sec)", "Ca sl (mM)"]])
empty_graph_4 = get_empty_input_graph("time (sec)", "[Ca]i (uM)")
empty_graph_5 = get_empty_input_graph("time (sec)", "Ito (pA/pF)")
empty_graph_6 = get_empty_input_graph("time (sec)", "INa (pA/pF)")
empty_graph_7 = get_empty_rows_graphs("time (sec)", ["IKs (pA/pF)", "ICFTR"])
empty_graph_8 = get_empty_rows_graphs("time (sec)", ["IK1 (pA/pF)", "IKr (pA/pF)"])
empty_graph_9 = get_empty_cols_graphs([["time (sec)", "[Na]j"], ["time (sec)", "[Na]s"], ["time (sec)", "[Na]j (mmol/L) relevant comportment"]])
empty_graph_10 = get_empty_input_graph("time (sec)", "INCX (pA/pF)")
empty_graph_11 = get_empty_rows_graphs("time (sec)", ["JRyRtot", "Passive Leak", "SR Ca release"])

app.layout = html.Div(children=[
    html.Button('Reload', id='reload-button', style=dcc_input_button),
    dcc.Graph(id='graph-1', figure=empty_graph_1),
    dcc.Graph(id='graph-2', figure=empty_graph_2),
    dcc.Graph(id='graph-3', figure=empty_graph_3),
    dcc.Graph(id='graph-4', figure=empty_graph_4),
    dcc.Graph(id='graph-5', figure=empty_graph_5),
    dcc.Graph(id='graph-6', figure=empty_graph_6),
    dcc.Graph(id='graph-7', figure=empty_graph_7),
    dcc.Graph(id='graph-8', figure=empty_graph_8),
    dcc.Graph(id='graph-9', figure=empty_graph_9),
    dcc.Graph(id='graph-10', figure=empty_graph_10),
    dcc.Graph(id='graph-11', figure=empty_graph_11),
], style=osparc_style)


# When pressing 'Load' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
    [
        Output('graph-1', 'figure'),
        Output('graph-2', 'figure'),
        Output('graph-3', 'figure'),
        Output('graph-4', 'figure'),
        Output('graph-5', 'figure'),
        Output('graph-6', 'figure'),
        Output('graph-7', 'figure'),
        Output('graph-8', 'figure'),
        Output('graph-9', 'figure'),
        Output('graph-10', 'figure'),
        Output('graph-11', 'figure')
    ],
    [
        Input('reload-button', 'n_clicks')
    ]
)
def read_input_files(_n_clicks):
    figs = [
        empty_graph_1,
        empty_graph_2,
        empty_graph_3,
        empty_graph_4,
        empty_graph_5,
        empty_graph_6,
        empty_graph_7,
        empty_graph_8,
        empty_graph_9,
        empty_graph_10,
        empty_graph_11
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
