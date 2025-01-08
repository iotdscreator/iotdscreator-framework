import os, sys, argparse, logging
import time
import threading
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.futils import init_host_features

class HostFeatureExtractor:
    def __init__(self, conf):
        self.conf = conf
        self.features = []
        init_host_features(self)

    def add_feature(self, feature):
        if self.conf[feature.get_name()]:
            self.features.append(feature)
            logging.debug("Feature {} is loaded".format(feature.get_name()))

    def run(self, host_logs):
        logging.info("Run Host Feature Extractor")
        self.host_logs = host_logs

        for host_log in host_logs:
            self.extract_feature(host_log)

    def output(self, odir, ofprefix, host, timestamp):
        ofname = "{}/{}-{}-{}-host.csv".format(odir, ofprefix, host, timestamp)
        host_logs = self.host_logs
        features = self.features

        with open(ofname, "w") as of:
            flst = ["hostname", "timestamp"]
            for feature in features:
                flst.append(feature.get_name())
            of.write(','.join(flst))
            of.write(",attack_flag,attack_step,attack_name\n")
            for host_log in host_logs:
                vlst = [host_log.get_hostname(), str(host_log.get_timestamp())]
                for feature in features:
                    vlst.append(str(host_log.get_feature_value(feature.get_name())))
                vlst.append(str(host_log.get_attack_flag()))
                vlst.append(host_log.get_attack_step())
                vlst.append(host_log.get_attack_name())
                logging.debug("vlst: {}".format(vlst))
                of.write(','.join(vlst))
                of.write("\n")

        logging.debug("The host log features are extracted and written in {}".format(ofname))
        return ofname

    def extract_feature(self, host_log):
        for f in self.features:
            f.extract_feature(host_log)

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, help="Configuration file", type=str)
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")

    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_configuration_file(args.config, "../..")
    c = conf.get("feature_extractor", None)
    if c:
        c = c.get("features", None)
        if c:
            c = c.get("host", None)
    hfe = HostFeatureExtractor(c)

    host_logs = None
    hfe.run(host_logs)

if __name__ == "__main__":
    main()
