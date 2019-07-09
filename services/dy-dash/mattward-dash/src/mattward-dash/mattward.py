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

from simcore_sdk import node_ports


DEVEL_MODE = False
if DEVEL_MODE:
    IN_OUT_PARENT_DIR = Path(Path(os.path.dirname(os.path.realpath(__file__))).parent).parent / 'validation'
else:
    IN_OUT_PARENT_DIR = Path('/home/jovyan')
INPUT_DIR = IN_OUT_PARENT_DIR / 'input'
OUTPUT_DIR = IN_OUT_PARENT_DIR / 'output'


DEFAULT_PATH = '/'
base_pathname = os.environ.get('SIMCORE_NODE_BASEPATH', DEFAULT_PATH)
if base_pathname != DEFAULT_PATH :
    base_pathname = "/{}/".format(base_pathname.strip('/'))
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
flex_columns = {
    'display': 'flex'
}
flex_column = {
    'flex': 1,
    'min-width': 0
}
unflex_column = {
    'flex': 0,
    'min-width': '220px',
    'color': osparc_style['color'],
    'backgroundColor': osparc_style['backgroundColor']
}
centered_text = {
    'text-align': 'center',
    'color': osparc_style['color'],
    'backgroundColor': osparc_style['backgroundColor']
}
tab_style = {
    'padding': '5px',
    'color': osparc_style['color'],
    'backgroundColor': osparc_style['backgroundColor']
}
options_layout = {
    # 'border': '1px solid',
    # 'border-radius': '5px',
    'margin-top': '50px'
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
dcc_input_label = {
    'width': '120px',
    'float': 'left'
}
dcc_input_number = {
    'height': '30px',
    'width': '100px',
    'color': dcc_input['color'],
    'backgroundColor': dcc_input['backgroundColor']
}
dcc_input_pair = {
    'overflow': 'hidden',
    'margin-top': '2px',
    'margin-bottom': '2px',
    'color': osparc_style['color'],
    'backgroundColor': osparc_style['backgroundColor']
}


def get_empty_input_graph():
    fig = tools.make_subplots(rows=4,
                            cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.05
    )

    fig['layout']['xaxis'].update(
        title='Conduction Velocity (m/s)',
        gridcolor=osparc_style['gridColor']
    )
    fig['layout']['yaxis'].update(
        title='Vmax(uV)',
        gridcolor=osparc_style['gridColor']
    )
    fig['layout']['yaxis2'].update(
        title='M coeff',
        gridcolor=osparc_style['gridColor']
    )
    fig['layout']['yaxis3'].update(
        title='B coeff (mA)',
        gridcolor=osparc_style['gridColor']
    )
    fig['layout']['yaxis4'].update(
        title='tau_SD(ms)',
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
        height=800,
        showlegend=False,
        plot_bgcolor=osparc_style['backgroundColor'],
        paper_bgcolor=osparc_style['backgroundColor'],
        font=dict(
            color=osparc_style['color']
        )
    )
    return fig

def get_empty_output_1_graph(fixed_tst=True, plot_vs_qst=False, plot_vs_tCNAP=False):
    margin = 10
    label_padding = 30

    layout = go.Layout(
        scene=dict(
            xaxis=dict(
                title='CV (m/s)',
                gridcolor=osparc_style['gridColor'],
                zerolinecolor='rgb(255, 255, 255)',
                showbackground=True,
                backgroundcolor=osparc_style['backgroundColor'],
                type='log',
                autorange=True
            ),
            yaxis=dict(
                title='I_st (mA)',
                gridcolor=osparc_style['gridColor'],
                zerolinecolor='rgb(255, 255, 255)',
                showbackground=True,
                backgroundcolor=osparc_style['backgroundColor']
            ),
            zaxis=dict(
                title='V_pred (uV)',
                gridcolor=osparc_style['gridColor'],
                zerolinecolor='rgb(255, 255, 255)',
                showbackground=True,
                backgroundcolor=osparc_style['backgroundColor']
            )
        ),
        showlegend=False,
        margin=dict(
            l=margin+label_padding,
            r=margin,
            b=margin,
            t=margin
        ),
        height=400,
        plot_bgcolor=osparc_style['backgroundColor'],
        paper_bgcolor=osparc_style['backgroundColor'],
        font=dict(
            color=osparc_style['color']
        )
    )

    if plot_vs_tCNAP:
        layout['scene']['xaxis'].update(
            title='t_CNAP (ms)',
            type='linear'
        )

    if not fixed_tst:
        layout['scene']['yaxis'].update(
            title='t_st (mA)'
        )
    if plot_vs_qst:
        layout['scene']['yaxis'].update(
            title='Q_st (nC)'
        )

    fig = {
        'layout': layout,
        'data': []
    }
    return fig

def get_empty_output_2_graph(fixed_tst=True, plot_vs_qst=False, plot_vs_tCNAP=False):
    margin = 10
    y_label_padding = 50
    x_label_padding = 30
    layout = go.Layout(
        scene=dict(
            xaxis=dict(
                title='CV (m/s)',
                type='log',
                autorange=True
            ),
            yaxis=dict(
                title='I_st (mA)'
            )
        ),
        margin=dict(
            l=margin+y_label_padding,
            r=margin,
            b=margin+x_label_padding,
            t=margin
        ),
        height=400,
        plot_bgcolor=osparc_style['backgroundColor'],
        paper_bgcolor=osparc_style['backgroundColor'],
        font=dict(
            color=osparc_style['color']
        )
    )

    if plot_vs_tCNAP:
        layout['scene']['xaxis'].update(
            title='t_CNAP (ms)',
            type='linear'
        )

    if not fixed_tst:
        layout['scene']['yaxis'].update(
            title='t_st (mA)'
        )
    if plot_vs_qst:
        layout['scene']['yaxis'].update(
            title='Q_st (nC)'
        )

    return {
        'layout': layout,
        'data': []
    }

empty_input_graph = get_empty_input_graph()
empty_output_1_graph = get_empty_output_1_graph()
empty_output_2_graph = get_empty_output_2_graph()

app.layout = html.Div(children=[
    html.Div([
        # Four input graphs on the left
        html.Div([
            html.H4(
                children='Learned Model Input Parameters',
                style=centered_text
            ),

            dcc.Graph(id='graph-ins', figure=empty_input_graph)
        ], style=flex_column),


        # Controls in the middle
        html.Div([
            html.Div(
                children='Minimal description of how the solver works.',
                style=centered_text
            ),

            html.Div([
                html.H5('Input options'),
                html.Label('Select a Nerve Profile'),
                dcc.Dropdown(
                    id='input-nerve-profile',
                    options=[
                        {'label': 'Subject 1: Cervical Vagus', 'value': 0},
                        {'label': 'Subject 2: Cervical Vagus', 'value': 1},
                        {'label': 'Subject 2: Gastric Vagus', 'value': 2}
                    ],
                    value=0,
                    style=dcc_input
                ),

                html.Label('Plot Options'),
                dcc.Checklist(
                    id='input-plot-options',
                    options=[
                        {'label': 'Plot against Charge-Phase', 'value': 'charge_phase_cb'},
                        {'label': 'Plot CNAP versus Time (ms)', 'value': 'time_cb'}
                    ],
                    values=[]
                ),

                html.Button('Load', id='load-input-button', style=dcc_input_button)
            ], style=options_layout),

            html.Div([
                html.H5('Sweep Pulse'),
                dcc.Tabs(
                    id="sweep-pulse-tabs",
                    value='current',
                    children=[
                        dcc.Tab(
                            label='Current',
                            value='current',
                            style=tab_style,
                            selected_style=tab_style,
                            children=[
                                html.Div([
                                    html.Div([
                                        html.Label('Starting tst (mA):')
                                    ], style=dcc_input_label),
                                    dcc.Input(
                                        id='current_in_1',
                                        type='number',
                                        value=0,
                                        style=dcc_input_number
                                    )
                                ], style=dcc_input_pair),

                                html.Div([
                                    html.Div([
                                        html.Label('Ending tst (mA):'),
                                    ], style=dcc_input_label),
                                    dcc.Input(
                                        id='current_in_2',
                                        type='number',
                                        value=1,
                                        style=dcc_input_number
                                    )
                                ], style=dcc_input_pair),

                                html.Div([
                                    html.Div([
                                        html.Label('Step Size (mA):')
                                    ], style=dcc_input_label),
                                    dcc.Input(
                                        id='current_in_3',
                                        type='number',
                                        value=0.01,
                                        style=dcc_input_number
                                    )
                                ], style=dcc_input_pair),

                                html.Div([
                                    html.Div([
                                        html.Label('Fixed Ist (ms):')
                                    ], style=dcc_input_label),
                                    dcc.Input(
                                        id='current_in_4',
                                        type='number',
                                        value=0.4,
                                        style=dcc_input_number
                                    )
                                ], style=dcc_input_pair),

                                html.Button('Predict CNAPs', id='predict-current-button', style=dcc_input_button),
                            ]
                        ),
                        dcc.Tab(
                            label='Duration',
                            value='duration',
                            style=tab_style,
                            selected_style=tab_style,
                            children=[
                                html.Div([
                                    html.Div([
                                        html.Label('Starting Ist (mA):')
                                    ], style=dcc_input_label),
                                    dcc.Input(
                                        id='duration_in_1',
                                        type='number',
                                        value=0,
                                        style=dcc_input_number
                                    )
                                ], style=dcc_input_pair),

                                html.Div([
                                    html.Div([
                                        html.Label('Ending Ist (mA):'),
                                    ], style=dcc_input_label),
                                    dcc.Input(
                                        id='duration_in_2',
                                        type='number',
                                        value=1,
                                        style=dcc_input_number
                                    )
                                ], style=dcc_input_pair),

                                html.Div([
                                    html.Div([
                                        html.Label('Step Size (mA):')
                                    ], style=dcc_input_label),
                                    dcc.Input(
                                        id='duration_in_3',
                                        type='number',
                                        value=0.01,
                                        style=dcc_input_number
                                    )
                                ], style=dcc_input_pair),

                                html.Div([
                                    html.Div([
                                        html.Label('Fixed tst (ms):')
                                    ], style=dcc_input_label),
                                    dcc.Input(
                                        id='duration_in_4',
                                        type='number',
                                        value=0.6,
                                        style=dcc_input_number
                                    )
                                ], style=dcc_input_pair),

                                html.Button('Predict CNAPs', id='predict-duration-button', style=dcc_input_button),
                            ]
                        )
                    ],
                ),
                html.Div(id='tabs-content')
            ], style=options_layout)
        ], style=unflex_column),


        # Two output graphs on the right
        html.Div([
            html.H4(
                id='output-label',
                children='Predicted Compund Nerve Action Potentials',
                style=centered_text
            ),

            dcc.Graph(id='graph-out1', figure=empty_output_1_graph),
            dcc.Graph(id='graph-out2', figure=empty_output_2_graph)
        ], style=flex_column),
    ], style=flex_columns)
], style=osparc_style)


def get_selected_checkboxes(string_from_components):
    checked = [0, 0]
    if ('charge_phase_cb' in string_from_components):
        checked[0] = 1
    if ('time_cb' in string_from_components):
        checked[1] = 1
    return checked


def create_learned_model_input(path, plot_vs_tcnap):
    column_names = ['t_ms', 'CV', 'Vmax','M_mod', 'B_mod', 'tauSD']
    data = pd.read_csv(path, sep=',', names=column_names)

    # dpi = 96
    # height = 1024
    # width = 1024
    # fontsize = 16
    # plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)

    return {
        "plot_vs_tcnap": plot_vs_tcnap,
        "x_axis": {
            "t_ms": data.t_ms,
            "CV": data.CV
        },
        "y_axis": {
            "Vmax": [i*-1e12 for i in data.Vmax],
            "M_mod": data.M_mod,
            "B_mod": data.B_mod,
            "tauSD": data.tauSD,
        }
    }

def create_predicted_compound_nerve_action(cv_path, t_path, ist_path, tst_path, qst_path, vpred_path, lpred_path, fixed_tst, plot_vs_qst, plot_vs_tCNAP): # pylint:disable=too-many-arguments
    data_cv = pd.read_csv(cv_path, sep=',', header=None)
    data_tcnap = pd.read_csv(t_path, sep=',', header=None)
    data_ist = None
    data_tst = None
    if fixed_tst:
        data_ist = pd.read_csv(ist_path, sep=',', header=None)
    else:
        data_tst = pd.read_csv(tst_path, sep=',', header=None)
    data_CAP = pd.read_csv(qst_path, sep=',', header=None)
    data_vpred = pd.read_csv(vpred_path, sep=',', header=None)
    data_lpred = pd.read_csv(lpred_path, sep=',', header=None)

    # dpi = 96
    # height = 1024
    # width = 800
    # fontsize = 16

    data_cv[data_cv>100] = None
    x_axis = data_cv
    if plot_vs_tCNAP:
        x_axis = data_tcnap

    y_axis = data_ist
    if not fixed_tst:
        y_axis = data_tst
    if plot_vs_qst:
        y_axis = data_CAP

    x_axis = x_axis.values[:,0]
    y_axis = y_axis.values[0,:]

    return {
        "fixed_tst": fixed_tst,
        "plot_vs_qst": plot_vs_qst,
        "plot_vs_tCNAP": plot_vs_tCNAP,
        "3d": {
            "x": y_axis,
            "y": x_axis,
            "z": data_vpred.values.T,
        },
        "heatmap": {
            "x": x_axis,
            "y": y_axis,
            "z": data_lpred.values.T,
        }
    }


def push_output_data():
    input_path= OUTPUT_DIR / 'input.csv'
    cv_path= OUTPUT_DIR / 'CV_plot.csv'
    t_path= OUTPUT_DIR / 't_plot.csv'
    ist_path= OUTPUT_DIR / 'Ist_plot.csv'
    tst_path= OUTPUT_DIR / 'tst_plot.csv'
    qst_path= OUTPUT_DIR / 'CAP_plot.csv'
    vpred_path= OUTPUT_DIR / 'V_pred_plot.csv'
    lpred_path= OUTPUT_DIR / 'Lpred_plot.csv'
    output_files = [input_path, cv_path, t_path, ist_path, tst_path, qst_path, vpred_path, lpred_path]
    ports = node_ports.ports()
    tasks = asyncio.gather(*[ports.outputs[idx].set(path) for idx, path in enumerate(output_files)])
    paths_to_outputs = asyncio.get_event_loop().run_until_complete( tasks )
    assert all( p.exists() for p in paths_to_outputs )
    return paths_to_outputs

def run_solver(*args):
    if DEVEL_MODE:
        return

    subprocess.call(["execute_cnap.sh", *args], cwd=OUTPUT_DIR)
    # push_output_data()

def create_input_files(model_id, plot_vs_tCNAP):
    # !execute_cnap.sh $model_id 0 0.0 1.0 0.5 0.4
    run_solver(str(model_id), "0", "0.0", "1.0", "0.5", "0.4")
    path = OUTPUT_DIR / 'input.csv'
    return create_learned_model_input(path, plot_vs_tCNAP)

def build_input_graphs(data):
    marker_size = 2
    line_width = 1
    plot_vs_tcnap = data["plot_vs_tcnap"]
    if (plot_vs_tcnap):
        x_data = data["x_axis"]["t_ms"]
    else:
        x_data = data["x_axis"]["CV"]
    trace1 = go.Scatter(
        x=x_data,
        y=data["y_axis"]["Vmax"],
        mode='lines+markers',
        marker = dict(
            size = marker_size
        ),
        line = dict(
            width = line_width
        )
    )
    trace2 = go.Scatter(
        x=x_data,
        y=data["y_axis"]["M_mod"],
        mode='lines+markers',
        marker = dict(
            size = marker_size
        ),
        line = dict(
            width = line_width
        )
    )
    trace3 = go.Scatter(
        x=x_data,
        y=data["y_axis"]["B_mod"],
        mode='lines+markers',
        marker = dict(
            size = marker_size
        ),
        line = dict(
            width = line_width
        )
    )
    trace4 = go.Scatter(
        x=x_data,
        y=data["y_axis"]["tauSD"],
        mode='lines+markers',
        marker = dict(
            size = marker_size
        ),
        line = dict(
            width = line_width
        )
    )

    fig = get_empty_input_graph()
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 2, 1)
    fig.append_trace(trace3, 3, 1)
    fig.append_trace(trace4, 4, 1)

    if (plot_vs_tcnap):
        fig['layout']['xaxis'].update(
            autorange=True
        )
    else:
        fig['layout']['xaxis'].update(
            type='log',
            autorange=True
        )

    return fig

# When pressing 'Load' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
    Output('graph-ins', 'figure'),
    [Input('load-input-button', 'n_clicks')],
    state=[
        State(component_id='input-nerve-profile', component_property='value'),
        State(component_id='input-plot-options', component_property='values')
    ]
)
def read_input_file(_n_clicks, input_nerve_profile, input_plot_options):
    model_id = input_nerve_profile + 1
    selected_cb = get_selected_checkboxes(input_plot_options)
    data = create_input_files(model_id, selected_cb[1])
    return build_input_graphs(data)


# When pressing 'Predict' this callback will be triggered.
# Also, its output will trigger the rebuilding of the two output graphs.
@app.callback(
    Output('output-label', 'children'),
    [
        Input('predict-current-button', 'n_clicks_timestamp'),
        Input('predict-duration-button', 'n_clicks_timestamp')
    ]
)
def update_output_label(button_current_ts, button_duration_ts):
    if button_current_ts is None:
        button_current_ts = 0
    if button_duration_ts is None:
        button_duration_ts = 0

    base_text = 'Predicted Compund Nerve Action Potentials'
    if button_current_ts<button_duration_ts:
        return base_text + ' (Duration)'
    return base_text + ' (Current)'


def build_graph_out_1(data):
    fig = get_empty_output_1_graph()
    if not data:
        return fig
    fig = get_empty_output_1_graph(data["fixed_tst"], data["plot_vs_qst"], data["plot_vs_tCNAP"])

    dummy_wireframe = False
    if dummy_wireframe:
        x = np.linspace(-5, 5, 50)
        y = np.linspace(-5, 5, 50)
        xGrid, yGrid = np.meshgrid(y, x)
        R = np.sqrt(xGrid ** 2 + yGrid ** 2)
        z = np.sin(R)

        # Creating the plot
        lines = []
        line_marker = dict(color='#0066FF', width=2)
        for i, j, k in zip(xGrid, yGrid, z):
            lines.append(go.Scatter3d(x=i, y=j, z=k, mode='lines', line=line_marker))

        fig['data'] = lines
        return fig

    data_3d = data["3d"]
    x = data_3d["x"]
    y = data_3d["y"]
    xGrid, yGrid = np.meshgrid(y, x)
    z = data_3d["z"]
    # Creating the plot
    lines = []
    line_marker = dict(color='#0066FF', width=2)
    for i, j, k in zip(xGrid, yGrid, z):
        lines.append(go.Scatter3d(x=i, y=j, z=k, mode='lines', line=line_marker))

    fig['data'] = lines
    return fig

def build_graph_out_2(data):
    fig = get_empty_output_2_graph()
    if not data:
        return fig
    fig = get_empty_output_2_graph(data["fixed_tst"], data["plot_vs_qst"], data["plot_vs_tCNAP"])

    data_heatmap = data["heatmap"]
    x = data_heatmap["x"]
    y = data_heatmap["y"]
    z = data_heatmap["z"]
    data = go.Heatmap(x=x, y=y, z=z)

    fig['data'] = [data]
    return fig

@app.callback(
    [
        Output('graph-out1', 'figure'),
        Output('graph-out2', 'figure'),
    ],
    [
        Input('predict-current-button', 'n_clicks_timestamp'),
        Input('predict-duration-button', 'n_clicks_timestamp')
    ],
    state=[
        State(component_id='input-nerve-profile', component_property='value'),
        State(component_id='input-plot-options', component_property='values'),
        State(component_id='current_in_1', component_property='value'),
        State(component_id='current_in_2', component_property='value'),
        State(component_id='current_in_3', component_property='value'),
        State(component_id='current_in_4', component_property='value'),
        State(component_id='duration_in_1', component_property='value'),
        State(component_id='duration_in_2', component_property='value'),
        State(component_id='duration_in_3', component_property='value'),
        State(component_id='duration_in_4', component_property='value')
    ]
)
def predict( # pylint:disable=too-many-arguments
    button_current_ts, button_duration_ts,
    input_nerve_profile,
    input_plot_options,
    current_1, current_2, current_3, current_4,
    duration_1, duration_2, duration_3, duration_4):
    if button_current_ts is None:
        button_current_ts = 0
    if button_duration_ts is None:
        button_duration_ts = 0

    if button_current_ts == 0 & button_duration_ts == 0:
        return [get_empty_output_1_graph(), get_empty_output_2_graph()]

    model_id = input_nerve_profile + 1
    selected_cb = get_selected_checkboxes(input_plot_options)
    plot_vs_qst = selected_cb[0]
    plot_vs_tCNAP = selected_cb[1]
    cv_path= OUTPUT_DIR / 'CV_plot.csv'
    t_path= OUTPUT_DIR / 't_plot.csv'
    ist_path= OUTPUT_DIR / 'Ist_plot.csv'
    tst_path= OUTPUT_DIR / 'tst_plot.csv'
    qst_path= OUTPUT_DIR / 'CAP_plot.csv'
    vpred_path= OUTPUT_DIR / 'V_pred_plot.csv'
    lpred_path= OUTPUT_DIR / 'Lpred_plot.csv'
    data = None
    if button_current_ts>button_duration_ts:
        sweep_param = 1
        fixed_tst=True
        print("Current clicked.", model_id, sweep_param, plot_vs_qst, plot_vs_tCNAP, current_1, current_2, current_3, current_4)
        # !execute_cnap.sh $model_id $sweep_param $start_ist.value $end_ist.value $step_size_current.value $fixed_tst.value
        run_solver(str(model_id), str(sweep_param), str(current_1), str(current_2), str(current_3), str(current_4))
        data = create_predicted_compound_nerve_action(cv_path=cv_path, t_path=t_path, ist_path=ist_path, tst_path=tst_path, qst_path=qst_path, vpred_path=vpred_path, lpred_path=lpred_path, fixed_tst=fixed_tst, plot_vs_qst=plot_vs_qst, plot_vs_tCNAP=plot_vs_tCNAP)
    else:
        sweep_param = 0
        fixed_tst=False
        print("Duration clicked.", model_id, sweep_param, plot_vs_qst, plot_vs_tCNAP, duration_1, duration_2, duration_3, duration_4)
        # !execute_cnap.sh $model_id $sweep_param $start_ist.value $end_ist.value $step_size_current.value $fixed_tst.value
        run_solver(str(model_id), str(sweep_param), str(duration_1), str(duration_2), str(duration_3), str(duration_4))
        data = create_predicted_compound_nerve_action(cv_path=cv_path, t_path=t_path, ist_path=ist_path, tst_path=tst_path, qst_path=qst_path, vpred_path=vpred_path, lpred_path=lpred_path, fixed_tst=fixed_tst, plot_vs_qst=plot_vs_qst, plot_vs_tCNAP=plot_vs_tCNAP)

    graph1 = build_graph_out_1(data)
    graph2 = build_graph_out_2(data)
    return [graph1, graph2]


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
