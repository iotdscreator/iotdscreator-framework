import os, sys, argparse, logging
import time
import json
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from definitions.host_log import HostLog
from helpers.host_data.host_info_processor import HostInfoProcessor

class HostLogReader:
    def __init__(self, conf):
        self.host_logs = []
        self.config = conf
        self.hip = HostInfoProcessor(None)

    def run(self, hname, lname):
        host_logs = self.read_host_logs(hname)
        flags, steps, names = parse_label(lname)

        logging.debug("# of host logs: {}".format(len(host_logs)))
        logging.debug("# of labels: {}".format(len(flags)))
        logging.debug("flags: {}, steps: {}, names: {}".format(flags, steps, names))

        logging.debug("host_logs: {}".format(len(host_logs)))
        num = 0
        for host_log in host_logs:

            hlog = self.parse_host_log(host_log)
            num += 1
            
            if hlog:
                try:
                    hlog.set_attack_flag(flags[num])
                    hlog.set_attack_step(steps[num])
                    hlog.set_attack_name(names[num])
                except:
                    hlog.set_attack_flag(0)
                    hlog.set_attack_step("benign")
                    hlog.set_attack_name("benign")

                self.host_logs.append(hlog)

    def get_host_logs(self):
        return self.host_logs

    def read_host_logs(self, hname):
        ret = []
        with open(hname, "r") as f:
            for line in f:
                js = json.loads(line.strip())
                ret.append(js)
        return ret

    def parse_host_log(self, host_log):
        hostname = host_log["name"]
        atype = host_log["type"]
        timestamp = int(host_log["timestamp"])
        data = host_log["data"]
        hlog = HostLog(hostname, timestamp)

        if atype == "atop":
            lines = data.splitlines()
            first_line = True
            processes = False
            for line in lines:
                line = line.strip()
                if len(line) == 0:
                    continue
                
                if first_line and line.startswith("ATOP -"):
                    first_line = False
                    continue

                if not processes:
                    if "PID SYSCPU" in line:
                        processes = True
                    elif len(line) > 0 and line[0].isupper():
                        components = line.split("|")
                        main_category = components[0].strip().split()[0].lower()
                        metrics = {}

                        for component in components[1:]:
                            component = component.strip()
                            if component:
                                key_value = component.split(maxsplit=1)
                                if len(key_value) == 2:
                                    key, value = key_value
                                    value = value.strip().rstrip("%").replace("w", "").strip()
                                    hlog.add_key_value(main_category, key, value)
                else:
                    pinfo = line.strip().split(" ")
                    lst = []
                    for e in pinfo:
                        e = e.strip()
                        if len(e) == 0:
                            continue
                        lst.append(e)
                    hlog.add_process(lst)
        return hlog

def parse_label(lname):
    logging.debug("lname: {}".format(lname))
    flag = {}
    udl = {}
    name = {}
    with open(lname, "r") as f:
        for line in f:
            try:
                tmp = line.strip().split(",")
                idx = int(tmp[1])
                flag[idx] = int(tmp[-1])
                udl[idx] = tmp[-2]
                name[idx] = tmp[-3]
            except:
                continue
    return flag, udl, name

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Configuration file", type=str, default="../config.yaml")
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")

    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_configuration_file(args.config, "..")
    c = conf.get("feature_extractor", None)
    if c:
        c = c.get("host_log_reader", None)
    host_log_reader = HostLogReader(c)

if __name__ == "__main__":
    main()
