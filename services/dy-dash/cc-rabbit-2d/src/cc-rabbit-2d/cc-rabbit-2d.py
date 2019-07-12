# pylint: disable=global-statement

import asyncio
import logging
import os
import sys
from shutil import copyfile

from flask import Flask, render_template, Blueprint
import pandas as pd
import numpy as np
from simcore_sdk import node_ports
from tenacity import before_log, retry, wait_fixed, stop_after_attempt

import tempfile
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tqdm
import zipfile


logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

#TODO: node_ports.wait_for_response()
@retry(wait=wait_fixed(3),
    stop=stop_after_attempt(15),
    before=before_log(logger, logging.INFO) )
def download_all_inputs(n_inputs = 1):
    ports = node_ports.ports()
    tasks = asyncio.gather(*[ports.inputs[n].get() for n in range(n_inputs)])
    paths_to_inputs = asyncio.get_event_loop().run_until_complete( tasks )
    assert all( p.exists() for p in paths_to_inputs )
    return paths_to_inputs


DEFAULT_PATH = '/'
base_pathname = os.environ.get('SIMCORE_NODE_BASEPATH', DEFAULT_PATH)
if base_pathname != DEFAULT_PATH :
    base_pathname = "/{}/".format(base_pathname.strip('/'))
logger.info('url_base_pathname %s', base_pathname)


bp = Blueprint('myBlueprint', __name__, static_folder='static', template_folder='templates')


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

    movie_name = "output_movie.mp4"
    number_of_frames = len(dat_files)
    video_file_path = os.path.join(out_images_path, movie_name)
    with movie_writer.saving(fig, video_file_path, dpi):
        for nFrame in tqdm.tqdm(range(0, number_of_frames)):
            plot_contour(dat_files[nFrame])
            movie_writer.grab_frame()
    plt.close(fig)
    rel_dst = "static/"+movie_name
    copyfile(video_file_path, "/home/jovyan/src/"+rel_dst)
    return rel_dst

# a route where we will display a welcome message via an HTML template
@bp.route("/", methods=['GET', 'POST'])
def serve_index():
    retrieve()
    if dat_files and len(dat_files) > 0:
        source = create_movie_writer()
        message = "CC-2D-Viewer"
        logger.info('video_source %s', source)
        return render_template('index.html', message=message, source=base_pathname+source, basepath=base_pathname)
    source = ""
    message = "Input not found"
    return render_template('index.html', message=message, source=base_pathname+source, basepath=base_pathname)


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


if __name__ == "__main__":
    # the following line is needed for async calls
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

    app = Flask(__name__)
    app.register_blueprint(bp, url_prefix=base_pathname)
    app.run(debug=False, port=8888, host="0.0.0.0")
