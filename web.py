#!/usr/bin/env python
import flask
import flask.ext.script
import tempfile

from convert import call, list_converters, list_converters_params

web = flask.Blueprint("web", __name__)


def create_app():
    app = flask.Flask(__name__)
    app.config.from_pyfile("settings.py", silent=True)
    app.register_blueprint(web)
    return app


@web.route("/")
def home():
    return 'Reportek converters'

@web.route("/list")
def available_converters():
    return flask.jsonify({'list': list_converters()})


@web.route("/params")
def converters_params():
    response = {'list': list_converters_params()}
    prefix =  flask.current_app.config.get('PREFIX', None)
    if prefix:
        response.update({'prefix': prefix})
    return flask.jsonify(response)


@web.route("/convert/<string:name>", methods=["POST"])
def convert(name):
    document = getattr(flask.request.files.get('file', ''), 'stream', None)
    if not document:
        import StringIO
        document = StringIO.StringIO(flask.request.data)
    with tempfile.NamedTemporaryFile() as tmp:
        chunk = True
        while chunk:
            chunk = document.read(10)
            tmp.file.write(chunk)
        tmp.file.flush()
        tmp.file.seek(0)
        try:
            response = call(name, tmp.name)
        except:
            #TODO return error response
            raise NotImplementedError
        else:
            return flask.Response(response, direct_passthrough=True, content_type="application/octet-stream")


manager = flask.ext.script.Manager(create_app())
if __name__ == "__main__":
    manager.run()

