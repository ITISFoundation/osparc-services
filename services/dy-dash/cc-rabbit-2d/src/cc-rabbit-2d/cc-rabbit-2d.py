# -*- coding: utf-8 -*-
# pylint: disable=dangerous-default-value
# pylint: disable=global-statement

import asyncio
import logging
import os
import sys
from pathlib import Path

import dash
import dash_html_components as html
import flask
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from simcore_sdk import node_ports
from tenacity import before_log, retry, wait_fixed

import tempfile
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tqdm
import zipfile


logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

#TODO: node_ports.wait_for_response()
@retry(wait=wait_fixed(3),
    #stop=stop_after_attempt(15),
    before=before_log(logger, logging.INFO) )
def download_all_inputs(n_inputs = 1):
    ports = node_ports.ports()
    tasks = asyncio.gather(*[ports.inputs[n].get() for n in range(n_inputs)])
    paths_to_inputs = asyncio.get_event_loop().run_until_complete( tasks )
    assert all( p.exists() for p in paths_to_inputs )
    return paths_to_inputs


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


empty_graph = get_empty_graph()

app.layout = html.Div(children=[
    html.Button('Reload', id='reload-button', style=dcc_input_button),
    html.Video(id='video')
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
dat_files = None
out_images_path = None

# @app.route("/retrieve")
def retrieve():
    global dat_files
    global out_images_path

    # download
    compressed_data_path = download_all_inputs(1)

    temp_folder = tempfile.mkdtemp()
    if len(compressed_data_path) > 0:
        if zipfile.is_zipfile(compressed_data_path[0]):
            with zipfile.ZipFile(compressed_data_path[0]) as zip_file:
                zip_file.extractall(temp_folder)

    # get the list of files
    dat_files = sorted([os.path.join(temp_folder, x) for x in os.listdir(temp_folder) if x.endswith(".dat")], key=lambda f: int(''.join(filter(str.isdigit, f))))
    out_images_path = tempfile.gettempdir()


def plot_contour(dat_file):
    plt.clf()
    data_frame = pd.read_csv(dat_file, sep='\t', header=None)
    if data_frame.shape[0] == 1:
        data_frame = pd.concat([data_frame]*data_frame.shape[1], ignore_index=True)
    plt.contourf(data_frame.values, cmap=plt.get_cmap('jet'), levels=np.arange(-100.0, 51.0, 1.0))
    plt.axis("off")
    plt.colorbar()


def create_movie_writer():
    FFMpegWriter = animation.writers["ffmpeg"]
    metdata = dict(title="Action potentials", artist="", comment="")
    movie_writer = FFMpegWriter(fps=30, metadata=metdata)

    pixel_size = 600
    dpi = 96.0
    plt.ioff()
    fig = plt.figure(frameon=False, figsize=(pixel_size/dpi, pixel_size/dpi), dpi=dpi)

    number_of_frames = len(dat_files)
    video_file_path = os.path.join(out_images_path, "test_movie.mp4")
    with movie_writer.saving(fig, video_file_path, dpi):
        for nFrame in tqdm.tqdm(range(0, number_of_frames)):
            plot_contour(dat_files[nFrame])
            movie_writer.grab_frame()
    plt.close(fig)
    return video_file_path


# When pressing 'Load' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
    [
        Output('video', 'src')
    ],
    [
        Input('reload-button', 'n_clicks')
    ]
)
def read_input_files(_n_clicks):
    retrieve()
    if (dat_files is not None) and (out_images_path is not None):
        # figs = [create_movie_writer()]
        figs = [get_empty_graph()]
    else:
        figs = [get_empty_graph()]
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
