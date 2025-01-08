import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
import numpy as np

class Transition:
    def __init__(self, hostname, start_time, window_length):
        self.hostname = hostname
        self.host_logs = []
        self.window_length = window_length
        
        self.stat = {} # map: feature -> value
        self.code = []

        self.attack_flag = 0
        self.attack_flag_labeled = 0

        self.attack_step = []
        self.attack_step_labeled = []

        self.attack_name = []
        self.attack_name_labeled = []

        self.window_start_time = start_time
        self.window_end_time = start_time + window_length

    def get_hostname(self):
        return self.hostname

    def add_host_log(self, host_log):
        self.host_logs.append(host_log)
        if host_log.get_attack_flag() == 1:
            self.attack_flag = 1
            
            if host_log.get_attack_step() not in self.attack_step:
                self.attack_step.append(host_log.get_attack_step())

            if host_log.get_attack_name() not in self.attack_name:
                name = "{} ({})".format(host_log.get_attack_name(), host_log.get_attack_step())
                self.attack_name.append(name)

            logging.debug("Window is set to an attack window".format(self.attack_flag))

    def get_host_logs(self):
        return self.host_logs

    def set_host_logs(self, host_logs):
        self.host_logs = host_logs
        for hlog in host_logs:
            if hlog.get_attack_flag() == 1:
                self.attack_flag = 1
                step = hlog.get_attack_step()
                if step not in self.attack_step:
                    self.attack_step.append(step)
                name = "{} ({})".format(hlog.get_attack_name(), hlog.get_attack_step())
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

    def get_num_of_host_logs(self):
        return len(self.host_logs)
