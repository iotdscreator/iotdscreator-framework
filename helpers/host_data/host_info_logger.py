import argparse, os, sys, logging
import socket
import time
import json
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)

class HostInfoLogger:
    def __init__(self, core, conf):
        logging.debug("Initialize Host Info Parser")
        self.core = core
        self.config = conf
        self.ofnames = {}
        self.ofprefix = None
        self.output_directory = None

    def save_log(self, js):
        conf = self.config
        dtype = js.get("type", None)
        name = js.get("name", None)
        data = js.get("data", None)
        timestamp = js.get("timestamp", None)
        logging.debug("name: {}, timestamp: {}".format(name, timestamp))

        odir = self.output_directory
        if not odir:
            odir = root_directory
        ofprefix = self.ofprefix
        if not ofprefix:
            ofprefix = "example"
        capture_timestamp = self.core.get_capture_timestamp()

        if name not in self.ofnames:
            self.ofnames[name] = "{}/{}-{}-{}.log".format(odir, ofprefix, name, capture_timestamp)

        ofname = self.ofnames[name]
        with open(ofname, "a+") as of:
            of.write("{}\n".format(json.dumps(js)))
        logging.debug("name: {}, timestamp: {} is logged into {}".format(name, timestamp, ofname))

    def set_output_file_prefix(self, ofprefix):
        self.ofprefix = ofprefix

    def set_output_directory(self, odir):
        self.output_directory = odir

    def get_ofnames(self):
        return self.ofnames

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    conf = {}
    conf["ofprefix"] = "example"
    conf["output_directory"] = root_directory
    HostInfoLogger(None, conf)

if __name__ == "__main__":
    main()

