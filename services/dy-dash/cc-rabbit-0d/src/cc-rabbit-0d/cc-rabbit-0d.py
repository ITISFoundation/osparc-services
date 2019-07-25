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
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly import subplots
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

def download_all_inputs(n_inputs = 1):
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
        data_paths = download_all_inputs(1)
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
X_LABEL_TIME_SEC = "Time (sec)"
Y_LABEL_1 = "Action potential (Vm)"
Y_LABEL_2 = "Calcium cytosol (mM)"

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

def get_empty_cols_graphs(labelPairs=[['x', 'y']]):
    fig = subplots.make_subplots(rows=1,
                            cols=len(labelPairs),
                            shared_xaxes=True,
                            vertical_spacing=0.05
    )
    xLabels = []
    yLabels = []
    for labelPair in labelPairs:
        xLabels.append(labelPair[0])
        yLabels.append(labelPair[1])
    fig = give_fig_osparc_style(fig, xLabels, yLabels)
    return fig

def get_empty_rows_graphs(xLabel='x', yLabels=['y']):
    fig = subplots.make_subplots(rows=len(yLabels),
                            cols=1,
                            shared_xaxes=True,
                            horizontal_spacing=0.05
    )
    fig = give_fig_osparc_style(fig, [xLabel], yLabels)
    return fig


empty_graph_1 = get_empty_graph(X_LABEL_TIME_SEC, Y_LABEL_1)
empty_graph_2 = get_empty_graph(X_LABEL_TIME_SEC, Y_LABEL_2)

app.layout = html.Div(children=[
    html.Button('Reload', id='reload-button', style=dcc_input_button),
    dcc.Graph(id='graph-1', figure=empty_graph_1),
    dcc.Graph(id='graph-2', figure=empty_graph_2),
], style=osparc_style)


SLICING = 10

def create_graphs(data_frames, **kwargs):
    data = [
        go.Scatter(
            x=data_frames[df_index].iloc[0::SLICING,0],
            y=data_frames[df_index].iloc[0::SLICING,i],
            #opacity=1,
            xaxis=("x" + str(df_index + 1)),
            yaxis=("y" + str(df_index + 1)),
            name=str(data_frames[df_index].columns[i])
        ) for df_index in range(0, len(data_frames))
        for i in range(1,data_frames[df_index].columns.size)
    ]

    layout = go.Layout(**kwargs)
    fig = go.Figure(data=data, layout=layout)
    fig = give_fig_osparc_style2(fig)
    return fig

def create_graph(data_frame, x_axis_title=None, y_axis_title=None):
    data = [
        go.Scatter(
            x=data_frame.iloc[0::SLICING,0],
            y=data_frame.iloc[0::SLICING,i]
        )
        for i in range(1,data_frame.columns.size)
    ]

    fig = get_empty_graph(x_axis_title, y_axis_title)
    layout = go.Layout(fig['layout'])
    fig = go.Figure(data=data, layout=layout)
    return fig

#---------------------------------------------------------#
# Data to plot in memory
data_frame_ty = None


# constants ----------
def compute_ynid():
    syids = 9
    yids = [30, 31, 32, 33, 34, 36, 37, 38, 39]
    ynid_l = [0] * 206
    for i in range(1,syids):
        ynid_l[yids[i]] = i
    return ynid_l

# ynid = compute_ynid()
# tArray = 1
# I_Ca_store = 2
# Ito = 3
# Itof = 4
# Itos = 5
# INa = 6
# IK1 = 7
# s1 = 8
# k1 = 9
# Jserca = 10
# Iks = 11
# Ikr = 12
# Jleak = [13,14]
# ICFTR = 15
# Incx = 16

def create_graph_1():
    # Action potential (Vm): col 9th
    axis_colums = [0, 8]
    plot_0 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    pandas_dataframe_to_output_data(plot_0, "ActionPotential", [X_LABEL_TIME_SEC, Y_LABEL_1], 0)
    fig = create_graph(data_frame=plot_0,
                x_axis_title=X_LABEL_TIME_SEC,
                y_axis_title=Y_LABEL_1)
    return fig

def create_graph_2():
    # Calcium cytosol (mM): col 10th
    axis_colums = [0, 9]
    plot_1 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    pandas_dataframe_to_output_data(plot_1, "CalciumCytosol", [X_LABEL_TIME_SEC, Y_LABEL_2], 1)
    fig = create_graph(data_frame=plot_1,
                x_axis_title=X_LABEL_TIME_SEC,
                y_axis_title=Y_LABEL_2)
    return fig

def preprocess_inputs():
    global data_frame_ty

    if data_paths and len(data_paths) == 1:
        data_path_ty = data_paths[0]
        if (data_path_ty is not None):
            # read from file to memory
            data_frame_ty = pd.read_csv(data_path_ty, sep='\t', header=None)

            # scale time
            f = lambda x: x/1000.0
            data_frame_ty[0] = data_frame_ty[0].apply(f)

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
    if (data_frame_ty is not None):
        figs = [
            create_graph_1(),
            create_graph_2()
        ]
    else:
        figs = [get_empty_graph() for i in range(11)]
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
