import os, sys, argparse, logging
import json, yaml
import pathlib
from glob import glob
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from modules.module import Module
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file, load_yaml_file
from iutils.etc import load_qemu_availability
from definitions.pnode import PNode

class ScenarioVerifier(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize Scenario Verifier")
        super().__init__(core, conf)
        logging.debug("self.config: {}".format(self.config))

        self.sd_verified = False
        self.pni_verified = False

        self.presets = {}
        preset_paths = self.load_presets()
        for preset_path in preset_paths:
            spec = preset_path.split("/")[-1]
            self.presets[spec] = preset_path
        logging.debug("self.presets: {}".format(self.presets))

        # architecture - machine - cpu
        self.qemu_availability = load_qemu_availability(self.get_root_directory())

    def run(self, sd_file=None, pni_file=None):
        logging.info("Running the scenario verifier")
        scenario_description = None
        physical_node_information = None

        if sd_file:
            scenario_description = self._verify_scenario_description(sd_file)
            if scenario_description:
                dataset_feature = scenario_description["dataset_feature"]
                ofprefix = dataset_feature.get("name", "noname")
                self.set_output_file_prefix(ofprefix)
                odir = dataset_feature.get("output_directory", root_directory)
                if odir:
                    odir = os.path.expanduser(odir)
                    self.set_output_directory(odir)

                if not os.path.exists(odir):
                    os.mkdir(odir)

        if pni_file:
            physical_node_information = self._verify_physical_node_information(pni_file)

        return scenario_description, physical_node_information

    def quit(self):
        logging.info(" - Quitting the scenario verifier")
        pass

    def _verify_scenario_description(self, sd_file):
        logging.info(" - Verifying the scenario description")
        scenario_description = load_yaml_file(sd_file)
        ret = None
        if not check_file_availability(sd_file):
            return None

        scenario_description = load_yaml_file(sd_file)

        if not scenario_description:
            logging.error("Loading the scenario description error")
            return None

        keys = ["network_configuration", "attack_scenario", "dataset_feature"]
        for key in keys:
            if key not in scenario_description:
                logging.error("The key ({}) does not exist in the scenario description".format(key))
                return None

        #1. Verify the network configuration
        #1-1) Verify the node configurations
        logging.info("  => Verifying the node configuration")
        nodes = scenario_description["network_configuration"].get("node", None)
        if nodes:
            if not self.__verify_node_configuration(nodes):
                logging.error("Verifying the node configuration failed")
                return None
        else:
            logging.error("No node is specified in the scenario description")

        #1-2) Verify the link configurations
        logging.info("  => Verifying the link configuration")
        links = scenario_description["network_configuration"].get("link", None)
        if links:
            if not self.__verify_link_configuration(links):
                logging.error("Verifying the link configuration failed")
                return None
        else:
            logging.error("No link is specified in the scenario description")

        ret = scenario_description
        self.sd_verified = True
        
        return ret

    def __verify_node_configuration(self, nodes):
        ret = True
        for key in nodes:
            for node in nodes[key]:
                if "name" not in node:
                    logging.error("The 'name' must be specified in the node")
                    ret = False

                if "type" not in node:
                    logging.error("The 'type' key must be in the node")
                    ret = False
                    break

                if node["type"] == "qemu":
                    if not self.___verify_qemu_node(node):
                        logging.error("Fail to verify the QEMU device ({})".format(node["name"]))
                        ret = False
                        break
                elif node["type"] == "docker":
                    if not self.___verify_docker_node(node):
                        logging.error("Fail to verify the docker device ({})".format(node["name"]))
                        ret = False
                        break

            if not ret:
                break

        return ret

    def ___verify_qemu_node(self, node):
        if "preset" in node:
            logging.debug("preset: {}".format(node["preset"]))
            spec = node["preset"]

            if spec in self.presets:
                preset = load_yaml_file(self.presets[spec])
                for key in preset:
                    node[key] = preset[key]
            else:
                logging.error("The inputted preset ({}) is not available.".format(spec))
                return False

        if "architecture" not in node:
            logging.error("The architecture for the node is not specified")
            return False

        if "machine" not in node:
            logging.error("The machine for the node is not specified")
            return False

        if "cpu" not in node:
            logging.error("The CPU information for the node is not specified")
            return False

        if "memory" not in node:
            logging.error("The memory information for the node is not specified")
            return False

        if ("firmware" not in node) and ("kernel" not in node or "filesystem" not in node):
            logging.error("The software stack for the node is not specified")
            return False
            
        if "interface" not in node:
            logging.debug("No network interface is specified. The default interface is automatically set.")
            node["interface"] = "eth0"

        if "append" not in node:
            logging.error("The options are not specified. Not sure to be booted")

        if node["architecture"] not in self.qemu_availability:
            logging.error("The architecture ({}) is unavailable in QEMU".format(node["architecture"]))
            return False

        if node["machine"] not in self.qemu_availability[node["architecture"]]:
            logging.error("The machine ({}) is unavailable in qemu-system-{}".format(node["machine"], node["architecture"]))
            return False

        if node["cpu"] not in self.qemu_availability[node["architecture"]][node["machine"]]:
            logging.error("The CPU ({}) is unavailable on the machine ({}) in qemu-system-{}".format(node["cpu"], node["machine"], node["architecture"]))
            return False

        return True

    def ___verify_docker_node(self, node):
        if "image" not in node:
            logging.error("The image for the node must be specified")
            return False
        return True

    def __verify_link_configuration(self, links):
        for link in links:
            pass
        return True

    def _verify_physical_node_information(self, pni_file):
        ret = None
        if not check_file_availability(pni_file):
            return ret

        physical_node_information = load_yaml_file(pni_file)
        if not physical_node_information:
            logging.error("Loading the physical node information error")
            return None

        #1. Verify the accessibility of the nodes
        nodes = physical_node_information["nodes"]
        pnodes = []
        for node in nodes:
            pnode = self.__verify_accessibility(node)
            if not pnode:
                logging.error("Fail to access the physical node ({}:{})".format(node["ipaddr"], node["port"]))
                return None
            pnodes.append(pnode)

        ret = pnodes
        self.pni_verified = True

        return ret

    def __verify_accessibility(self, node):
        ret = None
        timeout = self.config.get("timeout", 5)
        ret = PNode(node, timeout)
        #try:
        data = {"opcode": "hello"}
        json_data = json.dumps(data)
        response = ret.send_request(data)
        logging.debug("Received from the agent ({}:{}): {}".format(node["ipaddr"], node["port"], response))
            
        if not (response["opcode"] == "hello" and response["response"] == "hello"):
            ret = None
        #except:
        #    ret = None
        return ret

    def get_verification_result(self):
        ret = False
        if not self.sd_verified:
            logging.error("The scenario description is not verified")
        elif not self.pni_verified:
            logging.error("The physical node information is not verified")
        else:
            ret = True
            logging.debug("The scenario description and the physical node information are not verified")

        return ret

    def load_presets(self):
        preset_directory = self.config["preset_directory"]
        logging.debug("preset_directory: {}".format(preset_directory))
        preset_paths = glob(preset_directory + "/**/*.spec", recursive=True)
        logging.debug("presets: {}".format(self.presets))
        return preset_paths

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-s", "--scenario-description", metavar="<scenario description file>", help="Scenario description file", type=str, required=True)
    parser.add_argument("-p", "--physical-node-information", metavar="<physical node information file>", help="Physical node information file", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)
    
    conf = load_configuration_file(args.config, "..")
    c = conf.get("scenario_verifier", None)
    sv = ScenarioVerifier(None, c)
    scenario_description, physical_node_information = sv.run(args.scenario_description, args.physical_node_information)
    logging.info("scenario description: {}".format(scenario_description))
    logging.info("physical node information: {}".format(physical_node_information))

if __name__ == "__main__":
    main()
