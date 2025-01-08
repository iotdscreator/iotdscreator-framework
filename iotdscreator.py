import os, sys, argparse, logging
import yaml, time
import subprocess
import signal
from modules.scenario_verifier import ScenarioVerifier
from modules.network_abstractor import NetworkAbstractor
from modules.physical_node_mapper import PhysicalNodeMapper
from modules.virtual_network_constructor import VirtualNetworkConstructor
from modules.application_installer import ApplicationInstaller
from modules.attack_scenario_executor import AttackScenarioExecutor
from modules.data_labeler import DataLabeler
from modules.feature_extractor import FeatureExtractor
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file

class IoTDSCreator:
    def __init__(self, sd_file, pni_file, conf):
        logging.info("Starting the IoTDSCreator with the scenario description {}".format(sd_file))
        self.iotdscreator_start = int(time.time())
        self.sd_file = sd_file
        self.pni_file = pni_file
        self.config = conf
        self.root_directory = conf["general"]["root_directory"]
        self.names = {}

        self.find_default_interface()
        self.main_interfaces = {}

        self.scenario = None
        self.physical_node_information = None
        self.abstract_graph = None
        self.split_subgraphs = None
        self.virtual_network_constructed = False
        self.application_installed = False
        self.attack_scenario_executed = False

        self.interfaces = []
        self.network_log_filenames = {}
        self.network_label_filenames = {}

        self.hostnames = []
        self.host_log_filenames = {}
        self.host_label_filenames = {}

        self.labeled_packet_dataset = []
        self.labeled_flow_dataset = []
        self.labeled_host_dataset = []
        self.labeled_transition_dataset = []

        self.output_directory = None
        self.output_file_prefix = None

        self.sig = signal.SIGINT

        def signal_handler(signum, frame):
            logging.error("Stopping gracefully on capturing Ctrl+C")
            self.quit()
            sys.exit(1)
        signal.signal(self.sig, signal_handler)

        self.init_modules()
        self.run()

        self.quit()
        self.iotdscreator_end = int(time.time())
        logging.info("Total elapsed time: {} s".format(self.iotdscreator_end - self.iotdscreator_start))
        logging.info("Network configuration time: {} s".format(self.configuration_end - self.iotdscreator_start))
        logging.info("Dataset creation time: {} s".format(self.iotdscreator_end - self.dataset_creation_start))

    def find_default_interface(self):
        logging.info(" - Finding the main interface")
        cmd = ["route", "-n"]
        output = subprocess.check_output(cmd).decode().split("\n")

        for line in output:
            tokens = line.strip().split(" ")
            if tokens[0] == "0.0.0.0":
                minterface = tokens[-1]
                break

        logging.info("  => Setting the main interface to {}".format(minterface))

        logging.info(" - Finding the IP address of the main interface")
        cmd = "ifconfig | grep -A1 {}".format(minterface)
        output = subprocess.check_output(cmd, shell=True)
        mipaddr = output.decode().split("\n")[1].split("inet")[1].strip().split(" ")[0]

        self.minterface = minterface
        self.mipaddr = mipaddr
        logging.info("  => Setting the IP address of the main interface to {}".format(mipaddr))

        self.names["default"] = mipaddr

    def init_modules(self):
        conf = self.config

        # Initialize the scenario verifier
        c = conf.get("scenario_verifier", None)
        self.scenario_verifier = ScenarioVerifier(self, c)

        # Initialize the network abstractor
        c = conf.get("network_abstractor", None)
        self.network_abstractor = NetworkAbstractor(self, c)

        # Initialize the physical node mapper
        c = conf.get("physical_node_mapper", None)
        self.physical_node_mapper = PhysicalNodeMapper(self, c)

        # Initialize the virtual network constructor
        c = conf.get("virtual_network_constructor", None)
        self.virtual_network_constructor = VirtualNetworkConstructor(self, c)

        # Initialize the application installer
        c = conf.get("application_installer", None)
        self.application_installer = ApplicationInstaller(self, c)

        # Initialize the attack scenario executor
        c = conf.get("attack_scenario_executor", None)
        self.attack_scenario_executor = AttackScenarioExecutor(self, c)

        # Initialize the data labeler
        c = conf.get("data_labeler", None)
        self.data_labeler = DataLabeler(self, c)

        # Initialize the feature extractor
        c = conf.get("feature_extractor", None)
        self.feature_extractor = FeatureExtractor(self, c)

    def run(self):
        self.scenario_description, self.physical_node_information = self.scenario_verifier.run(self.sd_file, self.pni_file)

        if not self.scenario_description:
            logging.error("Fail to abstract the scenario description")
            sys.exit(1)

        if not self.physical_node_information:
            logging.error("Fail to abstract the physical node information")
            sys.exit(1)

        self.abstract_graph = self.network_abstractor.run()
        if not self.abstract_graph:
            logging.error("Fail to make an abstract graph")
            sys.exit(1)

        self.split_subgraphs = self.physical_node_mapper.run()
        if not self.split_subgraphs:
            logging.error("Fail to make subgraphs")
            sys.exit(1)

        self.virtual_network_constructed = self.virtual_network_constructor.run()
        if not self.virtual_network_constructed:
            logging.error("Fail to construct a virtual network")
            sys.exit(1)

        self.application_installed = self.application_installer.run()
        if not self.application_installed:
            logging.error("Fail to install applications on devices")
            sys.exit(1)

        self.configuration_end = int(time.time())
        self.attack_scenario_executed = self.attack_scenario_executor.run()
        if not self.attack_scenario_executed:
            logging.error("Fail to execute the attack scenario")
            sys.exit(1)

        self.dataset_creation_start = int(time.time())
        self.raw_data = self.data_labeler.run()
        if self.raw_data:
            for log, label in self.raw_data:
                logging.debug("log: {}, label: {}".format(log, label))
                dpname, dfname, dhname, dtname = self.feature_extractor.run()
        else:
            logging.error("Fail to make labels")
            sys.exit(1)

        self.labeled_packet_dataset, self.labeled_flow_dataset, self.labeled_host_dataset, self.label_transition_dataset = self.feature_extractor.run()
        logging.info("Dataset:")
        if self.labeled_packet_dataset:
            logging.info(" - Labeled packet dataset: {}".format(self.labeled_packet_dataset))
        if self.labeled_flow_dataset:
            logging.info(" - Labeled flow dataset: {}".format(self.labeled_flow_dataset))
        if self.labeled_host_dataset:
            logging.info(" - Labeled host dataset: {}".format(self.labeled_host_dataset))
        if self.labeled_transition_dataset:
            logging.info(" - Labeled transition dataset: {}".format(self.labeled_transition_dataset))

    def quit(self):
        logging.info("Quitting the entire processes")
        self.feature_extractor.quit()
        self.data_labeler.quit()
        self.attack_scenario_executor.quit()
        self.application_installer.quit()
        self.virtual_network_constructor.quit()
        self.physical_node_mapper.quit()
        self.network_abstractor.quit()
        self.scenario_verifier.quit()

    def get_root_directory(self):
        return self.root_directory

    def get_scenario_description(self):
        return self.scenario_description

    def get_physical_node_information(self):
        return self.physical_node_information

    def get_abstract_graph(self):
        return self.abstract_graph

    def get_split_subgraphs(self):
        return self.split_subgraphs

    def get_virtual_network_constructed(self):
        return self.virtual_network_constructed

    def get_application_installed(self):
        return self.application_installed

    def get_attack_scenario_executed(self):
        return self.attack_scenario_executed

    def get_names(self):
        return self.names

    def get_labeled_packet_dataset(self):
        return self.labeled_packet_dataset

    def get_labeled_flow_dataset(self):
        return self.labeled_flow_dataset

    def get_labeled_host_dataset(self):
        return self.labeled_host_dataset

    def get_labeled_transition_dataset(self):
        return self.labeled_transition_dataset

    def get_main_interface(self):
        return self.minterface

    def set_pnode_main_interface(self, pnode, interface):
        self.main_interfaces[pnode.get_name()] = interface

    def get_pnode_main_interface(self, pnode):
        return self.main_interfaces[pnode.get_name()]

    def get_interfaces_of_interest(self):
        return self.interfaces

    def get_network_log_filenames(self):
        return self.network_log_filenames

    def add_network_label_file(self, interface, lname):
        self.network_label_filenames[interface] = lname

    def get_network_label_filenames(self):
        return self.network_label_filenames

    def get_hostnames_of_interest(self):
        return self.hostnames

    def get_host_log_filenames(self):
        return self.host_log_filenames

    def add_host_label_file(self, hostname, lname):
        self.host_label_filenames[hostname] = lname

    def get_host_label_filenames(self):
        return self.host_label_filenames

    def set_output_directory(self, odir):
        self.output_directory = odir

    def get_output_directory(self):
        return self.output_directory

    def set_output_file_prefix(self, ofprefix):
        self.output_file_prefix = ofprefix

    def get_output_file_prefix(self):
        return self.output_file_prefix

    def set_capture_timestamp(self, timestamp):
        self.capture_timestamp = timestamp

    def get_capture_timestamp(self):
        return self.capture_timestamp

    def add_time_table_file(self, tname):
        if self.data_labeler:
            self.data_labeler.add_time_table_file(tname)

    def add_interface_of_interest(self, interface):
        self.interfaces.append(interface)
        if self.data_labeler:
            self.data_labeler.add_interface_of_interest(interface)

    def add_network_log_file(self, interface, nname):
        self.network_log_filenames[interface] = nname
        if self.data_labeler:
            self.data_labeler.add_network_log_file(interface, nname)

    def add_hostname_of_interest(self, hostname):
        self.hostnames.append(hostname)
        if self.data_labeler:
            self.data_labeler.add_hostname_of_interest(hostname)

    def add_host_log_file(self, hostname, hname):
        self.host_log_filenames[hostname] = hname
        if self.data_labeler:
            self.data_labeler.add_host_log_file(hostname, hname)

    def get_labeled_packet_dataset(self):
        return self.labeled_packet_dataset

    def get_labeled_flow_dataset(self):
        return self.labeled_flow_dataset

    def get_labeled_host_dataset(self):
        return self.labeled_host_dataset

    def get_labeled_transition_dataset(self):
        return self.labeled_transition_dataset

    def add_labeled_packet_dataset(self, dpname):
        self.labeled_packet_dataset.append(dpname)

    def add_labeled_flow_dataset(self, dfname):
        self.labeled_flow_dataset.append(dfname)

    def add_labeled_host_dataset(self, dhname):
        self.labeled_host_dataset.append(dhname)

    def add_labeled_transition_dataset(self, dtname):
        self.labeled_transition_dataset.append(dtname)

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--scenario-description", metavar="<scenario description>", help="Scenario description", type=str, required=True)
    parser.add_argument("-p", "--physical-node-information", metavar="<physical node information>", help="Physical node information", type=str, required=True)
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, default="config.yaml")
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    scenario = os.path.abspath(args.scenario_description)
    nodes = os.path.abspath(args.physical_node_information)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_configuration_file(args.config, ".")

    logging.debug("scenario description: {}".format(scenario))
    logging.debug("physical node information: {}".format(nodes))
    logging.debug("configuration: {}".format(conf))
    IoTDSCreator(scenario, nodes, conf)

if __name__ == "__main__":
	main()
