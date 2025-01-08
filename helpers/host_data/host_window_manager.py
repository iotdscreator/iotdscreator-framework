import os, sys, argparse, logging
import time
import threading
import copy
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from definitions.host_window import HostWindow

class HostWindowManager:
    def __init__(self, conf):
        self.window_length = conf.get("window_length", 10000) / 1000
        self.sliding_window = conf.get("sliding_window", True)
        if self.sliding_window:
            self.sliding_window_interval = conf.get("sliding_window_interval", 100000) / 1000
        else:
            self.sliding_window_interval = -1
        self.windows = []
        self.first_timestamp = 0
        self.last_timestamp = 0

    def set_last_timestamp(self, ts):
        self.last_timestamp = ts

    def get_windows(self):
        return self.windows
    
    def run(self, host_logs):
        if self.sliding_window:
            logging.info("Run Host Window Manager with Sliding Window")
        else:
            logging.info("Run Host Window Manager without Sliding Window")

        self.host_logs = host_logs
        logging.debug("host_logs: {}".format(host_logs))
        self.first_timestamp = host_logs[0].get_timestamp()
        self.last_timestamp = host_logs[-1].get_timestamp()

        window_start = self.first_timestamp
        while window_start < self.last_timestamp:
            self.process_window(window_start)
            if self.sliding_window:
                window_start += self.sliding_window_interval
            else:
                window_start += self.window_length

        logging.debug("# of windows: {}".format(len(self.windows)))

    def process_window(self, window_start):
        hlog = self.host_logs[0]
        hostname = hlog.get_hostname()
        window_length = self.window_length
        window = HostWindow(hostname, window_length)
        window_end = window_start + window_length
        for hlog in self.host_logs:
            timestamp = hlog.get_timestamp()
            if timestamp >= window_start and timestamp < window_end:
                window.add_host_log(hlog)
        window.set_times(window_start, window_end)
        self.windows.append(window)
