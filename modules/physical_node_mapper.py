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

class PhysicalNodeMapper(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize Physical Node Mapper")
        super().__init__(core, conf)
        self.scenario_description = None
        self.physical_node_information = None
        self.abstract_graph = None
        self.split_subgraphs = None

    def run(self, abstract_graph=None, physical_node_information=None):
        logging.info("Running the physical node mapper")
        if not abstract_graph:
            abstract_graph = self.get_abstract_graph()

        logging.debug("abstract_graph: {}".format(abstract_graph))

        if not physical_node_information:
            physical_node_information = self.get_physical_node_information()

        logging.debug("physical_node_information: {}".format(physical_node_information))

        logging.info(" - Checking whether the abstract graph and the physical node information are ready")
        if not abstract_graph or not physical_node_information:
            logging.error("To make split subnetworks, the abstract graph and the physical node information should be provided")
            logging.error("  abstract graph: {}".format(abstract_graph))
            logging.error("  physical node information: {}".format(physical_node_information))
            return None

        logging.info(" - Cleaning up resources")
        if not self._clean_up_resources(physical_node_information):
            logging.error("Fail to clean up the resources")
            return None

        logging.info(" - Collecting resource information about physical nodes")
        if not self._collect_resource_information(physical_node_information):
            logging.error("Unable to collect resource information from physical machines")
            return None

        return self._split_abstract_graph(abstract_graph, physical_node_information)

    def quit(self):
        logging.info(" - Quitting the physical node mapper")
        pni = self.get_physical_node_information()
        self._clean_up_resources(pni)

    def _clean_up_resources(self, pnodes):
        ret = True

        request = {}
        request["opcode"] = "execute"
        for pnode in pnodes:
            # 1. Remove the internet interface
            logging.info("  => Removing the \"internet\" interface")
            request["command"] = "ip link del internet"
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            # 2. Kill dnsmasq
            logging.info("  => Killing dnsmasq on a physical node")
            request["command"] = "killall dnsmasq"
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            # 3. Find the main interface toward the Internet
            logging.info("  => Finding the main interface toward the Internet")
            request["command"] = "which route"
            response = pnode.send_request(request)
            process_error(request, response)
            if len(response["stdout"].strip()) == 0 and len(response["stderr"].strip()) == 0:
                logging.debug("The iproute2 package is not installed")
                request["command"] = "apt-get install iproute2"
                response = pnode.send_request(request)
                process_error(request, response)

            request["command"] = "route -n"
            response = pnode.send_request(request)
            process_error(request, response)
            output = response["stdout"].split("\n")
            minterface = None
            for line in output:
                tokens = line.strip().split(" ")
                if tokens[0] == "0.0.0.0":
                    minterface = tokens[-1]
                    break
            logging.info("  => Setting the main interface to {}".format(minterface))
            self.set_pnode_main_interface(pnode, minterface)

            # 4. Remove the iptable rule set for the internet interface and the main interface
            logging.info("  => Removing the iptable rules")
            request["command"] = "iptables -t nat -D POSTROUTING -o {} -j MASQUERADE".format(minterface)
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            request["command"] = "iptables -D FORWARD -i {} -o internet -m state --state RELATED,ESTABLISHED -j ACCEPT".format(minterface)
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            request["command"] = "iptables -D FORWARD -i internet -o {} -j ACCEPT".format(minterface)
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            # 5. Remove all links of the pattern foo-tapX
            logging.info("  => Removing the tap interfaces")
            request["command"] = "ip link show | egrep -o [-_.[:alnum:]]+-tap[[:digit:]]+"
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            taps = response["stdout"].strip().split("\n")
            for tap in taps:
                request["command"] = "ip link del {}".format(tap)
                response = pnode.send_request(request)
                process_error(request, response, ignore=True)

            # 6. Remove all links of the pattern foo-brX
            logging.info("  => Removing the bridge interfaces")
            request["command"] = "ip link show | egrep -o [-_.[:alnum:]]+br[[:digit:]]+"
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            brs = response["stdout"].strip().split("\n")
            for br in brs:
                request["command"] = "ip link del {}".format(br)
                response = pnode.send_request(request)
                process_error(request, response, ignore=True)

        return ret

    def _collect_resource_information(self, pnodes):
        ret = True
        request = {}
        request["opcode"] = "report"
        for pnode in pnodes:
            logging.debug("request: {}".format(request))
            response = pnode.send_request(request)
            logging.debug("response: {}".format(response))
            pnode.set_resource("cpu", response["resource"]["cpu"])
            pnode.set_resource("memory", response["resource"]["memory"])
            pnode.set_working_directory(response["wdir"])
            logging.debug("resource: cpu: {}, memory: {}".format(pnode.get_resource("cpu"), pnode.get_resource("memory")))
        return ret

    def _split_abstract_graph(self, abstract_graph, pnodes):
        num_of_pnodes = len(pnodes)
        logging.info(" - Spliting the abstracted graph into {} subgraphs according to the greedy algorithm".format(num_of_pnodes))
        logging.debug("num of physical machines: {}".format(num_of_pnodes))

        split_subgraphs = []
        vertex, edge = abstract_graph

        wlst = [abstract_graph]

        while len(wlst) > 0:
            rresources = self.__calculate_requirements(wlst)
            mresource, idx = self.__get_maximum_requirement(rresources)
            ret = self.__assign_subnetwork_to_machine(mresource, idx, pnodes)
            logging.debug("ret: {}".format(ret))
            if not ret:
                graph = wlst[idx]
                subgraph1, subgraph2 = self.__split_into_smaller_networks(graph)

                if subgraph1:
                    wlst.append(subgraph1)

                if subgraph2:
                    wlst.append(subgraph2)
            else:
                graph = wlst.pop(ret[0])
                split_subgraphs.append((graph, pnodes[ret[1]]))

        logging.debug("split_subgraphs: {}".format(split_subgraphs))
        return split_subgraphs

    def __calculate_requirements(self, wlst):
        ret = []
        for subgraph in wlst:
            vertex, edge = subgraph
            ncpu = 0
            nmem = 0

            for v in vertex:
                resource = vertex[v].get_specification()
                logging.debug("resource: {}".format(resource))
                ncpu += 1
                mem = resource["memory"]
                num = 0
                exist = False
                for idx in range(len(mem)):
                    m = mem[idx].lower()
                    if m in ["k", "m", "g", "t"]:
                        num = int(mem[:idx])

                        if m == "k":
                            mem = num * 2 ** 10
                        elif m == "m":
                            mem = num * 2 ** 20
                        elif m == "g":
                            mem = num * 2 ** 30
                        elif m == "t":
                            mem = num * 2 ** 40
                        exist = True
                        break

                if not exist:
                    mem = int(mem)
                nmem += mem
            logging.debug("ncpu: {}, nmem: {}".format(ncpu, nmem))
            ret.append((ncpu, nmem))
        return ret

    def __get_maximum_requirement(self, rresources):
        midx = 0
        mcpu = 0
        mmem = 0       
        mresource = (0, 0)
        for idx in range(len(rresources)):
            ncpu, nmem = rresources[idx]
            if ncpu > mcpu:
                mcpu = ncpu
                midx = idx
            elif ncpu == mcpu:
                if nmem > mmem:
                    mmem = nmem
                    midx = idx

        mresource = rresources[midx]
        return mresource, midx

    def __assign_subnetwork_to_machine(self, mresource, gidx, pnodes):
        midx = -1
        gcpu = -1
        gmem = -1
        
        ret = None
        logging.debug("mresource: {}".format(mresource))
        rcpu, rmem = mresource
        for idx in range(len(pnodes)):
            pnode = pnodes[idx]
            acpu = pnode.get_resource("cpu")
            amem = pnode.get_resource("memory")
            logging.debug("acpu: {}, amem: {}".format(acpu, amem))
            dcpu = acpu - rcpu
            dmem = amem - rmem

            if gcpu < 0 and gmem < 0 and dcpu > 0 and dmem > 0:
                gcpu = dcpu
                gmem = dmem
                midx = idx
            elif gcpu > 0 and dcpu > 0 and dcpu < gcpu and gmem > 0 and dmem > 0 and dmem < gmem:
                gcpu = dcpu
                gmem = dmem
                midx = idx

        if midx >= 0:
            ret = (gidx, midx)

        return ret
        
    def __split_into_smaller_networks(self, graph):
        pass


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

    c = conf.get("network_abstractor", None)
    na = NetworkAbstractor(None, c)
    abstract_graph = na.run(scenario_description)

    c = conf.get("physical_node_mapper", None)
    pnm = PhysicalNodeMapper(None, c)
    split_subgraphs = pnm.run(abstract_graph, physical_node_information)
    logging.debug("split subgraphs: {}".format(split_subgraphs))

if __name__ == "__main__":
    main()
