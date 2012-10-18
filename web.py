#!/usr/bin/env python
import flask
import flask.ext.script
import tempfile

from convert import call, list_converters, list_converters_params, converters

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
        import subprocess
        try:
            extra_params = flask.request.form.values()
            if not extra_params:
                extra_params = flask.request.args.values()
            response = call(name, tmp.name, list(extra_params))
        except subprocess.CalledProcessError as exp:
            #TODO return error response
            response = exp.output
        content_type = converters.get(name).ct_output
        return flask.Response(response, content_type=content_type)


app = create_app()
manager = flask.ext.script.Manager(app)
if __name__ == "__main__":
    manager.run()
