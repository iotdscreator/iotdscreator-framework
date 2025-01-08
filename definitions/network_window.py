import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.network import extract_flow_info
import numpy as np

class NetworkWindow:
    def __init__(self, protocol, saddr, sport, daddr, dport, window_length, dummy=False):
        self.packets = {}
        self.packets["forward"] = []
        self.packets["backward"] = []

        self.protocol = protocol
        self.saddr = saddr
        self.sport = sport
        self.daddr = daddr
        self.dport = dport
        self.window_length = window_length
        
        self.stat = {} # map: feature -> value
        self.code = None
        if dummy:
            self.dummy = True
        else:
            self.dummy = False

        self.attack_flag = 0
        self.attack_flag_labeled = 0

        self.attack_step = []
        self.attack_step_labeled = []

        self.attack_name = []
        self.attack_name_labeled = []

        self.window_start_time = None
        self.window_end_time = None
        self.serial = 0

        self.flow_info = {}
        self.flow_info["forward"] = "{}:{}-{}:{}".format(saddr, sport, daddr, dport)
        self.flow_info["backward"] = "{}:{}-{}:{}".format(daddr, dport, saddr, sport)

    def is_dummy(self):
        return self.dummy

    def get_protocol(self):
        return self.protocol

    def get_saddr(self):
        return self.saddr

    def get_sport(self):
        return self.sport

    def get_daddr(self):
        return self.daddr

    def get_dport(self):
        return self.dport

    def get_serial_number(self):
        return self.serial
    
    def set_serial_number(self, serial):
        self.serial = serial

    def get_flow_info(self, direction=None):
        if direction:
            return self.flow_info[direction]
        else:
            return self.flow_info

    def get_flow(self, direction):
        return self.flow[direction]

    def add_packet(self, pkt):
        protocol, saddr, sport, daddr, dport = pkt.get_each_flow_info()

        if self.flow["forward"].get_protocol() == protocol and self.flow["forward"].get_saddr() == saddr and self.flow["forward"].get_sport() == sport and self.flow["forward"].get_daddr() == daddr and self.flow["forward"].get_dport() == dport:
            self.packets["forward"].append(pkt)
        elif self.flow["backward"].get_protocol() == protocol and self.flow["backward"].get_saddr() == saddr and self.flow["backward"].get_sport() == sport and self.flow["backward"].get_daddr() == daddr and self.flow["backward"].get_dport() == dport:
            self.packets["backward"].append(pkt)

        if pkt.get_attack_flag() == 1:
            self.attack_flag = 1
            
            if pkt.get_attack_step() not in self.attack_step:
                self.attack_step.append(pkt.get_attack_step())

            if pkt.get_attack_name() not in self.attack_name:
                name = "{} ({})".format(pkt.get_attack_name(), pkt.get_attack_step())
                self.attack_name.append(name)

            logging.debug("Window is set to an attack window".format(self.attack_flag))


    def get_packets(self, direction):
        return self.packets[direction]

    def set_packets(self, direction, pkts):
        self.packets[direction] = pkts
        for p in pkts:
            if p.get_attack_flag() == 1:
                self.attack_flag = 1
                step = p.get_attack_step()
                if step not in self.attack_step:
                    self.attack_step.append(step)
                name = "{} ({})".format(p.get_attack_name(), p.get_attack_step())
                if name not in self.attack_name:
                    self.attack_name.append(name)

    def add_feature_value(self, feature, val):
        if feature not in self.stat:
            self.stat[feature] = 0
        self.stat[feature] = self.stat[feature] + val

    def get_feature_value(self, feature):
        return self.stat.get(feature, None)

    def get_feature_names(self):
        return list(self.stat)

    def get_window_length(self):
        return self.window_length

    def set_code(self, code):
        self.code = code

    def get_code(self):
        return [i for i in self.stat.values()]
        #return [self.code]

    def set_attack_flag(self, value):
        self.attack_flag = value

    def get_attack_flag(self):
        return self.attack_flag

    def set_attack_flag_labeled(self, value):
        self.attack_flag_labeled = value

    def get_attack_flag_labeled(self):
        return self.attack_flag_labeled

    def set_attack_step(self, value):
        self.attack_step = value

    def get_attack_step(self):
        return self.attack_step

    def set_attack_step_labeled(self, value):
        self.attack_step_labeled = value

    def get_attack_step_labeled(self):
        return self.attack_step_labeled

    def set_attack_name(self, value):
        self.attack_name = value

    def get_attack_name(self):
        return self.attack_name

    def set_attack_name_labeled(self, value):
        self.attack_name_labeled = value

    def get_attack_name_labeled(self):
        return self.attack_name_labeled

    def get_stat(self):
        return self.stat

    def set_times(self, start_time, end_time):
        self.window_start_time = start_time
        self.window_end_time = end_time

    def get_window_start_time(self):
        return self.window_start_time

    def get_window_end_time(self):
        return self.window_end_time

    def get_num_of_packets(self, kwd):
        ret = 0
        if kwd == "both":
            ret += len(self.packets["forward"] + self.packets["backward"])
        else:
            ret += len(self.packets[kwd])
        return ret

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()
