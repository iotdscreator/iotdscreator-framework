import argparse, os, sys, logging
import socket
import time
import threading
import asyncio
import pathlib
import json
import base64
from json.decoder import JSONDecodeError
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file

BUF_SIZE=16384

class ApplicationCache:
    def __init__(self, core, conf):
        self.core = core
        self.config = conf
        addr = conf.get("name", None)
        if not addr:
            logging.error("The address of the application cache is not set")
            logging.error("The name must be specified in the configuration")
            sys.exit(1)

        port = conf.get("port", None)
        if not port:
            logging.error("The port number of the application cache is not set")
            logging.error("The port number must be specified in the configuration")
            sys.exit(1)

        self.cache = {}
        self.cache_files = {}
        self.cdir = conf.get("cache_directory", root_directory)
        self.bufsize = conf.get("buffer", BUF_SIZE)
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        logging.debug("addr: {}, port: {}".format(addr, port))
        self.sock.bind((addr, port))
        logging.info(" - Running the application cache at {}:{}".format(addr, port))

    def set_file_list(self, app, flst):
        self.cache[app] = flst

    def get_file_list(self, app):
        return self.cache[app]

    def get_cache_directory(self):
        return self.cdir

    def run(self):
        ac = threading.Thread(target=run, args=(self,))
        ac.start()

def run(ac):
    logging.debug("running the main loop")
    sock = ac.sock
    core = ac.core

    msg = ""
    while True:
        request, info = sock.recvfrom(ac.bufsize)
        request = json.loads(request)
        opcode = request.get("opcode", None)

        if not opcode:
            logging.error("The opcode is not specified in the request")
            sys.exit(1)
        logging.debug("The application cache receives the request: {}".format(request))

        client = threading.Thread(target=handler, args=(ac, request, info,))
        client.start()
        #except BlockingIOError:
        #    continue
        #except JSONDecodeError:
        #    continue

def handler(ac, request, info):
    opcode = request["opcode"]
    response = {}
    response["opcode"] = request["opcode"]
    response["resultcode"] = 0

    if request["opcode"] == "get":
        app = request.get("application", None)
        if not app:
            logging.error("The name of the application should be specified")
            sys.exit(1)

        logging.debug("the requested application: {}".format(app))
        response["application"] = app
        if not app in ac.cache:
            logging.error("The requested application ({}) is not in the cache".format(app))
            response["resultcode"] = 1
            response["reason"] = "the requested application ({}) is not in the cache".format(app)
        else:
            flst = ac.cache[app]
            logging.debug("the requested application: {}, flst: {}".format(app, flst))
            sequence = request.get("sequence", -1)
            logging.debug("sequence: {}".format(sequence))

            response["numfiles"] = len(flst)
            ac.sock.sendto(json.dumps(response).encode(), info)

            if app not in ac.cache_files:
                ac.cache_files[app] = {}

            for fname in flst:
                fpath = "{}/{}/{}".format(ac.get_cache_directory(), app, fname)
                if fname not in ac.cache_files[app]:
                    with open(fpath, "rb") as f:
                        content = f.read()
                    content = base64.b64encode(content).decode()
                    if fname not in ac.cache_files[app]:
                        ac.cache_files[app][fname] = {}
                    total = int(len(content) / 1000) + 1
                    ac.cache_files[app][fname]["total"] = total
                    ac.cache_files[app][fname]["content"] = {}

                    for i in range(total):
                        ac.cache_files[app][fname]["content"][i] = content[i*1000:(i+1)*1000]

    elif request["opcode"] == "download":
        app = request.get("application", None)
        if not app:
            logging.error("The name of the application should be specified")
            sys.exit(1)

        fidx = request.get("fidx", None)
        if fidx == None:
            logging.error("The file index number should be specified")
            sys.exit(1)

        logging.debug("the requested application: {} with the index: {}".format(app, fidx))
        flst = ac.cache[app]
        fname = flst[fidx]
        logging.debug("the file name is {}".format(fname))
        
        sequence = request.get("sequence", -1)
        response["total"] = ac.cache_files[app][fname]["total"]
        if sequence >= 0:
            response["sequence"] = sequence
            response["content"] = ac.cache_files[app][fname]["content"][sequence]
        response["filename"] = fname
        #except:
        #    response["resultcode"] = 1
        logging.debug("response: {}".format(response))
        ac.sock.sendto(json.dumps(response).encode(), info)

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", metavar="<server ip address>", help="Server IP Address", type=str, default="localhost")
    parser.add_argument("-p", "--port", metavar="<server port>", help="Server Port", type=int, default=10201)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    conf = {}
    conf["name"] = args.address
    conf["port"] = args.port
    conf["cache_directory"] = "{}/../../iotdscreator-cache".format(root_directory)
    ac = ApplicationCache(None, conf)

    flst = ["host_info_reporter.sh", "test"]
    ac.set_file_list("host_info_reporter", flst)
    ac.run()

if __name__ == "__main__":
    main()
