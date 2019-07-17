# pylint: disable=global-statement

import asyncio
import logging
import os
import sys
import json
from shutil import copyfile

from flask import Flask, render_template, Blueprint, Response
import pandas as pd
import numpy as np
from simcore_sdk import node_ports

import tempfile
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tqdm
import zipfile


logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()


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
    global dat_files
    global out_images_path

    # download
    logger.info('download inputs')
    try:
        compressed_data_path = download_all_inputs(1)
        logger.info('inputs downloaded to %s', compressed_data_path)

        temp_folder = tempfile.mkdtemp()
        transfered_bytes = 0
        for file_path in compressed_data_path:
            if file_path and zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path) as zip_file:
                    zip_file.extractall(temp_folder)
                transfered_bytes = transfered_bytes + file_path.stat().st_size

        # get the list of files
        dat_files = sorted([os.path.join(temp_folder, x) for x in os.listdir(temp_folder) if x.endswith(".dat")], key=lambda f: int(''.join(filter(str.isdigit, f))))
        out_images_path = tempfile.gettempdir()
        my_reposnse = {
            'data': {
                'size_bytes': transfered_bytes
            }
        }
        return Response(json.dumps(my_reposnse), status=200, mimetype='application/json')
    except Exception:  # pylint: disable=broad-except
        logger.exception("Unexpected error when retrievin data")
        return Response("Unexpected error", status=500, mimetype='application/json')

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
    dst = "/home/jovyan/src/"+rel_dst
    if os.path.exists(dst):
        os.remove(dst)
    copyfile(video_file_path, dst)
    return rel_dst


# a route where we will display a welcome message via an HTML template
@bp.route("/")
def serve_index():
    video_source = None

    if dat_files and len(dat_files) > 0:
        video_source = create_movie_writer()
        logger.info('video_source %s', video_source)
    if video_source:
        message = "CC-2D-Viewer"
        return render_template('index.html', message=message, source=base_pathname+video_source, basepath=base_pathname)
    message = "Input not found"
    return render_template('index.html', message=message, source="", basepath=base_pathname)


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
