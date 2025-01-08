import argparse, os, sys, logging
import socket
import time
import pathlib

fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from helpers.host_data.host_info_receiver import HostInfoReceiver
from helpers.host_data.host_info_logger import HostInfoLogger
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file

class HostInfoManager:
    def __init__(self, conf):
        logging.debug("Initialize Host Info Collector")
        self.config = conf
        self.capture_timestamp = None

        if "name" in conf:
            if conf["name"] == "default":
                conf["name"] = "0.0.0.0"

        if not conf["name"]:
            conf["name"] = "0.0.0.0"
        if not conf["port"]:
            conf["port"] = 10200

        self.host_info_receiver = HostInfoReceiver(self, conf)
        self.host_info_logger = HostInfoLogger(self, conf)

    def run(self):
        self.host_info_receiver.run()

    def quit(self):
        self.host_info_receiver.quit()

    def save_log(self, js):
        self.host_info_logger.save_log(js)

    def set_capture_timestamp(self, timestamp):
        self.capture_timestamp = timestamp

    def set_output_file_prefix(self, ofprefix):
        self.host_info_logger.set_output_file_prefix(ofprefix)

    def set_output_directory(self, odir):
        self.host_info_logger.set_output_directory(odir)

    def get_capture_timestamp(self):
        if not self.capture_timestamp:
            self.capture_timestamp = int(time.time())
        return self.capture_timestamp

    def get_host_logs(self):
        pass

    def get_host_log_files(self):
        return self.host_info_logger.get_ofnames()

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<config file>", help="Configuration File", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_configuration_file(args.config, "../..")
    c = None
    if conf:
        c = conf.get("virtual_network_constructor", None)
        if c:
            c = c.get("host_info_manager", None)
    him = HostInfoManager(c)
    him.run()

if __name__ == "__main__":
    main()
