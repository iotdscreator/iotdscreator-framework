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
from iutils.futils import init_transition_features

class TransitionFeatureExtractor:
    def __init__(self, conf):
        self.conf = conf
        self.features = []
        init_transition_features(self)

        self.windows = []

    def add_feature(self, feature):
        if self.conf[feature.get_name()]:
            self.features.append(feature)
            logging.debug("Feature {} is loaded".format(feature.get_name()))

    def run(self, windows):
        logging.info(" - Running Transition Feature Extractor")
        self.windows = windows

        for window in windows:
            self.extract_feature(window)

    def output(self, odir, ofprefix, host, timestamp):
        ofname = "{}/{}-{}-{}-transition.csv".format(odir, ofprefix, host, timestamp)
        windows = self.windows
        features = self.features

        with open(ofname, "w") as of:
            of.write("hostname,window_start,window_end,")
            flst = []
            for feature in features:
                flst.append(feature.get_name())
            of.write(','.join(flst))
            of.write(",attack_flag,attack_step,attack_name\n")

            for window in windows:
                vlst = []
                vlst.append(str(window.get_hostname()))
                vlst.append(str(window.get_window_start_time()))
                vlst.append(str(window.get_window_end_time()))

                for feature in features:
                    vlst.append(str(window.get_feature_value(feature.get_name())))

                vlst.append(str(window.get_attack_flag()))
                step = "/".join(window.get_attack_step())
                if len(step) == 0:
                    step = "-"
                vlst.append(step)
                name = "/".join(window.get_attack_name())
                if len(name) == 0:
                    name = "-"
                vlst.append("/".join(window.get_attack_name()))
                of.write(','.join(vlst))
                of.write("\n")

        logging.debug("{} features are extracted to {}".format(len(features), ofname))
        return ofname

    def extract_feature(self, window):
        logging.debug("extract_feature()")
        for f in self.features:
            f.extract_feature(window)

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
            c = c.get("transition", None)
    tfe = TransitionFeatureExtractor(c)

    windows = None
    tfe.run(windows)

if __name__ == "__main__":
    main()
