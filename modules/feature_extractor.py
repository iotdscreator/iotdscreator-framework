import os, sys, argparse, logging, time
import yaml, json
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.etc import process_error
from modules.module import Module
from helpers.network_data.packet_reader import PacketReader
from helpers.network_data.network_window_manager import NetworkWindowManager
from helpers.network_data.packet_feature_extractor import PacketFeatureExtractor
from helpers.network_data.flow_feature_extractor import FlowFeatureExtractor
from helpers.host_data.host_log_reader import HostLogReader
from helpers.host_data.host_window_manager import HostWindowManager
from helpers.host_data.host_feature_extractor import HostFeatureExtractor
from helpers.host_data.transition_feature_extractor import TransitionFeatureExtractor

class FeatureExtractor(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize FeatureExtractor")
        super().__init__(core, conf)
        c = conf.get("packet_reader", None)
        self.packet_reader = PacketReader(c)

        c = conf.get("network_window_manager", None)
        self.network_window_manager = NetworkWindowManager(c)

        c = conf.get("features", None)
        if c:
            c = c.get("packet", None)
        self.packet_feature_extractor = PacketFeatureExtractor(c)

        c = conf.get("features", None)
        if c:
            c = c.get("flow", None)
        self.flow_feature_extractor = FlowFeatureExtractor(c)

        c = conf.get("host_log_reader", None)
        self.host_log_reader = HostLogReader(c)

        c = conf.get("host_window_manager", None)
        self.host_window_manager = HostWindowManager(c)   

        c = conf.get("features", None)
        if c:
            c = c.get("host", None)
        self.host_feature_extractor = HostFeatureExtractor(c)

        c = conf.get("features", None)
        if c:
            c = c.get("transition", None)

        self.transition_feature_extractor = TransitionFeatureExtractor(c)

    def run(self, interfaces=None, pnames=None, nlnames=None, hosts=None, hnames=None, hlnames=None, odir=None, ofprefix=None, timestamp=None):
        logging.info("Running the feature extractor")

        if not interfaces:
            interfaces = self.get_interfaces_of_interest()

        logging.info(" - Interfaces of interest: {}".format(interfaces))

        if not pnames:
            pnames = self.get_network_log_filenames()

        logging.info(" - Network log files: {}".format(pnames))

        if not nlnames:
            nlnames = self.get_network_label_filenames()

        logging.info(" - Network label files: {}".format(nlnames))

        if not hosts:
            hosts = self.get_hostnames_of_interest()

        logging.info(" - Hosts of interest: {}".format(hosts))

        if not hnames:
            hnames = self.get_host_log_filenames()

        logging.info(" - Host log files: {}".format(hnames))

        if not hlnames:
            hlnames = self.get_host_label_filenames()

        logging.info(" - Host label files: {}".format(hlnames))

        if not odir:
            odir = self.get_output_directory()
            if not odir:
                odir = root_directory

        if not ofprefix:
            ofprefix = self.get_output_file_prefix()
            if not ofprefix:
                ofprefix = "noname"

        if not timestamp:
            timestamp = self.get_capture_timestamp()
            if not timestamp:
                timestamp = "notimestamp"

        logging.info(" - Making network dataset")
        logging.info("interfaces: {}".format(interfaces))
        if interfaces:
            for interface in interfaces:
                logging.info("interface: {}".format(interface))
                logging.info("pnames: {}, nlnames: {}".format(pnames, nlnames))
                time.sleep(1)

                if is_target_interface(pnames, nlnames, interface):
                    pairs = get_target_files(pnames, nlnames, interface)

                    for pname, nlname in pairs:
                        logging.info("  => Running the packet reader to load packets at {}".format(interface))
                        self.packet_reader.run(pname, nlname)
                        packets = self.packet_reader.get_packets()
                        logging.info("  => Extracting the packet features")
                        self.packet_feature_extractor.run(packets)
                        dpname = self.packet_feature_extractor.output(odir, ofprefix, interface, timestamp)
                        self.add_labeled_packet_dataset(dpname)
                        logging.info("  => Outputting the packet dataset as {}".format(dpname))

                        logging.info("  => Running the network window manager to generate windows at {}".format(interface))
                        self.network_window_manager.run(packets)
                        network_windows = self.network_window_manager.get_windows()
                        logging.info("  => Extracting the flow features")
                        self.flow_feature_extractor.run(network_windows)
                        dfname = self.flow_feature_extractor.output(odir, ofprefix, interface, timestamp)
                        self.add_labeled_flow_dataset(dfname)
                        logging.info("  => Outputting the flow dataset as {}".format(dfname))

        logging.info(" - Making host dataset")
        if hosts:
            for hostname in hosts:
                if hostname in hnames and hostname in hlnames:
                    logging.info("  => Running the host log reader to load host logs at {}".format(hostname))
                    self.host_log_reader.run(hnames[hostname], hlnames[hostname])
                    host_logs = self.host_log_reader.get_host_logs()
                    logging.info("  => Extracting the host features")
                    self.host_feature_extractor.run(host_logs)
                    dhname = self.host_feature_extractor.output(odir, ofprefix, hostname, timestamp)
                    self.add_labeled_host_dataset(dhname)
                    logging.info("  => Outputting the host dataset as {}".format(dhname))

                    logging.info("  => Running the host window manager to generate windows at {}".format(hostname))
                    self.host_window_manager.run(host_logs)
                    host_windows = self.host_window_manager.get_windows()
                    logging.info("  => Extracting the transition features")
                    self.transition_feature_extractor.run(host_windows)
                    dtname = self.transition_feature_extractor.output(odir, ofprefix, hostname, timestamp)
                    self.add_labeled_transition_dataset(dtname)
                    logging.info("  => Outputting the transition dataset as {}".format(dtname))

        dpnames = self.get_labeled_packet_dataset()
        dfnames = self.get_labeled_flow_dataset()
        dhnames = self.get_labeled_host_dataset()
        dtnames = self.get_labeled_transition_dataset()

        return dpnames, dfnames, dhnames, dtnames

    def quit(self):
        logging.info(" - Quitting the feature extractor")
        pass

def is_target_interface(pnames, nlnames, interface):
    ret = False
    
    for key in pnames:
        if interface in key:
            if key in nlnames:
                ret = True

    return ret

def get_target_files(pnames, nlnames, interface):
    ret = []

    for key in pnames:
        if interface in key:
            if key in nlnames:
                ret.append((pnames[key], nlnames[key]))

    return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-i", "--interfaces", metavar="<interface names>", help="Interface names", type=str, required=True, nargs="+")
    parser.add_argument("-j", "--hostnames", metavar="<host names>", help="Host names", type=str, required=True, nargs="+")
    parser.add_argument("-p", "--network-logs", metavar="<pcap filename>", help="Pcap filename", type=str, required=True, nargs="+")
    parser.add_argument("-q", "--network-label-files", metavar="<network label filename>", help="Network lable filename", type=str, required=True, nargs="+")
    parser.add_argument("-r", "--host-logs", metavar="<host log filename>", help="Host log filename", type=str, required=True, nargs="+")
    parser.add_argument("-s", "--host-label-files", metavar="<host label filename>", help="Host lable filename", type=str, required=True, nargs="+")

    parser.add_argument("-o", "--output", metavar="<output filename prefix>", help="Output filename prefix", type=str, default="noname")
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    for network_log in args.network_logs:
        if not check_file_availability(network_log):
            logging.error("The network log file ({}) does not exist.".format(network_log))
            sys.exit(1)

    for network_label_file in args.network_label_files:
        if not check_file_availability(network_label_file):
            logging.error("The network label file ({}) does not exist.".format(network_label_file))
            sys.exit(1)
    
    for host_log in args.host_logs:
        if not check_file_availability(host_log):
            logging.error("The host log file ({}) does not exist.".format(host_log))
            sys.exit(1)

    for host_label_file in args.host_label_files:
        if not check_file_availability(host_label_file):
            logging.error("The host label file ({}) does not exist.".format(host_label_file))
            sys.exit(1)

    interfaces = args.interfaces
    pnames = {}
    nlnames = {}

    for interface in interfaces:
        for pname in args.network_logs:
            if interface in pname:
                pnames[interface] = pname
                break

        for nlname in args.network_label_files:
            if interface in nlname:
                nlnames[interface] = nlname
                break

    hostnames = args.hostnames
    hnames = {}
    hlnames = {}

    for hostname in hostnames:
        for hname in args.host_logs:
            if hostname in hname:
                hnames[hostname] = hname
                break

        for hlname in args.host_label_files:
            if hostname in hlname:
                hlnames[hostname] = hlname
                break

    conf = load_configuration_file(args.config, "..")
    c = conf.get("feature_extractor", None)
    fe = FeatureExtractor(None, c)
    logging.debug("pnames: {}".format(pnames))
    dpnames, dfnames, dhnames, dtnames = fe.run(interfaces=args.interfaces, pnames=pnames, nlnames=nlnames, hosts=args.hostnames, hnames=hnames, hlnames=hlnames)
    logging.info("Labeled dataset name (network/packet): {}".format(dpnames))
    logging.info("Labeled dataset name (network/flow): {}".format(dfnames))
    logging.info("Labeled dataset name (host/host_log): {}".format(dhnames))
    logging.info("Labeled dataset name (host/transition): {}".format(dtnames))

if __name__ == "__main__":
    main()
