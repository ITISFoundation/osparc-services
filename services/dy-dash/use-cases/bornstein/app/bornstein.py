# -*- coding: utf-8 -*-
import os
from pathlib import Path
import subprocess

import pandas as pd
import matplotlib.pyplot as plt

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
from plotly import tools

# from simcore_sdk import node_ports
# PORTS = node_ports.ports()


DEVEL_MODE = True
if DEVEL_MODE:
    WORKDIR = str(Path(os.path.dirname(os.path.realpath(__file__))).parent)
else:
    WORKDIR = '/home/bornstein'
OUTPUT_DIR = WORKDIR + '/output'


app = dash.Dash(__name__)
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
    'min-width': '400px',
    'margin': '10px',
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
    'margin-top': '30px'
}
hidden = {
    'display': 'none'
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
    'width': '270px',
    'float': 'left'
}
dcc_input_number = {
    'height': '30px',
    'width': '130px',
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

def get_empty_graphs(n_inputs=3):
    fig = tools.make_subplots(rows=1+n_inputs,
                            cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.05
    )

    fig['layout']['xaxis'].update(
        title='Time (m/s)',
        gridcolor=osparc_style['gridColor']
    )
    for i in range(n_inputs+1):
        fig['layout']['yaxis'+str(i+1)].update(
            title='cell_'+str(i)+'_V_soma',
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

def get_input_neuron_tab_form(id):
    return html.Div([
        html.Div([
            html.Div([
                html.Label('Minimum delay (ms):')
            ], style=dcc_input_label),
            dcc.Input(
                id='input_neuron_min_delay_'+str(id),
                type='number',
                value=20,
                style=dcc_input_number
            )
        ], style=dcc_input_pair),

        html.Div([
            html.Div([
                html.Label('Maximum delay (ms):')
            ], style=dcc_input_label),
            dcc.Input(
                id='input_neuron_max_delay_'+str(id),
                type='number',
                value=30,
                style=dcc_input_number
            )
        ], style=dcc_input_pair),

        html.Div([
            html.Div([
                html.Label('Weight:')
            ], style=dcc_input_label),
            dcc.Input(
                id='input_neuron_weight_'+str(id),
                type='number',
                value=0.02,
                min=0,
                max=1,
                style=dcc_input_number
            )
        ], style=dcc_input_pair),

        html.Div([
            html.Div([
                html.Label('Transmitter:')
            ], style=dcc_input_label),
            dcc.Dropdown(
                id='input_neuron_transmitter_'+str(id),
                options=[
                    {'label': 'gaba a', 'value': 0},
                    {'label': 'gaba c', 'value': 1},
                    {'label': 'alpha', 'value': 2}
                ],
                value=0,
                style=dcc_input
            )
        ], style=dcc_input_pair)
    ])

empty_graphs = get_empty_graphs(3)

app.layout = html.Div(children=[
    html.Div([
        # Controls on the left side
        html.Div([
            html.H1(
                children='Bornstein solver',
                style=centered_text
            ),
            html.Div(
                children='Minimal description of how the solver works.',
                style=centered_text
            ),

            html.Div([
                html.Div([
                    html.Div([
                        html.Label('max conductance Kv 7-2  channel:')
                    ], style=dcc_input_label),
                    dcc.Input(
                        id='max_conductance',
                        type='number',
                        value=0.15,
                        style=dcc_input_number
                    )
                ], style=dcc_input_pair),
            ], style=options_layout),

            html.Div([
                html.Div([
                    html.Div([
                        html.Label('Number of input neurons:')
                    ], style=dcc_input_label),
                    dcc.Input(
                        id='n_input_neurons',
                        type='number',
                        value=3,
                        disabled=True,
                        style=dcc_input_number
                    )
                ], style=dcc_input_pair),
                html.Div([
                    dcc.Tabs(
                        id="input_neurons",
                        value='input_neuron_1',
                        children=[
                            dcc.Tab(
                                label='Neuron 1',
                                value='input_neuron_1',
                                style=tab_style,
                                selected_style=tab_style,
                                children=[get_input_neuron_tab_form(0)]
                            ),
                            dcc.Tab(
                                label='Neuron 2',
                                value='input_neuron_2',
                                style=tab_style,
                                selected_style=tab_style,
                                children=[get_input_neuron_tab_form(1)]
                            ),
                            dcc.Tab(
                                label='Neuron 3',
                                value='input_neuron_3',
                                style=tab_style,
                                selected_style=tab_style,
                                children=[get_input_neuron_tab_form(2)]
                            ),
                        ]
                    ),
                    html.Div(id='tabs-content')
                ]),
            ], style=options_layout),
            
            html.Div([
                html.Button('Run', id='run-button', style=dcc_input_button)
            ], style=options_layout)
        ], style=unflex_column),

        # Four graphs on the right
        html.Div([
            html.H4(
                children='Output and Inputs',
                style=centered_text
            ),

            dcc.Graph(id='graphs', figure=empty_graphs)
        ], style=flex_column)
    ], style=flex_columns)
], style=osparc_style)

def run_solver(*args):
    if DEVEL_MODE:
        return
    return

def traces_to_csv():
    path = OUTPUT_DIR+'/traces.pkl'
    traces = pd.read_pickle(path)

    n_data = len(traces['tracesData'])
    n_includes = len(traces['include'])
    n_traces = int(n_data / n_includes)

    dfs = []
    for i in range(n_includes):
        data = traces['tracesData'][i]
        dl = list(data.keys())
        x = data[dl[0]][1:]
        df = pd.DataFrame({"Time [ms]": x})
        dfs.append(df)

    # rest of quantites next
    for _i in range(n_traces):
        for _j in range(n_includes):
            idx = _i * n_includes + _j
            data = traces['tracesData'][idx]
            dl = list(data.keys())
            y = data[dl[1]]
            dfs[_j][dl[1]] = y

    dfs[0].to_csv(OUTPUT_DIR+'/output.csv', sep=',', encoding='utf-8', index=False)
    for idx, df in enumerate(dfs[1:]):
        df.to_csv(OUTPUT_DIR+'/input'+str(idx)+'.csv', sep=',', encoding='utf-8', index=False)

def create_trace_from_csv(filename):
    marker_size = 2
    line_width = 1
    df = pd.read_csv(filename)
    # print(df["Time [ms]"].values.tolist())
    # return
    trace = go.Scatter(
        x=df[df.columns[0]].values.tolist(),
        y=df[df.columns[6]].values.tolist(),
        mode='lines+markers',
        marker = dict(
            size = marker_size
        ),
        line = dict(
            width = line_width
        )
    )
    return trace

def csv_to_plots(n_inputs=3):
    traces = []
    out_path = OUTPUT_DIR+'/output.csv'
    if (os.path.isfile(out_path)):
        trace = create_trace_from_csv(out_path)
        traces.append(trace)

    for i in range(n_inputs):
        in_path = OUTPUT_DIR+'/input'+str(i)+'.csv'
        if (os.path.isfile(in_path)):
            trace = create_trace_from_csv(in_path)
            traces.append(trace)

    fig = get_empty_graphs()
    for idx, trace in enumerate(traces):
        fig.append_trace(trace, idx+1, 1)

    return fig

# When pressing 'Load' this callback will be triggered.
@app.callback(
    Output('graphs', 'figure'),
    [Input('run-button', 'n_clicks')]
)
def read_input_file(_n_clicks):
    run_solver()
    traces_to_csv()
    fig = csv_to_plots()
    return fig


if __name__ == '__main__':
    app.run_server(debug=DEVEL_MODE, port=8888, host="0.0.0.0")