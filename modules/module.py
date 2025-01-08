import os
import logging 

class Module:
    def __init__(self, core, conf):
        self.core = core
        self.config = conf
        logging.debug("self.config in module: {}".format(self.config))

    def run(self):
        pass

    def get_names(self):
        ret = None
        if self.core:
            ret = self.core.get_names()
        return ret

    def get_root_directory(self):
        ret = None
        if self.core:
            ret = self.core.get_root_directory()
        else:
            ret = os.getcwd() + "/.."
        return ret

    def get_scenario_description(self):
        ret = None
        if self.core:
            ret = self.core.get_scenario_description()
        return ret

    def get_physical_node_information(self):
        ret = None
        if self.core:
            ret = self.core.get_physical_node_information()
        return ret

    def get_abstract_graph(self):
        ret = None
        if self.core:
            ret = self.core.get_abstract_graph()
        return ret

    def get_split_subgraphs(self):
        ret = None
        if self.core:
            ret = self.core.get_split_subgraphs()
        return ret

    def set_pnode_main_interface(self, pnode, interface):
        if self.core:
            self.core.set_pnode_main_interface(pnode, interface)
        else:
            if not hasattr(self, "minterfaces"):
                self.minterfaces = {}
            self.minterfaces[pnode.get_name()] = interface

    def get_pnode_main_interface(self, pnode):
        ret = None
        if self.core:
            ret = self.core.get_pnode_main_interface(pnode)
        else:
            if hasattr(self, "minterfaces"):
                ret = self.minterfaces[pnode.get_name()]
        return ret

    def get_network_log_filenames(self):
        ret = None
        if self.core:
            ret = self.core.get_network_log_filenames()
        return ret

    def get_network_label_filenames(self):
        ret = None
        if self.core:
            ret = self.core.get_network_label_filenames()
        return ret

    def get_host_log_filenames(self):
        ret = None
        if self.core:
            ret = self.core.get_host_log_filenames()
        return ret

    def get_host_label_filenames(self):
        ret = None
        if self.core:
            ret = self.core.get_host_label_filenames()
        return ret

    def set_output_directory(self, odir):
        if self.core:
            self.core.set_output_directory(odir)

    def get_output_directory(self):
        ret = None
        if self.core:
            ret = self.core.get_output_directory()
        return ret

    def set_output_file_prefix(self, ofprefix):
        if self.core:
            self.core.set_output_file_prefix(ofprefix)

    def get_output_file_prefix(self):
        ret = None
        if self.core:
            ret = self.core.get_output_file_prefix()
        return ret

    def set_capture_timestamp(self, timestamp):
        if self.core:
            self.core.set_capture_timestamp(timestamp)

    def get_capture_timestamp(self):
        ret = None
        if self.core:
            ret = self.core.get_capture_timestamp()
        return ret

    def get_interfaces_of_interest(self):
        ret = None
        if self.core:
            ret = self.core.get_interfaces_of_interest()
        else:
            if self.interfaces:
                ret = self.interfaces
        return ret

    def get_hostnames_of_interest(self):
        ret = None
        if self.core:
            ret = self.core.get_hostnames_of_interest()
        else:
            if hasattr(self, "hostnames"):
                ret = self.hostnames
        return ret

    def add_time_table_file(self, tname):
        if self.core:
            self.core.add_time_table_file(tname)

    def add_interface_of_interest(self, interface):
        if self.core:
            self.core.add_interface_of_interest(interface)
        else:
            if not hasattr(self, "interfaces"):
                self.interfaces = []
            self.interfaces.append(interface)

    def add_hostname_of_interest(self, hostname):
        if self.core:
            self.core.add_hostname_of_interest(hostname)
        else:
            if not hasattr(self, "hostnames"):
                self.hostnames = []
            self.hostnames.append(hostname)

    def add_network_log_file(self, interface, nname):
        if self.core:
            self.core.add_network_log_file(interface, nname)
        else:
            if not hasattr(self, "network_log_files"):
                self.network_log_files = {}
            self.network_log_files[interface] = nname

    def add_network_label_file(self, interface, lname):
        if self.core:
            self.core.add_network_label_file(interface, lname)
        else:
            if not hasattr(self, "network_label_files"):
                self.network_label_files = {}
            self.network_label_files[interface] = lname

    def add_host_log_file(self, hostname, hname):
        if self.core:
            self.core.add_host_log_file(hostname, hname)
        else:
            if not hasattr(self, "host_log_files"):
                self.host_log_files = {}
            self.host_log_files[hostname] = hname

    def add_host_label_file(self, hostname, lname):
        if self.core:
            self.core.add_host_label_file(hostname, lname)
        else:
            if not hasattr(self, "host_label_files"):
                self.host_label_files = {}
            self.host_label_files[hostname] = lname

    def add_labeled_packet_dataset(self, dpname):
        if self.core:
            self.core.add_labeled_packet_dataset(dpname)
        else:
            if not hasattr(self, "labeled_packet_dataset"):
                self.labeled_packet_dataset = []
            self.labeled_packet_dataset.append(dpname)

    def add_labeled_flow_dataset(self, dfname):
        if self.core:
            self.core.add_labeled_flow_dataset(dfname)
        else:
            if not hasattr(self, "labeled_flow_dataset"):
                self.labeled_flow_dataset = []
            self.labeled_flow_dataset.append(dfname)

    def add_labeled_host_dataset(self, dhname):
        if self.core:
            self.core.add_labeled_host_dataset(dhname)
        else:
            if not hasattr(self, "labeled_host_dataset"):
                self.labeled_host_dataset = []
            self.labeled_host_dataset.append(dhname)

    def add_labeled_transition_dataset(self, dtname):
        if self.core:
            self.core.add_labeled_transition_dataset(dtname)
        else:
            if not hasattr(self, "labeled_transition_dataset"):
                self.labeled_transition_dataset = []
            self.labeled_transition_dataset.append(dtname)

    def get_labeled_packet_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_labeled_packet_dataset()
        else:
            if hasattr(self, "labeled_packet_dataset"):
                ret = self.labeled_packet_dataset
        return ret

    def get_labeled_flow_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_labeled_flow_dataset()
        else:
            if hasattr(self, "labeled_flow_dataset"):
                ret = self.labeled_flow_dataset
        return ret

    def get_labeled_host_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_labeled_host_dataset()
        else:
            if hasattr(self, "labeled_host_dataset"):
                ret = self.labeled_host_dataset
        return ret

    def get_labeled_transition_dataset(self):
        ret = None
        if self.core:
            ret = self.core.get_labeled_transition_dataset()
        else:
            if hasattr(self, "labeled_transition_dataset"):
                ret = self.labeled_transition_dataset
        return ret

