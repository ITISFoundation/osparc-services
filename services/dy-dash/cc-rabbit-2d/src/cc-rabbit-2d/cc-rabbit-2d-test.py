import os

from flask import Flask, render_template, Blueprint


DEFAULT_PATH = '/'
base_pathname = os.environ.get('SIMCORE_NODE_BASEPATH', DEFAULT_PATH)
if base_pathname != DEFAULT_PATH :
    base_pathname = "/{}/".format(base_pathname.strip('/'))
print('url_base_pathname', base_pathname)

bp = Blueprint('myBlueprint', __name__, static_folder='static', template_folder='templates')

@bp.route("/", methods=['GET', 'POST'])
def serve_index():
    source = "/static/video.mp4"
    message = "CC-2D-Viewer"
    return render_template('index.html', message=message, source=source, basepath=base_pathname)

app = Flask(__name__)
app.register_blueprint(bp, url_prefix=base_pathname)

if __name__ == "__main__":
    print("running main")
    app.run(debug=False, port=8888, host="0.0.0.0")
