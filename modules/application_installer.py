import os, sys, argparse, logging
import yaml, time
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.etc import process_error
from helpers.application_cache.application_cache import ApplicationCache
from modules.module import Module
from modules.scenario_verifier import ScenarioVerifier
from modules.network_abstractor import NetworkAbstractor
from modules.physical_node_mapper import PhysicalNodeMapper
from modules.virtual_network_constructor import VirtualNetworkConstructor

class ApplicationInstaller(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize ApplicationInstaller")
        super().__init__(core, conf)
        self.applications = []
        self.proxy = {}
        c = conf.get("application_cache", None)
        self.names = self.get_names()

        default_ipaddr = self.names.get("default", "0.0.0.0")
        default_port = 10201

        if not c:
            c = {}

        if "name" not in c:
            c["name"] = default_ipaddr

        if c["name"] == "default":
            c["name"] = default_ipaddr

        if "port" not in c:
            c["port"] = default_port

        self.info = (c["name"], c["port"])
        self.names["cache-address"] = c["name"]
        self.names["cache-port"] = c["port"]

        self.application_cache = ApplicationCache(c)

    def run(self, split_subgraphs=None):
        logging.info("Running the application installer")
        self.application_cache.run()
        logging.info(" - Having some cooling time to make sure the cache server is running")
        time.sleep(10)
        if not split_subgraphs:
            split_subgraphs = self.get_split_subgraphs()

        if not split_subgraphs:
            logging.error("To install applications on the nodes, the split subgraphs should be provided")
            logging.error("  split_subgraphs: {}".format(split_subgraphs))
            return None

        self._install_applications(split_subgraphs)

        return self._install_applications(split_subgraphs)

    def quit(self):
        logging.info(" - Quitting the application installer")
        self.application_cache.quit()

    def _install_applications(self, split_subgraphs):
        application_installed = False
        names = self.names

        for subgraph, pnode in split_subgraphs:
            vertex, edge = subgraph
            logging.debug("vertex: {}, edge: {}".format(vertex, edge))

            for v in vertex:
                # 1. Get a list of applications that should be installed on a node
                node = vertex[v]
                vtype = node.get_virtualization_type()
                apps = node.get_applications()
                anames = []
                for app in apps:
                    anames.append(app.get_name())
                logging.info(" - Getting a list of applications on {}: {}".format(node.get_name(), anames))

                arch = node.get_architecture()
                os = node.get_operating_system()

                # 2. Install default applications
                logging.info(" - Install a host information reporter")
                if node.is_host_logging_enabled():
                    node.set_names(self.names)
                    node.get_host_info_reporter()

                # 3. Install applications
                for app in apps:
                    # 3-1. Check if it is installed
                    logging.info(" - Checking whether {} is installed on {}".format(app.get_name(), node.get_name()))
                    cmds = app.check_application(arch, os)
                    needs_installation = False

                    request = {}
                    request["type"] = vtype
                    request["name"] = node.get_name()
                    request["shell"] = node.get_shell_prompts()
                    for cmd in cmds:
                        if "must" in cmd:
                            needs_installation = True
                            break
                        logging.debug("cmd: {}".format(cmd))
                        request["opcode"] = "control"
                        request["command"] = cmd
                        response = pnode.send_request(request)
                        process_error(request, response)
                        logging.debug("response: {}".format(response))

                        output = response["stdout"]
                        logging.debug("output (before): {}".format(output))
                        try:
                            idx = output.find(cmd)
                            if idx > 0:
                                output = output[idx+len(cmd):].strip()
                            logging.debug("output (after): {}".format(output))

                            if (app.get_application_type() not in output) or ("no such" in output.lower()):
                                needs_installation = True
                        except:
                            continue
                    logging.info("  => Requiring installation: {}".format(needs_installation))

                    # 3-2. Install it if it does not exist
                    if needs_installation:
                        logging.info(" - Installing {} on {}".format(app.get_name(), node.get_name()))
                        cmds = app.prepare_application(arch, os)
                        for cmd in cmds:
                            logging.info(" - Running {} on {}".format(cmd, node.get_name()))
                            request["opcode"] = "control"
                            request["type"] = vtype
                            if "cache-address" in cmd:
                                ipaddr = self.names.get("cache-address", self.names.get("default", None))
                                cmd = cmd.replace("cache-address", ipaddr)
                            if "cache-port" in cmd:
                                port = self.names.get("cache-port", 10201)
                                cmd = cmd.replace("cache-port", str(port))
                            request["command"] = cmd
                            request["capture"] = False
                            response = pnode.send_request(request)
                            process_error(request, response)

        application_installed = True
        return application_installed

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-s", "--scenario-description", metavar="<scenario description file>", help="Scenario description file", type=str, required=True)
    parser.add_argument("-p", "--physical-node-information", metavar="<physical node information file>", help="Physical node information file", type=str, required=True)
    parser.add_argument("-i", "--main-interface", metavar="<main interface>", help="Main interface", type=str, required=True)
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

    c = conf.get("network_abstractor", None)
    na = NetworkAbstractor(None, c)
    abstract_graph = na.run(scenario_description)

    c = conf.get("physical_node_mapper", None)
    pnm = PhysicalNodeMapper(None, c)
    split_subgraphs = pnm.run(abstract_graph, physical_node_information)

    c = conf.get("virtual_network_constructor", None)
    vnc = VirtualNetworkConstructor(None, c)
    vnc.set_main_interface(args.main_interface)
    virtual_network_constructed = vnc.run(split_subgraphs)

    if virtual_network_contructed:
        c = conf.get("application_installer", None)
        ai = ApplicationInstaller(None, c)
        application_installed = ai.run(split_subgraphs)

if __name__ == "__main__":
    main()
