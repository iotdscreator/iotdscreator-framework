import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
from features.feature import Feature

class MeanKernelMalloc(Feature):
    def __init__(self, name):
        super().__init__(name, "transition")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, window):
        # TODO: Implement the procedure to extract the feature

        values = []
        host_logs = window.get_host_logs()
        for hlog in host_logs:
            values.append(hlog.get_values("kernel_malloc"))
        
        if len(values) == 0:
            val = -1
        else:
            val = sum(values) / len(values)

        window.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
