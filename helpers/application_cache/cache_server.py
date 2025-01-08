import argparse, os, sys, logging
import socket, time, pathlib, base64
import io
from flask import Flask, json, jsonify, abort, make_response, send_file
from flask_restful import Api, Resource, reqparse
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file

app = Flask(__name__)
api = Api(app)
conf = {}
cache = {}

# URI: /
# HTTP behavior: GET
# GET: Get the available content (e.g., host_info_reporter)
# DELETE: Stop the web service
class Cache(Resource):
    def get(self):
        alst = list(cache.keys())
        return make_response(jsonify(applications=list(cache.keys())), 200)

# URI: /<application>
# HTTP behavior: GET
# GET: Get the filenames related to the application
class Application(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(Application, self).__init__()

    def get(self, application):
        if application == "favicon.ico":
            return None
        if not application in cache:
            return make_response(jsonify(error="unavailable application"), 404)
        flst = cache[application]
        return make_response(jsonify(filenames=flst), 200)

# URI: /<application>/<file path>
# HTTP behavior: GET
# GET: Get the file from the file path
class Content(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(Content, self).__init__()

    def get(self, application, content):
        logging.debug("application: {}, content: {}".format(application, content))
        if application == "favicon.ico" or content == "favicon.ico":
            return None
        if not application in cache:
            return make_response(jsonify(error="unavailable application"), 404)
        flst = cache[application]
        fname = "{}/{}".format(application, content)
        logging.debug("flst: {}, fname: {}".format(flst, fname))
        if fname not in flst:
            return make_response(jsonify(error="unavailable file"), 404)
        cdir = conf["cache directory"]
        fpath = "{}/{}".format(cdir, fname)
        logging.debug("fpath: {}".format(fpath))
        return send_file(fpath, download_name=content, mimetype="text/plain", as_attachment=True)

# The assignment of the mapping between the URI and the related class
api.add_resource(Cache, '/')
api.add_resource(Application, '/<string:application>')
api.add_resource(Content, '/<string:application>/<path:content>')

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", metavar="<server ip address>", help="Server IP Address", type=str, default="0.0.0.0")
    parser.add_argument("-p", "--port", metavar="<server port>", help="Server Port", type=int, default=10201)
    parser.add_argument("-c", "--cache-directory", metavar="<cache directory>", help="Cache directory", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    conf["name"] = args.name
    conf["port"] = args.port
    cdir = args.cache_directory
    if "~" in cdir:
        user = os.getlogin()
        home = os.path.expanduser("~{}".format(user))
        cdir = cdir.replace("~", home)

    conf["cache directory"] = cdir

    if not os.path.exists(cdir):
        os.mkdir(cdir)
    alst = [d for d in os.listdir(cdir) if os.path.isdir("{}/{}".format(cdir, d))]
    for application in alst:
        cache[application] = []
        for path, subdirs, files in os.walk("{}/{}".format(cdir, application)):
            for name in files:
                fpath = os.path.join(path, name)
                fpath = fpath[len(cdir)+1:]
                cache[application].append(fpath)

    logging.debug("cached applications: {}".format(alst))
    for application in alst:
        logging.debug(" - {}: {}".format(application, cache[application]))
    app.run(host=args.name, port=args.port)

# The process when the application is starting
if __name__ == "__main__":
    main()
