import os, sys, logging, argparse
import time
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import convert_to_seconds
from iutils.etc import convert_to_megabytes
from iutils.etc import convert_to_float

class Process:
    def __init__(self, pname, timestamp, pinfo):
        self.name = pname
        self.timestamp = timestamp

        self.stat = {}

        self.add_feature_value("cpu_running_time_on_system_mode", convert_to_seconds(pinfo[1]))
        self.add_feature_value("cpu_running_time_on_user_mode", convert_to_seconds(pinfo[2]))
        self.add_feature_value("virtual_memory_grow", convert_to_megabytes(pinfo[3]))
        self.add_feature_value("physical_memory_grow", convert_to_megabytes(pinfo[4]))
        if len(pinfo) > 11:
            value = pinfo[10]
            if len(value) > 0 and value[-1] == "%":
                value = value[:-1]
            value = int(value)
            self.add_feature_value("cpu_utilization_percentage", value)

    def add_feature_value(self, feature, val):
        self.stat[feature] = val

    def get_feature_value(self, feature):
        return self.stat.get(feature, None)

    def get_feature_names(self):
        return list(self.stat)

    def get_name(self):
        return self.name

    def get_timestamp(self):
        return self.timestamp
