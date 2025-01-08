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

class CacheRequester:
    def __init__(self, conf):
        self.config = conf
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        timeout = conf.get("timeout", 10)
        self.sock.settimeout(timeout)
        self.bufsize = conf.get("buffer", BUF_SIZE)
        self.wdir = conf.get("working directory", None)
        self.downloaded_files = {}

        if not self.wdir:
            logging.error("The working directory should be specified")
            sys.exit(1)

        logging.debug("working directory: {}".format(self.wdir))

        if not os.path.exists(self.wdir):
            os.mkdir(self.wdir)

    def exchange(self, request, info):
        if not isinstance(request, dict):
            return None
        response = None
        retry = 0
        sock = self.sock

        logging.debug("request: {}".format(request))

        while not response and retry < 3:
            sock.sendto(json.dumps(request).encode(), info)
            response, _ = sock.recvfrom(self.bufsize)

        if response:
            logging.debug("response: {}".format(response))
            response = json.loads(response)

        return response

    def request(self, app):
        conf = self.config
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

        adir = "{}/{}".format(self.wdir, app)
        if not os.path.exists(adir):
            os.mkdir(adir)

        info = (addr, port)
        self.sock.connect(info)
        logging.debug("the client is connected to {}:{}".format(addr, port))
        
        request = {}
        request["opcode"] = "get"
        request["application"] = app
        
        response = self.exchange(request, info)

        rc = response.get("resultcode", 1)

        if rc == 0:
            nfiles = response.get("numfiles", None)
            if not nfiles:
                logging.error("The total number of files must be specified")
                sys.exit(1)

            logging.debug("total number of files: {}".format(nfiles))

            for idx in range(nfiles):
                request["opcode"] = "download"
                request["fidx"] = idx
                request["sequence"] = -1
                response = self.exchange(request, info)

                total = response.get("total", None)
                if not total:
                    logging.error("The total number of content must be specified")
                    sys.exit(1)

                ofname = response.get("filename", None)
                if not ofname:
                    logging.error("The name of the output file must be specified")
                    sys.exit(1)

                ofpath = "{}/{}".format(adir, ofname)

                with open(ofpath, "wb") as of:
                    for i in range(total):
                        request["sequence"] = i
                        response = self.exchange(request, info)
                    
                        if response.get("sequence", -1) == i:
                            if "content" not in response:
                                logging.error("There is no content field in the response")
                                sys.exit(1)
                            content = base64.b64decode(response["content"].encode())
                            of.write(content)
                        else:
                            logging.error("Failed to get the application: {}".format(app))
                            sys.exit(1)
            
                if app not in self.downloaded_files:
                    self.downloaded_files[app] = []
                self.downloaded_files[app].append(ofpath)
                logging.debug("The application ({}) is downloaded to {}".format(app, self.downloaded_files[app]))
        elif rc == 1:
            logging.error("Failed to get the application: {}".format(app))
            sys.exit(1)

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", metavar="<server ip address>", help="Server IP Address", type=str, default="localhost")
    parser.add_argument("-p", "--port", metavar="<server port>", help="Server Port", type=int, default=10201)
    parser.add_argument("-a", "--application", metavar="<content>", help="Content", type=str, required=True)
    parser.add_argument("-w", "--working-directory", metavar="<working directory>", help="Working directory", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    conf = {}
    conf["name"] = args.name
    conf["port"] = args.port
    wdir = args.working_directory
    if "~" in wdir:
        user = os.getlogin()
        home = os.path.expanduser("~{}".format(user))
        wdir = wdir.replace("~", home)

    conf["working directory"] = wdir
    req = CacheRequester(conf)

    req.request(args.application)

if __name__ == "__main__":
    main()
