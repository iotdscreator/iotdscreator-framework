import os, sys, argparse, logging
import yaml
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from modules.module import Module
from modules.scenario_verifier import ScenarioVerifier
from definitions.node import Node
from definitions.edge import Edge
from nodes.interfaces.dummy_intf import DummyIntf

class NetworkAbstractor(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize Network Abstractor")
        super().__init__(core, conf)

    def run(self, scenario_description=None):
        logging.info("Running the network abstractor")
        logging.debug("Making an abstract graph according to the scenario description")

        if not scenario_description:
            scenario_description = self.get_scenario_description()

        if not scenario_description:
            logging.error("The scenario description should be provided")
            logging.error("  scenario_description: {}".format(scenario_description))
            return None
        return self._make_abstract_graph(scenario_description["network_configuration"])

    def quit(self):
        logging.info(" - Quitting the network abstractor")
        pass

    def _make_abstract_graph(self, network_configuration):
        vertex = {}
        logging.info(" - Loading nodes from the scenario description")
        nodes = network_configuration["node"]
        for ntype in nodes:
            for n in nodes[ntype]:
                n_name = n.get("name", None)
                if n_name:
                    vertex[n_name] = Node(n, ntype)

        edge = {}
        logging.info(" - Loading links from the scenario description")
        links = network_configuration.get("link", None)
        for m in vertex:
            edge[m] = {}
            for n in vertex:
                edge[m][n] = None

        if links:
            logging.info("  => Verifying configurations of links")
            for link in links:
                n1_name = link.get("node1", None)
                n2_name = link.get("node2", None)

                error = False
                reason = None
                if n1_name == None and n2_name == None:
                    error = True
                    reason = "Both vertice are None"
                elif n1_name == None and n2_name not in vertex:
                    error = True
                    reason = "One vertex is None and the other is not in the vertice set"
                elif n1_name not in vertex and n2_name == None:
                    error = True
                    reason = "One vertex is None and the other is not in the vertice set"
                elif n1_name not in vertex and n2_name not in vertex:
                    error = True
                    reason = "Both vertice are not in the vertice set"

                if error:
                    logging.error("Weird link as n1_name is {} and n2_name is {}".format(n1_name, n2_name))
                    logging.error("Reason: {}".format(reason))
                    logging.error("Please check your scenario file and try agains")
                    sys.exit(1)

                if n1_name == None:
                    n1_name = "internet"
                elif n2_name == None:
                    n2_name = "internet"

                # if we want to set up one interface to access the Internet, we will let the interface name be "internet" 
                # and its corresponding node to be None
                n1 = vertex.get(n1_name, None)
                n2 = vertex.get(n2_name, None)

                i1_name = link.get("intf1", None)
                i2_name = link.get("intf2", None)

                # if i1_name or i2_name is "internet", then the its corresponding node must be None; 
                # therefore, we do not need to care about the case
                i1 = None
                i2 = None

                if n1:
                    if i1_name:
                        i1 = n1.get_interface(i1_name)
                    else:
                        logging.error("The interface name is not specified for the node {}".format(n1.get_name()))
                        sys.exit(1)

                    if not i1:
                        logging.error("There is no interface with the name {} in the node {}".format(i1_name, n1_name))
                        sys.exit(1)

                if n2:
                    if i2_name:
                        i2 = n2.get_interface(i2_name)
                    else:
                        logging.error("The interface name is not specified for the node {}".format(n2.get_name()))
                        sys.exit(1)

                    if not i2:
                        logging.error("There is no interface with the name {} in the node {}".format(i2_name, n2_name))
                        sys.exit(1)

                if not i1:
                    i1 = DummyIntf(None, i1_name, 0)

                if not i2:
                    i2 = DummyIntf(None, i2_name, 0)

                l = Edge(link["type"], n1, i1, n2, i2)

                if n1_name != "internet" and n2_name != "internet":
                    edge[n1_name][n2_name] = l
                    edge[n2_name][n1_name] = l
                elif n1_name == "internet":
                    edge[n2_name][n1_name] = l
                elif n2_name == "internet":
                    edge[n1_name][n2_name] = l

        logging.info(" - Generating an abstracted graph")
        abstract_graph = (vertex, edge)

        return abstract_graph

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-s", "--scenario-description", metavar="<scenario description file>", help="Scenario description file", type=str, required=True)
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
    scenario_description, _ = sv.run(args.scenario_description, None)

    c = conf.get("network_abstractor", None)
    na = NetworkAbstractor(None, c)

    abstract_graph = na.run(scenario_description)
    logging.info("abstract graph: {}".format(abstract_graph))

if __name__ == "__main__":
    main()
