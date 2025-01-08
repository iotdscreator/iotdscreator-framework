import argparse, os, sys, logging
import socket
import subprocess
import time
import threading
import pathlib
import json
import base64
from json.decoder import JSONDecodeError
from multiprocessing import Process
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file

BUF_SIZE=16384

class ApplicationCache:
    def __init__(self, conf):
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

        self.pid = None
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
        logging.info(" - Running the application cache server")
        logging.info("  => Killing the existing application cache server process")
        cmd = "lsof -i:{}".format(self.config.get("port", 10201))
        cmd += " | awk '{print $2}'"
        output = subprocess.run(cmd, shell=True, capture_output=True)
        tmp = output.stdout.decode().strip().split("\n")
        pids = []
        pids.append(os.getpid())
        pids.append(os.getppid())
        for p in tmp:
            try:
                pid = int(p)
                if pid not in pids:
                    cmd = "kill -9 {}".format(pid)
                    logging.debug("cmd: {}".format(cmd))
                    subprocess.run(cmd, shell=True)
            except:
                continue

        logging.info("  => Running the application cache server")
        cache_server = self.config.get("cache_server", "{}/helpers/application_cache/cache_server.py".format(root_directory))
        addr = self.config.get("name", "0.0.0.0")
        port = self.config.get("port", 10201)
        cdir = self.cdir
        cmds = ["python3", cache_server, "-n", addr, "-p", "{}".format(port), "-c", cdir]
        process = subprocess.Popen(cmds, close_fds=True)
        self.pid = process.pid

    def quit(self):
        logging.info(" - Stopping the application cache")
        #cmd = "lsof -i:{}".format(self.config.get("port", 10201))
        #cmd += " | awk '{print $2}'"
        #output = subprocess.run(cmd, shell=True, capture_output=True)
        #tmp = output.stdout.decode().strip().split("\n")
        #for p in tmp:
        #    try:
        #        pid = int(p)
        #        cmd = "kill -2 {}".format(pid)
        #        logging.debug("cmd: {}".format(cmd))
        #        subprocess.run(cmd, shell=True)
        #    except:
        #        continue
        #if self.pid:
        #    cmd = "kill -2 {}".format(self.pid)
        #    logging.info("cmd: {}".format(cmd))
        #    subprocess.Popen(cmd, shell=True)
        #    logging.info("kill the process of the application cache")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", metavar="<server ip address>", help="Server IP Address", type=str, default="localhost")
    parser.add_argument("-p", "--port", metavar="<server port>", help="Server Port", type=int, default=10201)
    parser.add_argument("-c", "--cache-directory", metavar="<cache directory>", help="Cache directory", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    conf = {}
    conf["name"] = args.address
    conf["port"] = args.port

    cdir = args.cache_directory
    user = os.getlogin()
    home = os.path.expanduser("~{}".format(user))
    if "~" in cdir:
        cdir.replace("~", home)
    conf["cache_directory"] = cdir
    logging.debug("configuration: {}".format(conf))

    if not os.path.exists(cdir):
        os.mkdir(cdir)
    ac = ApplicationCache(conf)

    flst = ["host_info_reporter.sh", "test"]
    ac.set_file_list("host_info_reporter", flst)
    ac.run()

if __name__ == "__main__":
    main()
