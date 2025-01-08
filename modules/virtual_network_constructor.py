import os, sys, argparse, logging
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
from modules.scenario_verifier import ScenarioVerifier
from modules.network_abstractor import NetworkAbstractor
from modules.physical_node_mapper import PhysicalNodeMapper

class VirtualNetworkConstructor(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize VirtualNetworkConstructor")
        super().__init__(core, conf)
        self.abstract_graph = None
        self.physical_node_information = None
        self.minterface = None

    def run(self, split_subgraphs=None):
        logging.info("Running the virtual network constructor")
        if not split_subgraphs:
            split_subgraphs = self.get_split_subgraphs()
        logging.debug("split subgraphs: {}".format(split_subgraphs))

        if not split_subgraphs:
            logging.error("To make a virtual network, the split subgraphs should be provided")
            logging.error("  split_subgraphs: {}".format(split_subgraphs))
            return None
        return self._make_virtual_network(split_subgraphs)

    def quit(self):
        logging.info(" - Quitting the virtual network constructor")
        split_subgraphs = self.get_split_subgraphs()

        for subgraph, pnode in split_subgraphs:
            vertex, edge = subgraph
            for v in vertex:
                node = vertex[v]
                if node:
                   node.stop()

    def _make_virtual_network(self, split_subgraphs):
        virtual_network_constructed = False

        # TODO: how to interconnect routers should be implemented
        
        for subgraph, pnode in split_subgraphs:
            logging.debug("subgraph: {}".format(subgraph))
            logging.debug("pnode: {}".format(pnode))
            
            vertex, edge = subgraph
            routers = []
            devices = []
            externals = []

            logging.info(" - Making a subgraph on {}".format(pnode.get_name()))
            for v in vertex:
                vertex[v].set_configuration(self.config)
                vertex[v].set_pnode(pnode)
                vertex[v].configure()
                ntype = vertex[v].get_node_type()
                if ntype == "router":
                    routers.append(vertex[v])
                elif ntype == "device":
                    devices.append(vertex[v])
                elif ntype == "external":
                    externals.append(vertex[v])

            # 1. Make the internet interface first
            logging.info("  => Making the internet interface on {}".format(pnode.get_name()))
            iname = "internet"
            ipaddr = "172.31.0.1"
            low = "172.31.0.2"
            high = "172.31.255.255"
            nbits = 16

            request = {}
            request["opcode"] = "execute"

            # 1-1) Update the apt-get list
            request["command"] = "apt-get update"
            request["capture"] = False
            response = pnode.send_request(request)
            process_error(request, response)

            # 1-2) Make the internet interface
            request["command"] = "ip link add {} type bridge".format(iname)
            request["capture"] = True
            response = pnode.send_request(request)
            process_error(request, response)

            # 1-3) Turn on the internet interface
            request["command"] = "ip link set {} up".format(iname)
            request["capture"] = True
            response = pnode.send_request(request)
            process_error(request, response)

            # 1-4) Add the address to the internet interface
            request["command"] = "ip addr add {}/{} dev {}".format(ipaddr, nbits, iname)
            request["capture"] = True
            response = pnode.send_request(request)
            process_error(request, response)

            # 1-5) Check if the physical node installed dnsmasq
            logging.info("  => Running the dnsmasq on {}".format(pnode.get_name()))
            request["command"] = "which dnsmasq"
            request["capture"] = True
            response = pnode.send_request(request)
            process_error(request, response)
            if "dnsmasq" not in response["stdout"].split("/"):
                request["command"] = "apt-get install dnsmasq"
                request["capture"] = False
                response = pnode.send_request(request)
                process_error(request, response)
            else:
                logging.debug("dnsmasq is already installed in the physical machine")

            # 1-6) Run the dnsmasq
            lh = self.config.get("lease_hours", "12h")
            minterface = self.get_pnode_main_interface(pnode)
            if not minterface:
                minterface = self.minterface

            if minterface:
                request["command"] = "dnsmasq --interface=internet --except-interface={} --bind-interfaces --listen-address={} --dhcp-range={},{},{} --port=0".format(minterface, ipaddr, low, high, lh)
            else:
                request["command"] = "dnsmasq --interface=internet --bind-interfaces --listen-address={} --dhcp-range={},{},{} --port=0".format(ipaddr, low, high, lh)
            request["capture"] = True
            response = pnode.send_request(request)
            process_error(request, response)

            # TODO: need to recover it at the last time
            if response["returncode"] == 2:
                request["command"] = "mv /etc/dnsmasq.conf /etc/dnsmasq.conf.bak"
                request["capture"] = True
                response = pnode.send_request(request)
                process_error(request, response)

                if minterface:
                    request["command"] = "dnsmasq --interface=internet --except-interface={} --bind-interfaces --listen-address={} --dhcp-range={},{},{} --port=0".format(minterface, ipaddr, low, high, lh)
                else:
                    request["command"] = "dnsmasq --interface=internet --bind-interfaces --listen-address={} --dhcp-range={},{},{} --port=0".format(ipaddr, low, high, lh)
                request["capture"] = True
                response = pnode.send_request(request)
                process_error(request, response)

            # 1-7) Configure the IPv4 forwarding
            logging.info("  => Configuring the network setting on {}".format(pnode.get_name()))
            request["command"] = "sysctl -w net.ipv4.ip_forward=1"
            request["capture"] = True
            response = pnode.send_request(request)
            process_error(request, response)

            # 1-8) Configure the iptables
            request["command"] = "iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format(minterface)
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "iptables -A FORWARD -i {} -o internet -m state --state RELATED,ESTABLISHED -j ACCEPT".format(minterface)
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "iptables -A FORWARD -i internet -o {} -j ACCEPT".format(minterface)
            response = pnode.send_request(request)
            process_error(request, response)

            # 1-9) Make the directory for the nodes
            logging.info("  => Making the working directory on {}".format(pnode.get_name()))
            idir = self.config.get("image_directory", "extensibility")
            image_directory = "{}/{}".format(pnode.get_working_directory(), idir)
            request["command"] = "mkdir -p {}/dtb {}/kernels {}/rootfs {}/firmware".format(image_directory, image_directory, image_directory, image_directory)
            response = pnode.send_request(request)
            process_error(request, response)

            # 5. Make links
            logging.info("  => Making the links on {}".format(pnode.get_name()))
            logging.debug("edge: {}".format(edge))
            created = {}
            for v in vertex:
                created[v] = {}
                created[v]["internet"] = 0
                for w in vertex:
                    created[v][w] = 0

            for e in edge:
                for f in edge[e]:
                    if edge[e][f] and created[e][f] == 0:
                        logging.debug("Create a link between {} and {}".format(e, f))
                        edge[e][f].create()
                        created[e][f] = 1
                        if f != "internet":
                            created[f][e] = 1

            # 2. Make routers first (install and configure packages related to networking such as hostapd or dnsmasq)
            logging.info("  => Making routers and running them on {}".format(pnode.get_name()))
            for router in routers:
                router.start()
                    
            # 3. Make devices
            logging.info("  => Making devices and running them on {}".format(pnode.get_name()))
            for device in devices:
                device.start()

            # 4. Make externals
            logging.info("  => Making externals and running them on {}".format(pnode.get_name()))
            for external in externals:
                external.start()

        # 6. Interconnect subgraphs using the GRE tunneling

        virtual_network_constructed = True
        return virtual_network_constructed

    def set_main_interface(self, minterface):
        self.minterface = minterface

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-s", "--scenario-description", metavar="<scenario description file>", help="Scenario description file", type=str, required=True)
    parser.add_argument("-p", "--physical-node-information", metavar="<scenario description file>", help="Scenario description file", type=str, required=True)
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
    virtual_network_constructed = vnc.run(split_subgraphs)
    logging.info("virtual network constructed: {}".format(virtual_network_constructed))

if __name__ == "__main__":
    main()
