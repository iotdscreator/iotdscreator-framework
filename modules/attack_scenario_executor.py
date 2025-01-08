import os, sys, argparse, logging
import yaml
import pathlib
import time
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
from modules.virtual_network_constructor import VirtualNetworkConstructor
from modules.application_installer import ApplicationInstaller
from helpers.packet_capturer.packet_capturer import PacketCapturer
from helpers.host_data.host_info_manager import HostInfoManager
from definitions.attack import Attack

ADDITIONAL_TIME = 5

class AttackScenarioExecutor(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize AttackScenarioExecutor")
        super().__init__(core, conf)
        self.names = self.get_names()
        self.nodes = {}
        c = conf.get("host_info_manager", None)

        default_ipaddr = self.names.get("default", "0.0.0.0")
        default_port = 10200
        if not c:
            c = {}

        if "name" not in c:
            c["name"] = default_ipaddr

        if c["name"] == "default":
            c["name"] = default_ipaddr

        if "port" not in c:
            c["port"] = default_port

        self.names["host_info_manager-address"] = c["name"]
        self.names["host_info_manager-port"] = c["port"]
        self.host_info_manager = HostInfoManager(c)

    def run(self, split_subgraphs=None, attack_scenario=None, dataset_feature=None):
        logging.info("Running the attack scenario executor")
        logging.info(" - Running the host info manager")
        self.host_info_manager.set_output_file_prefix(self.get_output_file_prefix())
        self.host_info_manager.set_output_directory(self.get_output_directory())
        self.host_info_manager.run()

        if not split_subgraphs:
            split_subgraphs = self.get_split_subgraphs()

        if not attack_scenario:
            scenario_description = self.get_scenario_description()
            attack_scenario = scenario_description["attack_scenario"]

        if not dataset_feature:
            scenario_description = self.get_scenario_description()
            dataset_feature = scenario_description["dataset_feature"]

        if not split_subgraphs or not attack_scenario or not dataset_feature:
            logging.error("To execute the attack scenario, the scenario_description should be provided")
            logging.error("  attack_scenario: {}".format(attack_scenario))
            logging.error("  dataset_feature: {}".format(dataset_feature))
            return None

        logging.debug("dataset_feature: {}".format(dataset_feature))

        return self._run_attack_scenario(split_subgraphs, attack_scenario, dataset_feature)

    def quit(self):
        logging.info(" - Quitting the attack scenario executor")
        self.host_info_manager.quit()

    def _run_attack_scenario(self, split_subgraphs, attack_scenario, dataset_feature):
        attack_scenario_executed = False
        interfaces = dataset_feature.get("interfaces", {})

        # TODO: need to add the attacker's interfaces
        # Find it from the attack_scenario's attackers

        ilst = []
        for interface in interfaces:
            self.add_interface_of_interest(interface["name"])
            try:
                ilst.append(interface["name"])
            except:
                continue

        attacks = attack_scenario.get("attacks", [])
        for attack in attacks:
            try:
                ilst.append(attack["attacker"])
            except:
                continue
        
        hostnames = dataset_feature.get("hostnames", {})
        for hostname in hostnames:
            self.add_hostname_of_interest(hostname["name"])

        pcs = []
        logging.debug("interfaces: {}".format(interfaces))
        node = None
        aapps = []
        lst = attack_scenario["attacks"]
        for e in lst:
            aapps.append(e["type"])

        # TODO: When and how a user specifies the interfaces of his/her interest should be determined
        for subgraph, pnode in split_subgraphs:
            vertex, edge = subgraph

            #1. Start dumping packets
            logging.info(" - Staring capturing packets")
            for v in vertex:
                node = vertex[v]
                self.nodes[node.get_name()] = node
                if node.get_name() in ilst:
                    intfs = node.get_interfaces()

                    for idx in intfs:
                        interface = intfs[idx].get_external_ifname()
                        pcs.append(PacketCapturer(dataset_feature, pnode, node.get_name(), interface))
            minterface = self.get_pnode_main_interface(pnode)
            self.add_interface_of_interest(minterface)
            if not minterface:
                minterface = self.minterface
            pcs.append(PacketCapturer(dataset_feature, pnode, "internet", minterface))

            #2. Start collecting host information
            logging.info(" - Running the host info reporter on {}".format(node.get_name()))
            params = {}
            params["device name"] = node.get_name()
            params["address"] = self.names["host_info_manager-address"]
            params["port"] = self.names["host_info_manager-port"]
            params["application"] = "atop"
            conf = self.config.get("host_info_manager", None)
            interval = 10
            if conf:
                interval = conf.get("interval", 10)
            params["interval"] = interval
            node.run_host_info_reporter(**params)
            
            #3. Run applications 
            apps = node.get_applications()
            vtype = node.get_virtualization_type()
            os = node.get_operating_system()
            arch = node.get_architecture()
            for app in apps:
                if app.get_application_type() in aapps:
                    continue
                cmds = app.run_application(arch=arch, os=os)
                request = {}
                request["name"] = node.get_name()
                request["shell"] = node.get_shell_prompts()

                for cmd in cmds:
                    request["opcode"] = "control"
                    request["type"] = vtype
                    request["command"] = cmd
                    response = pnode.send_request(request)

            # Add the main interface of each physical node by default
            self.add_interface_of_interest(minterface)

        #4. Perform attacks according to the attack scenario
        logging.info(" - Starting capturing packets")
        self.__start_capturing_packets(pcs)
        alst = self.__init_attack_list(attack_scenario)
        for attack in alst:
            attack.set_start_time(self.start_time)
        alst.sort(key = lambda x: x.get_start_time())
        logging.debug("start_capturing_time: {}, start_time: {}".format(self.start_capturing_time, self.start_time))

        curr = int(time.time())
        logging.info(" - Running the attack scenario at {} for {} seconds".format(self.start_time, self.end_time - self.start_time))
        while curr < self.end_time:
            logging.debug("curr: {}, self.end_time: {}".format(curr, self.end_time))
            for attack in alst:
                if attack.is_finished():
                    continue

                if attack.is_performed():
                    if curr > attack.get_end_time():
                        attack.set_finished()
                    continue

                if curr > attack.get_start_time():
                    logging.info(" - Performing the attack ({}) at {}".format(attack.get_attack_type(), curr))
                    attacker = attack.get_attacker()
                    vtype = attack.get_virtualization_type()
                    pnode = attack.get_pnode()
                    cmds = attack.perform_attack()
                    shell_prompts = attack.get_shell_prompts()
                
                    request = {}
                    request["name"] = attacker
                    request["shell"] = shell_prompts
                    for cmd in cmds:
                        request["opcode"] = "control"
                        request["type"] = vtype
                        request["command"] = cmd
                        response = pnode.send_request(request)
                        process_error(request, response)
                    attack.set_performed()
            time.sleep(0.5)
            curr = int(time.time())

        time.sleep(ADDITIONAL_TIME)

        logging.info(" - Finishing capturing packets")
        self.__finish_capturing_packets(pcs)
        
        hlogs = self.host_info_manager.get_host_log_files()
        for hostname in hlogs:
            hname = hlogs[hostname]
            hostname = hname.strip().split("/")[-1]
            hostname = hostname.strip().split(".")[0]
            hostname = "-".join(hostname.split("-")[1:-1])
            self.add_host_log_file(hostname, hname)
            self.add_hostname_of_interest(hostname)

        ofprefix = self.get_output_file_prefix()
        odir = self.get_output_directory()
        tname = "{}/{}-timetable-{}.csv".format(odir, ofprefix, self.start_capturing_time)

        with open(tname, "w") as tf:
            for attack in alst:
                attack.set_end_time(self.end_time)
                tf.write(attack.output())
        self.add_time_table_file(tname)

        attack_scenario_executed = True
        return attack_scenario_executed

    def __start_capturing_packets(self, pcs):
        self.start_capturing_time = int(time.time())
        self.host_info_manager.set_capture_timestamp(self.start_capturing_time)
        self.set_capture_timestamp(self.start_capturing_time)
        for pc in pcs:
            logging.info("  => Capturing at {}".format(pc.get_interface_name()))
            pc.run(self.start_capturing_time)

    def __finish_capturing_packets(self, pcs):
        for pc in pcs:
            logging.info("  => Stopping capturing at {}".format(pc.get_interface_name()))
            pc.stop()
            time.sleep(1)
            pc.get()
            logging.info("  => Getting the captured file ({})".format(pc.get_network_log_filename()))
            nname = pc.get_network_log_filename()
            interface = nname.strip().split("/")[-1]
            interface = interface.strip().split(".")[0]
            tmp = interface.split("-")
            interface = "-".join(tmp[1:-1])
            self.add_network_log_file(interface, nname)
        self.end_capturing_time = int(time.time())

    def __init_attack_list(self, attack_scenario):
        alst = []
        scenario_length = attack_scenario["scenario_length"]
        attacks = attack_scenario["attacks"]
        for attack in attacks:
            name = attack.get("attacker", None)
            attacker = None
            nodes = self.nodes
            if name in nodes:
                attacker = nodes[name]
            else:
                logging.error("The attacker's name is not correctly specified")
                logging.error("Please check the name of the attacker in the attack scenario")
                sys.exit(1)
            logging.debug("name: {}, attacker: {}".format(name, attacker))
            begin = attack.get("begin", 0)
            atype = attack.get("type", "none")
            step = attack.get("step", "none")
            duration = attack.get("duration", 0)
            target = attack.get("target", "none")
            options = attack.copy()
            if "attacker" in options:
                del options["attacker"]
            if "target" in options:
                del options["target"]
            if "begin" in options:
                del options["begin"]
            if "type" in options:
                del options["type"]
            if "step" in options:
                del options["step"]
            if "duration" in options:
                del options["duration"]

            if target in self.nodes:
                interfaces = self.nodes[target].get_interfaces()
                intf = interfaces[0]
                ipaddr = intf.get_ipaddr()
                target = ipaddr
            logging.info("attacker: {}, target: {}, begin: {}, atype: {}, step: {}, duration: {}".format(attacker, target, begin, atype, step, duration))
            alst.append(Attack(attacker, target, begin, atype, step, duration, **options))

            self.start_time = start = int(time.time())
            self.end_time = self.start_time + scenario_length + ADDITIONAL_TIME
        return alst
    
    def set_main_interface(self, minterface):
        self.minterface = minterface

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

    logging.info("Test> Scenario Verifier")
    conf = load_configuration_file(args.config, "..")
    c = conf.get("scenario_verifier", None)
    sv = ScenarioVerifier(None, c)
    scenario_description, physical_node_information = sv.run(args.scenario_description, args.physical_node_information)

    logging.info("Test> Network Abstractor")
    c = conf.get("network_abstractor", None)
    na = NetworkAbstractor(None, c)
    abstract_graph = na.run(scenario_description)

    logging.info("Test> Physical Node Mapper")
    c = conf.get("physical_node_mapper", None)
    pnm = PhysicalNodeMapper(None, c)
    split_subgraphs = pnm.run(abstract_graph, physical_node_information)

    logging.info("Test> Virtual Network Constructor")
    c = conf.get("virtual_network_constructor", None)
    vnc = VirtualNetworkConstructor(None, c)
    vnc.set_main_interface(args.main_interface)
    virtual_network_constructed = vnc.run(split_subgraphs)

    if virtual_network_constructed:
        logging.info("Test> Application Installer")
        c = conf.get("application_installer", None)
        ai = ApplicationInstaller(None, c)
        application_installed = ai.run(split_subgraphs)

    if application_installed:
        logging.info("Test> Attack Scenario Executor")
        c = conf.get("attack_scenario_executor", None)
        ase = AttackScenarioExecutor(None, c)
        ase.set_main_interface(args.main_interface)
        attack_scenario = scenario_description["attack_scenario"]
        dataset_feature = scenario_description["dataset_feature"]
        attack_scenario_executed = ase.run(split_subgraphs, attack_scenario, dataset_feature)

    if attack_scenario_executed:
        logging.info("Test> Attack Scenario is well Executed")
    

if __name__ == "__main__":
    main()
