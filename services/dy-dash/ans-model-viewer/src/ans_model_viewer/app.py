
import numpy as np

from pathlib import Path
from typing import List
import os
from dash.dependencies import Output, Input
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
from flask import Flask, Blueprint, Response
import logging 
from scipy.signal import find_peaks
import plotly.graph_objs as go
from multipledispatch import dispatch


DEVEL_MODE = bool(os.getenv("DEVEL_MODE", False))
if not DEVEL_MODE:
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

base_pathname = '/'
print('url_base_pathname', base_pathname)

server = Flask(__name__)
app = dash.Dash(__name__,
                server=server,
                url_base_pathname=base_pathname
                )

bp = Blueprint('myBlueprint', __name__)

osparc_style = {
    'color': '#bfbfbf',
    'backgroundColor': '#202020',
    'gridColor': '#444444',
}

# The Interval component and call make runs every 5 seconds, reload input data and plots them
app.layout = html.Div(style=osparc_style,
    children=[
    dcc.Graph(id='graph-1'),
    dcc.Graph(id='graph-2'),
            dcc.Interval(
            id='interval-component',
            interval=1*20000, # in milliseconds
            n_intervals=0
        )
]
)

@app.callback(
    [
        Output('graph-1', 'figure'),
        Output('graph-2', 'figure')
    ],
    [
    Input('interval-component', 'n_intervals')
    ]
)
def plot_graphs(n) -> List[go.Figure]:
    if len(check_inputs()) == 3:
        if check_inputs()[-1] == "san":
            figs = [
                plot_top_graph(0, 5, 6),
                plot_bottom_graph(15)
            ]
        elif check_inputs()[-1] == "vm":
            figs = [
                plot_top_graph(0,1),
                plot_bottom_graph(0,1)
            ]
        else:
            print("Input 1 file name doesn't contain model type, plotting empty graph")
            figs = [get_empty_graph() for i in range(2)]   
    else:
        print("No inputs found, showing empty graph", flush=DEVEL_MODE)
        figs = [get_empty_graph() for i in range(2)]
    return figs

@bp.route("/")
def serve_index():
    plot_graphs(1)
    return app.layout

# @bp.route("/healthcheck")
# def healthcheck():
#     return Response("healthy", status=200, mimetype='application/json')

#---------------------------------------------------------#
# Check if expected inputs are in the input ports, get and process them

IN_PARENT_DIR = Path(os.environ["DY_SIDECAR_PATH_INPUTS"])

def check_inputs() -> list:
    INPUT_1 = list(Path(os.environ["DY_SIDECAR_PATH_INPUTS"]).joinpath("input_1/").glob("*txt"))
    INPUT_2 = list(Path(os.environ["DY_SIDECAR_PATH_INPUTS"]).joinpath("input_2/").glob("*txt"))
    if len(INPUT_1) == 1 and len(INPUT_2) == 1:
        if "SAN" in str(INPUT_1[0]):
            model_type = 'san'
        elif "VM" in str(INPUT_1[0]):
            model_type = 'vm'
        else:
            model_type = 'other'
        return [INPUT_1[0], INPUT_2[0], model_type]
    else:
        return []

def get_input_array(input_path: Path, id: int) -> np.ndarray:
    input = np.loadtxt(input_path)
    return input[:, id]


#---------------------------------------------------------#
# Plot data 

@dispatch(int, int, int)
def plot_top_graph(id1, id2, id3) -> go.Figure:
    tcach = get_input_array(check_inputs()[0], id1)/1e3 # time
    cch = get_input_array(check_inputs()[0], id2) # Ach
    icns = get_input_array(check_inputs()[0], id3)  # icns
    fig = create_graphs([tcach, tcach], [cch, icns], trace_names=["Ach", "Icns"], 
                        xLabel='Time (sec)', yLabel="", legend=True)
    fig.update_yaxes(range=[0,150])
    return fig

@dispatch(int, int)
def plot_top_graph(id1, id2) -> go.Figure:
    tcach = get_input_array(check_inputs()[0], id1)*0.001 # time
    vm = get_input_array(check_inputs()[0], id2) # voltage
    fig = create_graphs([tcach], [vm], trace_names=["Vm"], 
                        xLabel='Time (sec)', yLabel="Vm (mV)")
    fig.update_yaxes(range=[-100,50])
    return fig

@dispatch(int)
def plot_bottom_graph(id) -> go.Figure:
    vmach = get_input_array(check_inputs()[1], id) # voltage

    # Calculate heart rates
    loc,_ = find_peaks( vmach , prominence=0.01, width=20 )
    HR = 60./np.diff(loc) * 1000
    fig = create_graphs([loc[1:]*0.001], [HR], trace_names=["bpm"],
                        xLabel='Time (sec)', yLabel='AP firing rate [bpm]')
    return fig

@dispatch(int, int)
def plot_bottom_graph(id1, id2) -> go.Figure:
    time = get_input_array(check_inputs()[1], id1)*0.001 # time
    ca = get_input_array(check_inputs()[1], id2)*1000
 
    fig = create_graphs([time], [ca], trace_names=["Ca"],
                        xLabel='Time (sec)', yLabel='Cai [µM]')
    fig.update_yaxes(range=[0,1])
    return fig


def create_graphs(x_data: list, y_data: list, trace_names:list, xLabel="x", yLabel="y", legend=False) -> go.Figure:
    data = [go.Scatter(x=x, y=y, name = n)
            for x,y,n in zip(x_data, y_data, trace_names)]

    fig = get_empty_graph(xLabel, yLabel, legend=legend)
    layout = go.Layout(fig['layout'])
    fig = go.Figure(data=data, layout=layout)
    return fig

#---------------------------------------------------------#
# Styling

# app.css.append_css({
#     "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
# })




def give_fig_osparc_style(fig, xLabels=['x'], yLabels=['y'], legend=False):
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
    fig = give_fig_osparc_style2(fig, legend=legend)
    return fig

def give_fig_osparc_style2(fig, legend=False):
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
        height=400,
        showlegend=legend,
        plot_bgcolor=osparc_style['backgroundColor'],
        paper_bgcolor=osparc_style['backgroundColor'],
        font=dict(
            color=osparc_style['color']
        )
    )
    return fig

def get_empty_graph(xLabel='x', yLabel='y', legend=False):
    fig = go.Figure(data=[], layout={})
    fig = give_fig_osparc_style(fig, [xLabel], [yLabel], legend=legend)
    return fig


if __name__ == "__main__":
    server.register_blueprint(bp, url_prefix=base_pathname)
    print(f"Devel mode is: {DEVEL_MODE}")
    app.run_server(debug=DEVEL_MODE, port=8888, host="0.0.0.0")
