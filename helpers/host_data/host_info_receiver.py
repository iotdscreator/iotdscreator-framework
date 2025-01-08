import argparse, os, sys, logging
import socket
import time
import threading
import asyncio
import pathlib
import json
from json.decoder import JSONDecodeError
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file

BUF_SIZE=16384

class HostInfoReceiver:
    def __init__(self, core, conf):
        self.core = core
        self.config = conf
        addr = conf.get("name", None)
        if not addr:
            logging.error("The address of the host info receiver is not set")
            logging.error("The name must be specified in the configuration")
            sys.exit(1)

        port = conf.get("port", None)
        if not port:
            logging.error("The port number of the host info receiver is not set")
            logging.error("The port number must be specified in the configuration")
            sys.exit(1)

        self.bufsize = conf.get("buffer", BUF_SIZE)
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        logging.debug("addr: {}, port: {}".format(addr, port))
        self.sock.bind((addr, port))
        self.running = True
        logging.info(" - Running the host information receiver at {}:{}".format(addr, port))

    def run(self):
        loop = asyncio.new_event_loop()
        self.hir = threading.Thread(target=run, args=(self, loop,))
        self.hir.start()

    def quit(self):
        logging.info(" - Quitting the host info receiver")
        self.running = False
        self.hir.join()

def run(hir, loop):
    logging.debug("Running the loop")
    sock = hir.sock
    core = hir.core

    msg = ""
    while hir.running:
        try:
            m, a = sock.recvfrom(hir.bufsize)
            msg += m.decode()
            js = json.loads(msg, strict=False)
        except BlockingIOError:
            continue
        except JSONDecodeError:
            continue

        logging.debug("received msg: {}".format(js))
        logging.debug("timestamp: {}".format(js["timestamp"]))
        core.save_log(js)
        msg = ""
    logging.info("  => Getting out from the main loop (the host info receiver)")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", metavar="<server ip address>", help="Server IP Address", type=str, default="localhost")
    parser.add_argument("-p", "--port", metavar="<server port>", help="Server Port", type=int, default=10200)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    conf = {}
    conf["name"] = args.address
    conf["port"] = args.port
    hir = HostInfoReceiver(None, conf)
    hir.run()

if __name__ == "__main__":
    main()
