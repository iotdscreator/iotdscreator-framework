import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from features.feature import Feature

class CpuRunningTimeOnSystemMode(Feature):
    def __init__(self, name):
        super().__init__(name, "host")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, hlog):
        # TODO: Implement the procedure to extract the feature

        val = hlog.get_values("cpu_running_time_on_system_mode")

        hlog.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
