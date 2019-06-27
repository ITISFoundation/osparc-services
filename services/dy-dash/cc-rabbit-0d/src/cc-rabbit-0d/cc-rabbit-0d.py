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


DEVEL_MODE = True
if DEVEL_MODE:
    # WORKDIR = str(Path(os.path.dirname(os.path.realpath(__file__))).parent)
    WORKDIR = str(Path(Path(os.path.dirname(os.path.realpath(__file__))).parent).parent)
else:
    WORKDIR = '/home/jovyan'
INPUT_DIR = WORKDIR + '/input'


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
    return fig

def create_graph(data_frame, title=None, x_axis_title=None, y_axis_title = None):
    data = [
        go.Scatter(
            x=data_frame.iloc[0::SLICING,0],
            y=data_frame.iloc[0::SLICING,i],
            #opacity=1,
            # name=str(data_frame.columns[i])
        )
        for i in range(1,data_frame.columns.size)
    ]

    fig = get_empty_input_graph(x_axis_title, y_axis_title)
    layout = go.Layout(fig['layout'])
    fig = go.Figure(data=data, layout=layout)
    return fig


# data_path_ty = await PORTS.inputs[0].get()
data_path_ty = INPUT_DIR + '/vm_1Hz.txt'
data_frame_ty = pd.read_csv(data_path_ty, sep='\t', header=None)

# scale time
f = lambda x: x/1000.0
data_frame_ty[0] = data_frame_ty[0].apply(f)
syids = 9
yids = [30, 31, 32, 33, 34, 36, 37, 38, 39]
ynid = [0] * 206
for id in range(1,syids):
    ynid[yids[id]] = id

# data_path_ar = await PORTS.inputs[1].get()
data_path_ar = INPUT_DIR + '/allresult_1Hz.txt'
data_frame_ar = pd.read_csv(data_path_ar, sep='\t', header=None)

tArray = 1
I_Ca_store = 2
Ito = 3
Itof = 4
Itos = 5
INa = 6
IK1 = 7
s1 = 8
k1 = 9
Jserca = 10
Iks = 11
Ikr = 12
Jleak = [13,14]
ICFTR = 15
Incx = 16

def create_graph_1():
    # membrane potential
    title="Membrane Potential"
    axis_colums = [0,ynid[39]+1]
    plot_0 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    fig = create_graph(data_frame=plot_0,
                x_axis_title="time (sec)",
                y_axis_title=title)
    return fig

def create_graph_2():
    # LCC current (ICa)
    title="I<sub>Ca</sub> (pA/pF)"
    axis_colums = [0,I_Ca_store-1]
    plot_1 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    fig = create_graph(data_frame=plot_1,
                x_axis_title="time (sec)",
                y_axis_title=title)
    return fig

def create_graph_3():
    # CaSRT & Caj
    data_frame_casrt = data_frame_ty.filter(items=[data_frame_ty.columns[0], data_frame_ty.columns[ynid[30]+1], data_frame_ty.columns[ynid[31]+1]])
    data_frame_casrt[3] = data_frame_casrt[1] + data_frame_casrt[2]
    plot_2 = data_frame_casrt.filter(items=[data_frame_casrt.columns[0], data_frame_casrt.columns[3]])
    plot_data = [plot_2]

    #
    g = lambda x: x*1000.0
    axis_colums = [0,ynid[36]+1]
    data_frame_ty[ynid[36]+1] = data_frame_ty[ynid[36]+1].apply(g)
    plot_3 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    plot_data.append(plot_3)

    axis_colums = [0,ynid[37]+1]
    plot_4 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    plot_data.append(plot_4)
    figs = create_graphs(data_frames=plot_data,
                title=None,
                showlegend=False,
                xaxis=dict(
                    domain=[0,0.3],
                    title="time (sec)"
                ),
                xaxis2=dict(
                    domain=[0.4,0.6],
                    title="time (sec)"),
                xaxis3=dict(
                    domain=[0.7,1.0],
                    title="time (sec)"),
                yaxis=dict(
                    title="[Ca]<sub>SRT</sub> (mM)"
                ),
                yaxis2=dict(
                    title="Ca Dyad (\u00B5M)",
                    anchor="x2"),
                yaxis3=dict(
                    title="Ca sl (mM)",
                    anchor="x3")
                )
    return figs

def create_graph_4():
    # Cai
    title="[Ca]<sub>i</sub> (\u00B5M)"
    axis_colums = [0,ynid[38]+1]
    plot_5 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    fig = create_graph(data_frame=plot_5,
                title=None,
                x_axis_title="time (sec)",
                y_axis_title=title)
    return fig

def create_graph_5():
    # Ito
    title="I<sub>to</sub> (pA/pF)"
    axis_colums = [0,Ito-1]
    plot_6 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    create_graph(data_frame=plot_6,
                title=None,
                x_axis_title="time (sec)",
                y_axis_title=title)

def create_graph_6():
    # INa
    title="I<sub>Na</sub> (pA/pF)"
    axis_colums = [0,INa-1]
    plot_7 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    create_graph(data_frame=plot_7,
                title=None,
                x_axis_title="time (sec)",
                y_axis_title=title)

def create_graph_7():
    # IKs and ICFTR
    axis_colums = [0,Iks-1]
    plot_8 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    plot_data = [plot_8]

    axis_colums = [0,ICFTR-1]
    plot_9 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    plot_data.append(plot_9)

    create_graphs(
        data_frames=plot_data,
        title=None,
        showlegend=False,
        #xaxis=dict(title="time (sec)"),
        xaxis2=dict(
            title="time (sec)",
            anchor="y2"
        ),
        yaxis=dict(
            domain=[0.6,1.0],
            title="I<sub>Ks</sub> (pA/pF)"
        ),
        yaxis2=dict(
            domain=[0,0.5],
            title="I<sub>CFTR</sub>",
            anchor="x2"
        )
    )

def create_graph_8():
    # IKr and IK1
    axis_colums = [0,Ikr-1]
    plot_10 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    plot_data = [plot_10]

    axis_colums = [0,IK1-1]
    plot_11 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    plot_data.append(plot_11)

    create_graphs(
        data_frames=plot_data,
        title=None,
        showlegend=False,
        #xaxis=dict(title="time (sec)"),
        xaxis2=dict(title="time (sec)", anchor="y2"),
        yaxis=dict(
            domain=[0.6,1.0],
            title="I<sub>Kr</sub> (pA/pF)"
        ),
        yaxis2=dict(
            domain=[0,0.5],
            title="I<sub>K1</sub> (pA/pF)",
            anchor="x2"
        )
    )

def create_graph_9():
    # [Na]
    axis_colums = [0,ynid[32]+1]
    plot_12 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    plot_data = [plot_12]

    axis_colums = [0,ynid[33]+1]
    plot_13 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    plot_data.append(plot_13)

    axis_colums = [0,ynid[34]+1]
    plot_14 = data_frame_ty.filter(items=[data_frame_ty.columns[i] for i in axis_colums])
    plot_data.append(plot_14)

    create_graphs(
        data_frames=plot_data,
        title=None,
        showlegend=False,
        xaxis=dict(title="time (sec)", domain=[0,0.3]),
        xaxis2=dict(title="time (sec)", domain=[0.4,0.6]),
        xaxis3=dict(title="time (sec)", domain=[0.7,1.0]),
        yaxis=dict(
            title="[Na]<sub>j</sub>"
        ),
        yaxis2=dict(
            title="[Na]<sub>s<sup>l</sup></sub>",
            anchor="x2"
        ),
        yaxis3=dict(
            title="[Na]<sub>i</sub> (mmol/L relevant compartment",
            anchor="x3"
        )
    )

def create_graph_10():
    # I_NCX
    title="I<sub>NCX</sub> (pA/pF)"
    axis_colums = [0,Incx-1]
    plot_15 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    create_graph(data_frame=plot_15,
                title=None,
                x_axis_title="time (sec)",
                y_axis_title=title)

def create_graph_11():
    # RyR fluxes
    axis_colums = [0,Jleak[0]-1]
    plot_16 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    plot_data = [plot_16]

    axis_colums = [0,Jleak[1]-1]
    plot_17 = data_frame_ar.filter(items=[data_frame_ar.columns[i] for i in axis_colums])
    plot_data.append(plot_17)

    plot_18 = data_frame_ar.filter(items=[data_frame_ar.columns[0]])
    plot_18[1] = data_frame_ar[Jleak[0]-1] - data_frame_ar[Jleak[1]-1]
    plot_data.append(plot_18)
    create_graphs(
        data_frames=plot_data,
        title=None,
        showlegend=False,
        xaxis=dict(title=None),
        xaxis2=dict(title=None),
        xaxis3=dict(title="time (sec)", anchor="y3"),
        yaxis=dict(
            domain=[0.7,1.0],
            title="JRyR<sub>tot</sub>"
        ),
        yaxis2=dict(
            domain=[0.4,0.6],
            title="Passive Leak",
            anchor="x2"
        ),
        yaxis3=dict(
            domain=[0,0.3],
            title="SR Ca release",
            anchor="x3"
        )
    )


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
    print(INPUT_DIR)
    figs = [
        create_graph_1(),
        create_graph_2(),
        create_graph_3(),
        create_graph_4(),
        create_graph_5(),
        create_graph_6(),
        create_graph_7(),
        create_graph_8(),
        create_graph_9(),
        create_graph_10(),
        create_graph_11()
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