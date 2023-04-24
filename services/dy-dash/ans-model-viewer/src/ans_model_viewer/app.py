
import numpy as np
from scipy.signal import find_peaks
from pathlib import Path
from typing import List, Union
import os
from dash.dependencies import Output, Input
import dash
from dash import dcc
from dash import html
import plotly.tools as tls
import plotly.graph_objs as go
from flask import Flask, Blueprint, Response
import asyncio

DEVEL_MODE = False
if DEVEL_MODE:
    IN_PARENT_DIR = Path(Path(os.path.dirname(
        os.path.realpath(__file__))).parent).parent / 'validation/inputs'
else:
    IN_PARENT_DIR = Path(os.environ["DY_SIDECAR_PATH_INPUTS"])


DEFAULT_PATH = '/'
#base_pathname = os.environ.get('SIMCORE_NODE_BASEPATH', DEFAULT_PATH)
#if base_pathname != DEFAULT_PATH:
#    base_pathname = "/{}/".format(base_pathname.strip('/'))
base_pathname = '/'
print('url_base_pathname', base_pathname)

server = Flask(__name__)
app = dash.Dash(__name__,
                server=server,
                url_base_pathname=base_pathname
                )

bp = Blueprint('myBlueprint', __name__)

@app.callback(
    [
        Output('graph-1', 'figure'),
        Output('graph-2', 'figure')
    ],
    [
        Input('reload-button', 'n_clicks')
    ]
)
def plot_graphs(_n_clicks) -> List[go.Figure]:
    if INPUTS_EXIST:
        print("Inputs have been found, plotting them...")
        figs = [
            plot_ach_icns(),
            plot_heart_rate()
        ]
    else:
        print("No inputs found, showing empty graph")
        figs = [get_empty_graph() for i in range(2)]
    return figs

@bp.route("/")
def serve_index():
    plot_graphs(1)
    return app.layout

@bp.route("/healthcheck")
def healthcheck():
    return Response("healthy", status=200, mimetype='application/json')
#---------------------------------------------------------#
# Get and process inputs

INPUT_1 = IN_PARENT_DIR.joinpath("input_1/SAN_icnsach.txt")
INPUT_2 = IN_PARENT_DIR.joinpath("input_2/SAN_alloutputs_icnsach.txt")
INPUTS_EXIST = INPUT_1.exists() and INPUT_2.exists()
print(f"This is IN_PARENT_DIR: {IN_PARENT_DIR}")
print(os.listdir(IN_PARENT_DIR))

def get_input_array(input_path: Path, id: int) -> np.ndarray:
    input = np.loadtxt(input_path)
    return input[:, id]

if INPUTS_EXIST: 
    tach = get_input_array(INPUT_2, 0)/1e3  # time
    vmach = get_input_array(INPUT_2, 15) # voltage

    tcach = get_input_array(INPUT_1, 0)/1e3 # time
    cch = get_input_array(INPUT_1, 5) # Ach
    icns = get_input_array(INPUT_1, 6)  # icns

    # calculate heart rates
    loc,_ = find_peaks( vmach , prominence=0.01, width=20 )
    HR = 60./np.diff(loc) * 1000

#---------------------------------------------------------#
# Plot data 

def plot_ach_icns() -> go.Figure:
    # Original code
    #fig3, axs3 = plt.subplots(2, 1, figsize=(12.8, 9.6) )
    #fig3.subplots_adjust(wspace=0.5)
    
    #axs3[0].plot( tcach, cch, 'g' )
    #axs3[0].plot( tcach, icns, 'b' )
    #axs3[0].set_ylim( [0, 150] )
    fig = create_graphs([tcach, tcach], [cch, icns], trace_names=["Ach", "Icns"], 
                        xLabel='Time (sec)', yLabel="")
    fig.update_yaxes(range=[0,150])
    return fig

def plot_heart_rate() -> go.Figure:
    # Original code
    # plot heart rate
    #axs3[1].plot( loc[1:]*0.001, HR, 'm')
    #axs3[1].set_xlabel('Time (sec)', fontsize=20)
    #axs3[1].set_ylabel('AP firing rate [bpm]', fontsize=20)
    fig = create_graphs([loc[1:]*0.001], [HR], trace_names=["bpm"],
                        xLabel='Time (sec)', yLabel='AP firing rate [bpm]')
    return fig



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

empty_graph_1 = get_empty_graph(X_LABEL_TIME_SEC, Y_LABEL_1)
empty_graph_2 = get_empty_graph(X_LABEL_TIME_SEC, Y_LABEL_2)

app.layout = html.Div(children=[
    html.Button('Reload', id='reload-button', style=dcc_input_button),
    dcc.Graph(id='graph-1', figure=empty_graph_1),
    dcc.Graph(id='graph-2', figure=empty_graph_2),
], style=osparc_style)


def create_graphs(x_data: list, y_data: list, trace_names:list, xLabel="x", yLabel="y") -> go.Figure:
    data = [go.Scatter(x=x, y=y, name = n)
            for x,y,n in zip(x_data, y_data, trace_names)]

    fig = get_empty_graph(xLabel, yLabel)
    layout = go.Layout(fig['layout'])
    fig = go.Figure(data=data, layout=layout)
    return fig

if __name__ == "__main__":
    # the following line is needed for async calls
    #asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    server.register_blueprint(bp, url_prefix=base_pathname)
    app.run_server(debug=DEVEL_MODE, port=8888, host="0.0.0.0")
