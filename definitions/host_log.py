import os, sys, logging, argparse
import time
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from definitions.process import Process
from iutils.etc import convert_to_seconds
from iutils.etc import convert_to_megabytes
from iutils.etc import convert_to_float

class HostLog:
    def __init__(self, hostname, timestamp):
        self.hostname = hostname
        self.timestamp = timestamp
        self.processes = {}
        self.code = {}

        self.stat = {}
        self.values = {}
        self.attack_flag = 0
        self.attack_step = None
        self.attack_name = None

        self.attack_flag_labeled = 0
        self.attack_step_labeled = None
        self.attack_name_labeled = None

        self.label = None
        self.labeled = None

    def set_code(self, name, code):
        self.code[name] = code

    def get_code(self, name):
        return self.code[name]

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
        logging.debug("A host log is set to {}".format(self.label))

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

    def add_feature_value(self, feature, val):
        self.stat[feature] = val

    def get_feature_value(self, feature):
        return self.stat.get(feature, None)

    def get_feature_names(self):
        return list(self.stat)

    def get_hostname(self):
        return self.hostname

    def get_timestamp(self):
        return self.timestamp

    def add_key_value(self, category, key, value):
        feature = None
        if category == "prc":
            if key == "sys":
                value = convert_to_seconds(value)
                feature = "cpu_running_time_on_system_mode"
            elif key == "user":
                value = convert_to_seconds(value)
                feature = "cpu_running_time_on_user_mode"
            elif key == "#proc":
                value = int(value)
                feature = "number_of_open_processes"
            elif key == "#zombie":
                value = int(value)
                feature = "number_of_zombie_processes"
            elif key == "#trun":
                value = int(value)
                feature = "number_of_running_threads"
            elif key == "#tslpi":
                value = int(value)
                feature = "sleeping_uninterruptible"
            elif key == "clones":
                value = int(value)
                feature = "clone_system_call"
            elif key == "exit":
                value = int(value)
                feature = "number_of_exit_processes"
        elif category == "cpu":
            if key == "sys":
                if len(value) > 0 and value[-1] == "%":
                    value = value[:-1]
                value = int(value)
                feature = "cpu_utilization_on_kernel_mode"
            elif key == "user":
                if len(value) > 0 and value[-1] == "%":
                    value = value[:-1]
                value = int(value)
                feature = "cpu_utilization_on_user_mode"
            elif key == "irq":
                if len(value) > 0 and value[-1] == "%":
                    value = value[:-1]
                value = int(value)
                feature = "cpu_utilization_on_interrupt_handling"
            elif key == "wait":
                if len(value) > 0 and value[-1] == "%":
                    value = value[:-1]
                value = int(value)
                feature = "cpu_waiting_time_percentage"
            elif key == "steal":
                if len(value) > 0 and value[-1] == "%":
                    value = value[:-1]
                value = int(value)
                feature = "cpu_stolen_time_percentage"
            elif key == "idle":
                if len(value) > 0 and value[-1] == "%":
                    value = value[:-1]
                value = int(value)
                feature = "cpu_idle_time_percentage"
        elif category == "cpl":
            if key == "avg1":
                value = float(value)
                feature = "cpu_load_average_per_minute"
            elif key == "avg5":
                value = float(value)
                feature = "cpu_load_average_per_5_minutes"
            elif key == "avg15":
                value = float(value)
                feature = "cpu_load_average_per_15_minutes"
            elif key == "csw":
                value = convert_to_float(value)
                feature = "number_of_context_switching"
            elif key == "intr":
                value = convert_to_float(value)
                feature = "number_of_interrupt"

        elif category == "mem":
            if key == "tot":
                value = convert_to_megabytes(value)
                feature = "total_memory_megabytes"
            elif key == "free":
                value = convert_to_megabytes(value)
                feature = "total_free_memory_megabytes"
            elif key == "cache":
                value = convert_to_megabytes(value)
                feature = "page_cache_megabytes"
            elif key == "buff":
                value = convert_to_megabytes(value)
                feature = "filesystem_metadata"
            elif key == "slab":
                value = convert_to_megabytes(value)
                feature = "kernel_malloc"
        
        elif category == "swp":
            if key == "tot":
                value = convert_to_megabytes(value)
                feature = "total_swap_space_megabytes"
            elif key == "free":
                value = convert_to_megabytes(value)
                feature = "free_swap_space_megabytes"
            elif key == "vmcom":
                value = convert_to_megabytes(value)
                feature = "current_vm_space_megabytes"
            elif key == "vmlim":
                value = convert_to_megabytes(value)
                feature = "maximum_vm_space_megabytes"

        elif category == "dsk":
            if key == "busy":
                if len(value) > 0 and value[-1] == "%":
                    value = value[:-1]
                if "e" in value:
                    index = value.index("e")
                    base, exp = value[:index], value[index+1:]
                    value = base * 10 ** exp
                else:
                    value = int(value)
                feature = "disk_busy_time"
            elif key == "read":
                if "e" in value:
                    index = value.index("e")
                    base, exp = value[:index], value[index+1:]
                    value = base * 10 ** exp
                else:
                    value = int(value)
                feature = "read_request_throughput"
            elif key == "write":
                if "e" in value:
                    index = value.index("e")
                    base, exp = int(value[:index]), int(value[index+1:])
                    value = base * 10 ** exp
                else:
                    value = int(value)
                feature = "write_request_throughput"

        elif category == "net":
            if key == "tcpi":
                value = int(value)
                feature = "number_of_received_tcp_segments"
            elif key == "tcpo":
                value = int(value)
                feature = "number_of_transmitted_tcp_segments"
            elif key == "udpi":
                value = int(value)
                feature = "number_of_received_udp_datagrams"
            elif key == "udpo":
                value = int(value)
                feature = "number_of_transmitted_udp_datagrams"
            elif key == "icmpi":
                value = int(value)
                feature = "number_of_received_icmp_datagrams"
            elif key == "icmpo":
                value = int(value)
                feature = "number_of_transmitted_icmp_datagrams"
            elif key == "tcpao":
                value = int(value)
                feature = "number_of_active_tcp_open"
            elif key == "tcppo":
                value = int(value)
                feature = "number_of_passive_tcp_open"
            elif key == "tcprs":
                value = int(value)
                feature = "number_of_retransmission"

        if feature:
            self.values[feature] = value

    def get_values(self, key=None):
        if key:
            return self.values.get(key, -1)
        else:
            return self.values

    def add_process(self, pinfo):
        pid = int(pinfo[0])
        pname = pinfo[-1]
        timestamp = self.timestamp
        self.processes[pid] = Process(pname, timestamp, pinfo)

    def get_processes(self):
        return self.processes
