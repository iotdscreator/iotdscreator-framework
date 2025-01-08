import argparse, os, sys, logging
import socket
import time, datetime
import threading
import asyncio
import pathlib
import re
import pandas as pd
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)

class HostInfoProcessor:
    def __init__(self, core):
        logging.debug("Initialize Host Info Parser")
        self.core = core

    def process_message(self, js):
        dtype = js.get("type", None)
        name = js.get("name", None)
        data = js.get("data", None)
        timestamp = js.get("timestamp", None)

        logging.debug("name: {}, timestamp: {}".format(name, timestamp))

        if dtype == "atop" and data:
            parsed_data = self.parse_atop_data(data)

    def parse_atop_data(self, data):
        host_log = {}
        host_log["processes"] = set([])
        lines = data.splitlines()
        change_list = {}
        first_line = True

        processes = False
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue

            if first_line and line.startswith('ATOP -'):
                parts = line.split()
                if len(parts) >= 5:
                    dt = "{} {}".format(parts[3], parts[4])
                    host_log["timestamp"] = time.mktime(datetime.datetime.strptime(dt, "%Y/%m/%d %H:%M:%S").timetuple())
                    logging.debug("timestamp: {}".format(host_log["timestamp"]))
                first_line = False
                continue

            if not processes:
                if "PID SYSCPU" in line:
                    processes = True
                elif len(line) > 0 and line[0].isupper():
                    components = line.split('|')
                    main_category = components[0].strip().split()[0]
                    metrics = {}
                    changes = {}

                    for component in components[1:]:
                        clean_component = component.strip()
                        if clean_component:
                            key_value = clean_component.split(maxsplit=1)
                            if len(key_value) == 2:
                                key, value = key_value
                                value = value.strip().rstrip('%').replace('w', '').strip()
                                metrics[key] = value
                                host_log[main_category] = metrics
            else:
                tmp = line.strip().split(" ")
                process = "{}".format(tmp[-1])
                host_log["processes"].add(process)

        return host_log

def is_float(num):
    ret = True
    try:
        num = float(num)
    except:
        ret = False
    return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    HostInfoProcessor(None)

if __name__ == "__main__":
    main()

