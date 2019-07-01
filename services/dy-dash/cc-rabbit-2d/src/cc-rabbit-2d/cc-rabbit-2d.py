# -*- coding: utf-8 -*-
import os
from pathlib import Path
import asyncio

import numpy as np
import pandas as pd
import tempfile
import zipfile
import tqdm
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import flask
import dash
import logging
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
from plotly import tools

logger = logging.getLogger(__name__)

DEVEL_MODE = True
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


def plot_contour(dat_files, i):
    plt.clf()
    data_frame = pd.read_csv(dat_files[i], sep='\t', header=None)
    if data_frame.shape[0] == 1:
        data_frame = pd.concat([data_frame]*data_frame.shape[1], ignore_index=True)
    plt.contourf(data_frame.values, cmap=plt.get_cmap('jet'), levels=np.arange(-100.0, 51.0, 1.0))
    plt.axis("off")
    plt.colorbar()

# def _no_relative_path_zip(members: zipfile.ZipFile):
def _no_relative_path_zip(members):
    for zipinfo in members.infolist():
        path = Path(zipinfo.filename)
        if path.is_absolute():
            # absolute path are not allowed
            continue
        if path.match("/../"):
            # relative paths are not allowed
            continue
        yield zipinfo.filename

def plot_video():
    # data_path_a = await PORTS.inputs[0].get()
    data_path_a = INPUT_DIR / 'aps.zip'

    temp_folder = tempfile.mkdtemp()
    if zipfile.is_zipfile(data_path_a):
        logger.info("unzipping %s", data_path_a)
        with zipfile.ZipFile(data_path_a) as zip_file:
            zip_file.extractall(temp_folder, members=_no_relative_path_zip(zip_file))

    # get the list of files
    dat_files = sorted([os.path.join(temp_folder, x) for x in os.listdir(temp_folder) if x.endswith(".dat")], key=lambda f: int(''.join(filter(str.isdigit, f))))
    out_images_path = tempfile.gettempdir()

    # create movie writer
    FFMpegWriter = animation.writers["ffmpeg"]
    metadata = dict(title="Action potentials", artist="", comment="")
    movie_writer = FFMpegWriter(fps=30, metadata=metadata)

    pixel_size = 600
    dpi = 96.0
    plt.ioff()
    fig = plt.figure(frameon=False, figsize=(pixel_size/dpi, pixel_size/dpi), dpi=dpi)

    number_of_frames = len(dat_files)
    video_file_path = os.path.join(out_images_path, "movie.mp4")
    with movie_writer.saving(fig, video_file_path, dpi):
        for frame in tqdm.tqdm(range(0, number_of_frames)):
            plot_contour(dat_files, frame)
            movie_writer.grab_frame()
    plt.close(fig)

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
        plot_video()
    ]
    return figs


class AnyThreadEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """Event loop policy that allows loop creation on any thread."""

    # def get_event_loop(self) -> asyncio.AbstractEventLoop:
    def get_event_loop(self):
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
