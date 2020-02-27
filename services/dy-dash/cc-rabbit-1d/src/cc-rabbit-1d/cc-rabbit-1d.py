# -*- coding: utf-8 -*-
# pylint: disable=dangerous-default-value
# pylint: disable=global-statement

import asyncio
import logging
import os
import sys
import json
from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, Blueprint, Response
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from simcore_sdk import node_ports

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()


DEVEL_MODE = False
if DEVEL_MODE:
    IN_OUT_PARENT_DIR = Path(Path(os.path.dirname(os.path.realpath(__file__))).parent).parent / 'validation'
else:
    IN_OUT_PARENT_DIR = Path('/home/jovyan')
INPUT_DIR = IN_OUT_PARENT_DIR / 'input'


DEFAULT_PATH = '/'
base_pathname = os.environ.get('SIMCORE_NODE_BASEPATH', DEFAULT_PATH)
if base_pathname != DEFAULT_PATH :
    base_pathname = "/{}/".format(base_pathname.strip('/'))
print('url_base_pathname', base_pathname)


server = Flask(__name__)
app = dash.Dash(__name__,
    server=server,
    url_base_pathname=base_pathname
)

bp = Blueprint('myBlueprint', __name__)

#---------------------------------------------------------#
# Data to service
data_paths = None

@bp.route("/healthcheck")
def healthcheck():
    return Response("healthy", status=200, mimetype='application/json')

def download_all_inputs(n_inputs = 2):
    ports = node_ports.ports()
    tasks = asyncio.gather(*[ports.inputs[n].get() for n in range(n_inputs)])
    paths_to_inputs = asyncio.get_event_loop().run_until_complete( tasks )
    return paths_to_inputs

@bp.route("/retrieve", methods=['GET', 'POST'])
def retrieve():
    global data_paths

    # download
    logger.info('download inputs')
    try:
        data_paths = download_all_inputs(2)
        logger.info('inputs downloaded to %s', data_paths)

        transfered_bytes = 0
        for file_path in data_paths:
            if file_path:
                transfered_bytes = transfered_bytes + file_path.stat().st_size
        my_response = {
            'data': {
                'size_bytes': transfered_bytes
            }
        }
        return Response(json.dumps(my_response), status=200, mimetype='application/json')
    except Exception:  # pylint: disable=broad-except
        logger.exception("Unexpected error when retrieving data")
        return Response("Unexpected error", status=500, mimetype='application/json')

def pandas_dataframe_to_output_data(data_frame, title, header=False, port_number=0):
    title = title.replace(" ", "_") + ".csv"
    dummy_file_path = Path(title)
    data_frame.to_csv(dummy_file_path, sep=',', header=header, index=False, encoding='utf-8')

    ports = node_ports.ports()
    task = ports.outputs[port_number].set(dummy_file_path)
    asyncio.get_event_loop().run_until_complete( task )

#---------------------------------------------------------#
# Styling

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
        if idx == 0:
            suffix = ''
        fig['layout']['xaxis'+suffix].update(
            title=xLabel,
            gridcolor=osparc_style['gridColor']
        )
    for idx, yLabel in enumerate(yLabels):
        suffix = str(idx)
        if idx == 0:
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
empty_graph_2 = get_empty_graph()

app.layout = html.Div(children=[
    html.Button('Reload', id='reload-button', style=dcc_input_button),
    dcc.Graph(id='graph-1', figure=empty_graph_1),
    dcc.Graph(id='graph-2', figure=empty_graph_2)
], style=osparc_style)


def create_graph(data_frame, x_axis_title=None, y_axis_title=None):
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

#---------------------------------------------------------#
# Data to plot in memory
data_frame_a = None
data_frame_JJ  = None

def plot_ECG():
    x_label = 'Time (sec)'
    y_label = 'ECGs'
    axis_colums = [0,1]
    plot_1 = data_frame_a.filter(items=[data_frame_a.columns[i] for i in axis_colums])
    pandas_dataframe_to_output_data(plot_1, y_label, [x_label, y_label], 0)
    fig = create_graph(data_frame=plot_1, x_axis_title=x_label, y_axis_title=y_label)
    return fig

def ap_surface_1D():
    out_v = data_frame_JJ

    num_cells = 165
    # point ranges you want to plot
    minimum = 0 #90000;
    maximum = out_v.shape[0]-1 # 4 #100000;
    diff = (maximum - minimum + 1)

    t = np.array(out_v.iloc[range(minimum,maximum+1), 0]).reshape(diff, 1)
    T = t
    #creates a matrix of t matricies (1 for each cell)
    for _b in range(1,(num_cells)):
        T = np.hstack((T, t))

    #creats an array of cell numbers
    celln = [x+1 for x in range(num_cells)]
    cellnum = np.array(celln).reshape(1, num_cells)

    #creates a square matrix of cell numbers on the diagonal
    cellm = np.ones((diff,1)) @ cellnum
    vm = out_v.iloc[range(minimum,maximum+1), range(1,num_cells+1)]

    colormap = [
        [0, 'rgb(40.0, 40.0, 40.0)'],
        [1.0, 'rgb(240.0, 240.0, 240.0)']
    ]

    data = [
        go.Surface(
            x=cellm,
            y=T,
            z=vm.values,
            colorscale=colormap,
            reversescale=True
        )
    ]

    camera = dict(
        up=dict(x=-1, y=0, z=0),
        center=dict(x=0,y=0,z=0),
        eye=dict(x=1, y=0, z=2)
    )

    layout = go.Layout(
        title=None,
        scene=dict(camera=camera),
    )
    fig = go.Figure(data=data, layout=layout)
    fig = give_fig_osparc_style2(fig)
    return fig

def preprocess_inputs():
    global data_frame_a
    global data_frame_JJ

    if data_paths and len(data_paths) == 2:
        data_path_a, data_path_JJ = data_paths
        if (data_path_a is not None) and (data_path_JJ is not None):
            # read from file to memory
            data_frame_a = pd.read_csv(data_path_a, sep='\t', header=None)
            data_frame_JJ = pd.read_csv(data_path_JJ, sep='\t', header=None)

# When pressing 'Load' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
    [
        Output('graph-1', 'figure'),
        Output('graph-2', 'figure')
    ],
    [
        Input('reload-button', 'n_clicks')
    ]
)
def read_input_files(_n_clicks):
    preprocess_inputs()
    if (data_frame_a is not None) and (data_frame_JJ is not None):
        figs = [
            plot_ECG(),
            ap_surface_1D()
        ]
    else:
        figs = [get_empty_graph() for i in range(2)]
    return figs

@bp.route("/")
def serve_index():
    read_input_files(1)
    return app.layout


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

    server.register_blueprint(bp, url_prefix=base_pathname)
    app.run_server(debug=DEVEL_MODE, port=8888, host="0.0.0.0")
