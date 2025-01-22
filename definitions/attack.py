import os, sys, logging, argparse
import time
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import check_file_availability
from iutils.etc import load_configuration_file
from iutils.etc import load_yaml_file
from common.util import get_application_class
from modules.scenario_verifier import ScenarioVerifier
from definitions.node import Node

class Attack:
    def __init__(self, attacker, initiator, target, begin, atype, step, duration=0, **params):
        self.attacker = attacker
        self.initiator = initiator
        self.target = target
        self.begin = begin
        self.duration = duration
        self.atype = atype
        self.attack = get_application_class(atype)(atype)
        self.attack_step = step
        self.params = params
        self.start_time = params.get("start", 0)
        self.end_time = self.start_time + self.duration
        self.performed = False
        self.finished = False

    def set_start_time(self, start):
        self.start_time = start + self.begin

    def get_start_time(self):
        return self.start_time

    def set_end_time(self, end):
        if self.duration == 0:
            self.end_time = end
            self.duration = self.end_time - self.start_time

    def get_end_time(self):
        return self.end_time

    def set_duration(self, end):
        if self.duration == 0:
            self.duration = self.end_time - self.start_time

    def get_attacker(self):
        return self.attacker.get_name()

    def get_initiator(self):
        return self.initiator.get_name()

    def get_pnode(self):
        return self.initiator.get_pnode()

    def get_attack_type(self):
        return self.atype

    def get_attack_step(self):
        return self.attack_step

    def get_virtualization_type(self):
        return self.initiator.get_virtualization_type()

    def output(self):
        return "{},{},{},{},{},{}\n".format(self.attacker.get_name(), self.target, self.atype, self.start_time, self.duration, self.attack_step)

    def is_performed(self):
        return self.performed

    def set_performed(self, value=True):
        self.performed = value

    def is_finished(self):
        return self.finished

    def set_finished(self, value=True):
        self.finished = value

    def get_shell_prompts(self):
        return self.initiator.get_shell_prompts()

    def perform_attack(self):
        arch = self.initiator.get_architecture()
        os = self.initiator.get_operating_system()
        attack = self.attack
        params = self.params
        target = self.target
        if "target" not in params:
            params["target"] = target
        logging.debug("attack: {}, arch: {}, os: {}".format(attack, arch, os))
        cmds = attack.run_application(arch, os, **params)
        return cmds

def test(sd, nodes, ofname):
    attacks = sd["attack_scenario"]
    alst = []
    for attack in attacks:
        name = attack.get("attacker", None)
        attacker = None
        if name in nodes:
            attacker = nodes[name]
        target = attack.get("target", "internet")
        begin = attack.get("begin", 0)
        atype = attack.get("type", "none")
        step = attack.get("step", "none")
        duration = attack.get("duration", 0)
        options = attack.copy()
        alst.append(Attack(attacker, target, begin, atype, step, duration, **options))

    start = int(time.time())
    for attack in alst:
        attack.set_start_time(start)

    alst.sort(key = lambda x: x.get_start_time())

    logging.info("Starting time: {}".format(start))
    while True:
        curr = int(time.time())
        out = True
        for attack in alst:
            if not attack.is_performed():
                out = False
                if curr > attack.get_start_time():
                    logging.info("cmds: {}".format(attack.perform_attack()))
                    # cmds must be run as backgrounds
                    attack.set_performed()
        if out:
            break

    end = int(time.time())
    logging.info("Ending time: {}".format(end))

    for attack in alst:
        attack.set_end_time(end)

    with open(ofname, "w") as of:
        for attack in alst:
            of.write(attack.output())

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, required=True)
    parser.add_argument("-s", "--scenario-description", metavar="<scenario description file>", help="Scenario description file", type=str, required=True)
    parser.add_argument("-o", "--output", metavar="<output filename>", help="Output filename", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    if not check_file_availability(args.scenario_description):
        logging.error("The scenario description file ({}) does not exist.".format(args.scenario_description))
        sys.exit(1)
    
    conf = load_configuration_file(args.config, "..")
    c = conf.get("scenario_verifier", None)
    sv = ScenarioVerifier(None, c)
    scenario_description, _ = sv.run(args.scenario_description, None)
    nodes = scenario_description["network_configuration"].get("node", None)

    nlst = {}
    for ntype in nodes:
        for n in nodes[ntype]:
            n_name = n.get("name", None)
            if n_name:
                nlst[n_name] = Node(n, ntype)
    test(scenario_description, nlst, args.output)

if __name__ == "__main__":
    main()
