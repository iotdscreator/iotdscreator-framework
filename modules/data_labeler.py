import os, sys, argparse, logging, time
import copy, dpkt, socket, json
from scapy.all import rdpcap
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from modules.module import Module
from modules.scenario_verifier import ScenarioVerifier
from modules.network_abstractor import NetworkAbstractor
from modules.physical_node_mapper import PhysicalNodeMapper
from modules.virtual_network_constructor import VirtualNetworkConstructor
from helpers.host_data.host_info_processor import HostInfoProcessor

class DataLabeler(Module):
    def __init__(self, core, conf):
        logging.debug("Initialize DataLabeler")
        super().__init__(core, conf)
        self.interfaces = []
        self.network_log_files = {}
        self.network_label_files = {}

        self.attacks = {}
        self.atk_packets = {}
        self.gw_packets = {}
        self.processed_logs = {}

        self.zitter = conf.get("zitter", 1)

        self.hostnames = []
        self.host_log_files = {}
        self.host_label_files = {}
        self.host_info_processor = HostInfoProcessor(None)

    def add_atk_packets(self, packet_ip_id, timestamp, attack_name, attack_step, src_ip, dst_ip, ip_protocol, packet_info):
        if packet_ip_id != -1:
            if not packet_ip_id in self.atk_packets:
                self.atk_packets[packet_ip_id] = []
            self.atk_packets[packet_ip_id].append((attack_name, attack_step, src_ip, dst_ip, timestamp, ip_protocol, packet_info))
        else:
            if not ip_protocol in self.atk_packets:
                self.atk_packets[ip_protocol] = []
            self.atk_packets[ip_protocol].append((attack_name, attack_step, src_ip, dst_ip, timestamp, ip_protocol, packet_info))

    def packet_preprocessing(self, pkt_data):
        packet_info = str(pkt_data).split("\\")[1:]
        packet_info = f"{packet_info}"
        packet_info = packet_info[1:-1]
        packet_info = packet_info.replace("\"", "").replace(",","").replace("\'", "").replace(" ", "")
        # print(packet_info)
        return packet_info

    def get_transport_protocol(self, eth):
        ip = eth.data
        try:
            ip.data.sum = 0x0000
        except:
            pass

        transport_protocol = ip.data
        try:
            if isinstance(transport_protocol, dpkt.tcp.TCP):
                packet_info = self.packet_preprocessing(transport_protocol)
                return "TCP", packet_info
            
            elif isinstance(transport_protocol, dpkt.udp.UDP):
                packet_info = self.packet_preprocessing(transport_protocol.data)
                return "UDP", packet_info
            
            elif isinstance(transport_protocol, dpkt.icmp.ICMP):
                packet_info = self.packet_preprocessing(transport_protocol)
                return "ICMP", packet_info
            
            elif isinstance(transport_protocol, dpkt.igmp.IGMP):
                packet_info = self.packet_preprocessing(transport_protocol)
                return "IGMP", packet_info
            
            elif eth.type == dpkt.ethernet.ETH_TYPE_ARP:
                packet_info = self.packet_preprocessing(ip)
                return "ARP", packet_info
            
            else:
                return "Unknown", -1

        except Exception as e:
            logging.error(f"Error (transport): {e}")
            return None

    def label_network_data(self):
        logging.debug("network log files: {}".format(self.network_log_files))
        logging.debug("attacks: {}".format(self.attacks))
        attackers = list(self.attacks.keys())
        zitter = self.zitter
        for interface in self.network_log_files:
            logging.debug("interface: {}, attackers: {}".format(interface, attackers))
            if is_attacker_interface(attackers, interface):
                attacker = get_attacker_name(attackers, interface)
                logging.debug("attacker: {}".format(attacker))
                with open(self.network_log_files[interface], 'rb') as file:
                    logging.debug("attacker: {} ({})".format(attacker, self.network_log_files[interface]))
                    pcap = dpkt.pcap.Reader(file)
                    num = 0
                    for _, _ in pcap:
                        num += 1
                    logging.info("# of packets: {}".format(num))

                with open(self.network_log_files[interface], 'rb') as file:
                    pcap = dpkt.pcap.Reader(file)
                    cnt = 0
                    for timestamp, packet_data in pcap:
                        eth = dpkt.ethernet.Ethernet(packet_data)
                        ip = eth.data
                        try:
                            ip_id = ip.id
                            src_ip = socket.inet_ntoa(ip.src)
                            dst_ip = socket.inet_ntoa(ip.dst)
                            ip_protocol, packet_info = self.get_transport_protocol(eth)
                            # print(f"Timestamp: {timestamp}, IP ID: {ip_id}")
                            atk_packet = None
                            for type in self.attacks[attacker]:
                                logging.debug("type (try): {} ({})".format(type, timestamp))
                                if 0 - zitter < timestamp - float(type[2]) < float(type[3]) + zitter:
                                    logging.debug("  => dst_ip: {}, type[0]: {} at {}".format(dst_ip, type[0], timestamp))

                                    if dst_ip == type[0]:
                                        logging.debug("  => selected at {} as {} ({})".format(timestamp, type[1], type[4]))
                                        atk_packet = (ip_id, timestamp, type[1], type[4], src_ip, dst_ip, ip_protocol, packet_info)
                            if atk_packet:
                                logging.debug("  => added at {} as {} ({})".format(atk_packet[1], atk_packet[2], atk_packet[3]))
                                self.add_atk_packets(atk_packet[0], atk_packet[1], atk_packet[2], atk_packet[3], atk_packet[4], atk_packet[5], atk_packet[6], atk_packet[7])

                        except: # if "ip id" not exist : compare with packet information
                            try:
                                ip_protocol, packet_info = self.get_transport_protocol(eth)
                                atk_packet = None
                                for type in self.attacks[attacker]:
                                    logging.debug("type (except): {} ({})".format(type, timestamp))
                                    if 0 - zitter < timestamp - float(type[2]) < float(type[3]) + zitter:
                                        logging.debug("  => dst_ip: {}, type[0]: {} at {}".format(dst_ip, type[0], timestamp))

                                        if dst_ip == type[0]:
                                            logging.debug("  => selected at {} as {} ({})".format(timestamp, type[1], type[4]))
                                            atk_packet = (-1, timestamp, type[1], type[4], -1, -1, ip_protocol, packet_info)
                                if atk_packet:
                                    logging.debug("  => added at {} as {} ({})".format(atk_packet[1], atk_packet[2], atk_packet[3]))
                                    self.add_atk_packets(-1, timestamp, type[1], type[4], -1, -1, ip_protocol, packet_info)

                            except Exception as e:
                                logging.error(f"Error (interface): {e}")

                        cnt += 1
                        if cnt % 10000 == 0:
                            logging.info("{} packets are processed ({}/{})".format(cnt, cnt, num))

        logging.debug("# of attack packets: {}".format(len(self.atk_packets)))

        num = 1
        for interface in self.interfaces:
            logging.debug("self.network_log_files: {}, interface: {}, self.interfaces: {}".format(self.network_log_files, interface, self.interfaces))
            intfs = get_interfaces(list(self.network_log_files.keys()), interface)

            for intf in intfs:
                with open(self.network_log_files[intf], 'rb') as file:
                    pcap = dpkt.pcap.Reader(file)
                    for timestamp, packet_data in pcap:
                        eth = dpkt.ethernet.Ethernet(packet_data)
                        ip = eth.data
                        try:
                            ip_id = ip.id
                            src_ip = socket.inet_ntoa(ip.src)
                            dst_ip = socket.inet_ntoa(ip.dst)
                        
                            ip_protocol, packet_info = self.get_transport_protocol(eth)
                            info_lst = [num, timestamp, ip_protocol, ip_id, src_ip, dst_ip,'normal', 'benign', 0]
                            # print(info_lst)
                            if ip_id in self.atk_packets:
                                for pkt_info in self.atk_packets[ip_id]:
                                    if pkt_info[5] == ip_protocol:
                                    
                                        if 0 - zitter < (timestamp - pkt_info[4]) < 5 + zitter and pkt_info[6] == packet_info: # max delay 10s, packet info comparison
                                            info_lst[6] = pkt_info[0]
                                            info_lst[7] = pkt_info[1]
                                            info_lst[8] = 1
                        
                            if intf not in self.gw_packets:
                                self.gw_packets[intf] = []
                            self.gw_packets[intf].append(info_lst)
                        except:
                            try:
                                ip_protocol, packet_info = self.get_transport_protocol(eth)
                                info_lst = [-1, timestamp, ip_protocol, -1, -1, -1,'normal', 'benign', 0]
                                if ip_protocol in self.atk_packets:
                                    for pkt_info in self.atk_packets[ip_protocol]:
                                        # if ip_protocol == "ARP":
                                            # print(packet_info)
                                        if 0 - zitter < (timestamp - pkt_info[4]) < 5 + zitter and pkt_info[6] == packet_info: # max delay 10s, packet info comparison
                                            info_lst[6] = pkt_info[0]
                                            info_lst[7] = pkt_info[1]
                                            info_lst[8] = 1
                            
                                self.gw_packets[intf].append(info_lst)

                            except Exception as e:
                                logging.error(f"Error ({interface}): {e}")
                    
                        num += 1
                logging.info("intf: {}, self.gw_packets: {}".format(intf, self.gw_packets))
                logging.info("# of packets captured at {}: {}".format(intf, len(self.gw_packets[intf])))
        
        ret = self.write_network_label_files()
        return ret

    def write_network_label_files(self):
        ret = []
        sd = self.get_scenario_description()
        odir = root_directory
        if sd:
            odir = sd["dataset_feature"].get("output_directory", root_directory)
        odir = os.path.expanduser(odir)
        ofprefix = self.get_output_file_prefix()
        if not ofprefix:
            ofprefix = "noname"
        timestamp = self.get_capture_timestamp()
        if not timestamp:
            timestamp = "notimestamp"
        for interface in self.interfaces:
            intfs = get_interfaces(list(self.network_log_files.keys()), interface)

            for intf in intfs:
                lfname = "{}/{}-{}-{}-network.label".format(odir, ofprefix, intf, timestamp)

                try:
                    with open(lfname, 'w') as p:
                        p.write("index,timestamp,protocol,id,src_ip,dst_ip,attack_type,attack_step,attack_flag\n")
                        for pkt in self.gw_packets[intf]:
                            pkt_str = f"{pkt}"
                            pkt_str = pkt_str[1:-1]
                            pkt_str = pkt_str.replace("'","")
                            pkt_str = pkt_str.replace(" ","")
                            p.write(f"{pkt_str}\n")
                    pname = self.network_log_files[intf]
                    ret.append((pname, lfname))
                    self.add_network_label_file(intf, lfname)
                except:
                    continue
        return ret

    def label_host_data(self):
        hostnames = list(self.host_log_files.keys())

        #p.write("hostname,index,timestamp,attack_type,attack_step,attack_flag\n")
        host_log_files = self.host_log_files
        for hostname in host_log_files:
            alst = self.attacks.get(hostname, [])
            logging.debug("alst: {}".format(alst))
            hname = host_log_files[hostname]
            self.processed_logs[hostname] = {}

            idx = 0
            with open(hname, "r") as f:
                for line in f:
                    js = json.loads(line.strip())
                    data = js["data"]
                    host_log = self.host_info_processor.parse_atop_data(data)
                    timestamp = host_log["timestamp"]
                    processes = host_log["processes"]
                    attack_type = "benign"
                    attack_step = "benign"
                    attack_flag = 0
                    for proc in processes:
                        for attack in alst:
                            if proc == attack[1]:
                                ats = int(attack[2])
                                duration = int(attack[3])
                                if timestamp >= ats and timestamp < ats + duration:
                                    attack_type = attack[1]
                                    attack_step = attack[4]
                                    attack_flag = 1

                    log = "{},{},{},{},{},{}".format(hostname, idx, timestamp, attack_type, attack_step, attack_flag)
                    self.processed_logs[hostname][idx] = log
                    idx += 1

        # TODO: add logs about the victims

        ret = self.write_host_label_files()
        return ret

    def write_host_label_files(self):
        ret = []
        sd = self.get_scenario_description()
        odir = root_directory
        if sd:
            odir = sd["dataset_feature"].get("output_directory", root_directory)
        odir = os.path.expanduser(odir)
        ofprefix = self.get_output_file_prefix()
        if not ofprefix:
            ofprefix = "noname"
        timestamp = self.get_capture_timestamp()
        if not timestamp:
            timestamp = "notimestamp"
        
        hostnames = list(self.host_log_files.keys())
        for hostname in hostnames:
            lfname = "{}/{}-{}-{}-host.label".format(odir, ofprefix, hostname, timestamp)
            hname = self.host_log_files[hostname]
            try:
                with open(lfname, "w") as p:
                    p.write("hostname,index,timestamp,attack_type,attack_step,attack_flag\n")
                    logs = self.processed_logs[hostname]
                    for idx in logs:
                        p.write("{}\n".format(logs[idx]))
                ret.append((hname, lfname))
            except:
                continue
            self.add_host_label_file(hostname, lfname)
        return ret

    def run(self):
        logging.info("Running the data labeler")
        self.capture_timestamp = self.get_capture_timestamp()
        if not self.capture_timestamp:
            klst = list(self.network_log_files.keys())
            nname = self.network_log_files[klst[0]]
            logging.debug("nname: {}".format(nname))
            self.capture_timestamp = int(nname.split(".")[0].split("-")[-1])
        logging.debug("self.capture_timestamp: {}".format(self.capture_timestamp))
        logging.info(" - Labeling network data")
        ret1 = self.label_network_data()
        logging.debug("ret1: {}".format(ret1))
        logging.info(" - Labeling host data")
        ret2 = self.label_host_data()
        logging.debug("ret2: {}".format(ret2))
        return ret1 + ret2
                        
    def quit(self):
        logging.info(" - Quitting the data labeler")
        pass

    def add_network_log_file(self, interface, nname):
        self.network_log_files[interface] = nname
        logging.debug("self.network_log_files: {}".format(self.network_log_files))

    def add_host_log_file(self, hostname, hname):
        self.host_log_files[hostname] = hname
        logging.debug("self.host_log_files: {}".format(self.host_log_files))

    def add_time_table_file(self, tname):
        with open(tname, "r") as f:
            for line in f:
                attacker, target, attack_name, begin, duration, attack_step = line.strip().split(",")
                self.add_attack_info(attacker, target, attack_name, begin, duration, attack_step)

    def add_interface_of_interest(self, interface):
        self.interfaces.append(interface)

    def add_hostname_of_interest(self, hostname):
        self.hostnames.append(hostname)

    def add_attack_info(self, attacker, target, aname, begin, duration, attack_step):
        if not attacker in self.attacks:
            self.attacks[attacker] = []
        self.attacks[attacker].append((target, aname, begin, duration, attack_step))

    def set_capture_timestamp(self, timestamp):
        self.capture_timestamp = timestamp

def is_attacker_interface(attackers, interface):
    ret = False

    for attacker in attackers:
        if attacker in interface:
            ret = True

    return ret

def get_attacker_name(attackers, interface):
    ret = None

    for attacker in attackers:
        if attacker in interface:
            ret = attacker

    return ret

def get_interfaces(interfaces, intf):
    ret = []
    for interface in interfaces:
        if intf in interface:
            ret.append(interface)
    return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, metavar="<configuration file>", help="Configuration file", type=str)
    parser.add_argument("-p", "--network-logs", required=True, metavar="<filepath to the network log files>", help="File path to the network log files", type=str, nargs="+")
    parser.add_argument("-q", "--host-logs", required=True, metavar="<filepath to the host log files>", help="File path to the host log files", type=str, nargs="+")
    parser.add_argument("-i", "--interfaces", required=True, metavar="<interface of interest>", help="Interface of interest", type=str, nargs="+")
    parser.add_argument("-t", "--time-table", metavar="<attack time table file>", help="Attack time table file", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    for nname in args.network_logs:
        if not check_file_availability(nname):
            logging.error("The specified network log file does not exists: {}".format(nname))
            sys.exit(1)

    for hname in args.host_logs:
        if not check_file_availability(hname):
            logging.error("The specified host log file does not exists: {}".format(hname))
            sys.exit(1)

    if not check_file_availability(args.time_table):
        logging.error("The specified time table file does not exists: {}".format(args.time_table))
        sys.exit(1)

    conf = load_configuration_file(args.config, "..")
    c = conf.get("data_labeler", None)
    dl = DataLabeler(None, c)
    for nname in args.network_logs:
        interface = nname.strip().split("/")[-1]
        interface = interface.strip().split(".")[0]
        tmp = interface.split("-")
        timestamp = tmp[-1]
        interface = "-".join(tmp[1:-1])
        dl.add_network_log_file(interface, nname)
        dl.set_capture_timestamp(timestamp)

    for interface in args.interfaces:
        dl.add_interface_of_interest(interface)

    for hname in args.host_logs:
        hostname = hname.strip().split("/")[-1]
        hostname = hostname.strip().split(".")[0]
        hostname = "-".join(hostname.split("-")[1:-1])
        dl.add_host_log_file(hostname, hname)

    dl.add_time_table_file(args.time_table)

    dl.run()

if __name__ == "__main__":
    main()
