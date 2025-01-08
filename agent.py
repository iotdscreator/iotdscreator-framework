import os, sys, argparse, logging
import pwd
import socket
import threading
import json
import base64
import subprocess
import select
from iutils.etc import check_file_availability
from iutils.etc import load_yaml_file

class Agent:
    def __init__(self, conf):
        self.config = conf
        self.socket = None
        self.master = None
        self.network_log_files = {}

        self.working_directory = os.getcwd()
        if "working_directory" in conf:
            wdir = conf["working_directory"]
            if "~" in wdir:
                try:
                    user = os.getlogin()
                except:
                    user = os.environ['SUDO_USER'] if 'SUDO_USER' in os.environ else os.environ['USER']
                home = os.path.expanduser('~{}'.format(user))
                wdir = wdir.replace("~", home)
                logging.debug("user: {}, home: {}, wdir: {}".format(user, home, wdir))

            if not os.path.exists(wdir):
                os.mkdir(wdir)
            self.working_directory = wdir

        logging.debug("working directory: {}".format(wdir))
        self.run()

    def run(self):
        conf = self.config
        addr = conf.get("ipaddr", "0.0.0.0")
        port = conf.get("port", 5555)

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            logging.error("The socket error")
            sys.exit(1)

        try:
            self.socket.bind((addr, port))
        except:
            logging.error("The bind() error ({}:{})".format(addr, port))
            sys.exit(1)

        logging.info("[*] The agent is ready to receive the commands from IoTDSCreator")

        while True:
            request, info = self.socket.recvfrom(1024)
            request = json.loads(request)
            logging.debug("[*] the agent accepts the connection from {}:{}".format(info[0], info[1]))
            logging.debug("[*] the agent receives the command: {}".format(request["opcode"]))
            if "command" in request:
                logging.debug("[*] command: {}".format(request["command"]))
            response = {}

            if request["opcode"] == "execute":
                response = self._execute_command(request)
            elif request["opcode"] == "capture":
                response = self._capture_packets(request)
            elif request["opcode"] == "upload":
                response = self._upload_network_log_file(request)
            elif request["opcode"] == "control":
                response = self._control_node(request)
            elif request["opcode"] == "listen":
                response = self._listen_to_node(request)
            elif request["opcode"] == "report":
                response = self._report_resource_information(request)
                response["wdir"] = self.working_directory
            elif request["opcode"] == "hello":
                response = self._test_connectivity(request)
            response["opcode"] = request["opcode"]

            if response["opcode"] != "upload":
                logging.debug("response: {}".format(response))
            self.socket.sendto(json.dumps(response).encode(), info)

    def get_master_socket(self):
        return self.master

    def _execute_command(self, request):
        ret = {}
        conf = self.config
        timeout = conf.get("timeout", 10)
        if "timeout" in request:
            timeout = request["timeout"]

        logging.debug("command: {}".format(request["command"]))
        tmp = request["command"].strip().split("|")
        output = {}
        idx = 0
        
        pre = []
        if timeout > 0:
            pre = ["timeout", "--preserve-status", "--signal", "SIGINT", "{}".format(timeout * 60)]

        capture = request.get("capture", True)

        while tmp != []:
            cmd = tmp.pop(0)
            cmd = cmd.strip().split(" ")

            if "background" in request and request["background"]:
                cmd.append("&")

            if idx == 0:
                cmd = ' '.join(pre + cmd)
                if capture:
                    output[idx] = subprocess.run(cmd, shell=True, capture_output=True)
                else:
                    output[idx] = subprocess.run(cmd, shell=True)
            else:
                cmd = ' '.join(cmd)
                if capture:
                    output[idx] = subprocess.run(cmd, input=output[idx-1].stdout, shell=True, capture_output=True)
                else:
                    output[idx] = subprocess.run(cmd, input=output[idx-1].stdout, shell=True)
            logging.info("command: {}".format(cmd))
            idx += 1

        for i in range(idx):
            logging.debug("output[{}]: {}".format(i, output[i]))

        result = output[idx-1]
        logging.debug("result: {}".format(result))

        ret["command"] = request["command"]
        ret["returncode"] = result.returncode
        if capture:
            ret["stdout"] = result.stdout.decode()
            ret["stderr"] = result.stderr.decode()
        return ret

    def _capture_packets(self, request):
        ret = {}
        conf = self.config
        cmd = request["command"].split(" ")
        odir = "{}/network_log_files".format(self.working_directory)

        if not os.path.exists(odir):
            os.mkdir(odir)

        ofname = "{}/{}".format(odir, request.get("filename", "tmp.pcap"))
        cmd.append("-w")
        cmd.append(ofname)
        logging.info("network log file name: {}".format(ofname))
        process = subprocess.Popen(cmd, close_fds=True)
        ret["pid"] = process.pid
        ret["returncode"] = process.returncode
        return ret

    def _upload_network_log_file(self, request):
        ret = {}
        conf = self.config
        ofname = "{}/network_log_files/{}".format(self.working_directory, request.get("filename", "tmp.pcap"))
        sequence = request.get("sequence", -1)

        if not ofname:
            ret["resultcode"] = 1
        else:
            try:
                if sequence == -1:
                    with open(ofname, "rb") as of:
                        content = of.read()
                    content = base64.b64encode(content).decode()
                    self.network_log_files[ofname] = {}
                    
                    total = int(len(content) / 1000) + 1

                    self.network_log_files[ofname]["total"] = total
                    self.network_log_files[ofname]["content"] = {}
                    
                    for i in range(total):
                        self.network_log_files[ofname]["content"][i] = content[i*1000:(i+1)*1000]
                elif sequence >= 0:
                    ret["sequence"] = sequence
                    ret["content"] = self.network_log_files[ofname]["content"][sequence]
                ret["total"] = self.network_log_files[ofname]["total"]
                ret["resultcode"] = 0
            except:
                ret["resultcode"] = 1
        
        return ret

    def _control_node(self, request):
        ret = {}
        nname = request.get("name", None)
        vtype = request.get("type", None)

        if not nname:
            logging.error("No name is provided in the request")
            logging.error("Please try again after checking if the command is sent with the name of the node")
            ret["returncode"] = 1
        else:
            logging.debug("Node to be controlled: {}".format(nname))
            if vtype == "qemu":
                pname = "/tmp/{}-pipe.in".format(nname)
                if not os.path.exists(pname):
                    logging.error("No pipe exists")
                    logging.error("Please try again after checking if the pipe exists")
                    ret["returncode"] = 1
                else:
                    pin = os.open(pname, os.O_WRONLY)
                    if "background" in request and request["background"]:
                        cmd = "{} &\n".format(request["command"])
                    else:
                        cmd = "{}\n".format(request["command"])
                    logging.info("command to {}: {}".format(request["name"], cmd))
                    os.write(pin, cmd.encode())
                    os.close(pin)
                    ret["returncode"] = 0
            elif vtype == "docker":
                cmds = []
                cmds.append("docker")
                cmds.append("exec")
                cmds.append("-it")
                if "background" in request and request["background"]:
                    cmds.append("-d")
                cmds.append(nname)
                cmds.append(request["command"])
                capture = request.get("capture", True)
                cmd = ' '.join(cmds)
                output = subprocess.run(cmd, shell=True, capture_output=capture)
                if capture:
                    ret["stdout"] = output.stdout.decode()
                    ret["stderr"] = output.stderr.decode()
                ret["returncode"] = 0
            else:
                logging.error("unsupported virtualization type")
                ret["returncode"] = 1

        ret["command"] = request["command"]
        return ret

    def _listen_to_node(self, request):
        ret = {}
        nname = request.get("name", None)
        if not nname:
            logging.error("No name is provided in the request")
            logging.error("Please try again after checking if the command is sent with the name of the node")

        pname = "/tmp/{}-pipe.out".format(nname)
        if not os.path.exists(pname):
            logging.error("The pipe ({}) does not exist".format(pname))
            logging.error("Please try again after checking if the pipe exists")
            ret["returncode"] = 1
        else:
            output = b''
            pout = os.open(pname, os.O_RDONLY)
            amount = request.get("amount", 1)

            while True:
                output += os.read(pout, amount)
                try:
                    output = output.decode()
                    break
                except:
                    continue

            os.close(pout)
            ret["returncode"] = 0
            ret["stdout"] = output
        return ret

    def _report_resource_information(self, request):
        ret = {}
        ret["resource"] = {}
        ret["resource"]["cpu"] = self.__get_num_of_cpus()
        ret["resource"]["memory"] = self.__get_available_memory()
        return ret

    def __get_num_of_cpus(self):
        output = subprocess.check_output(["lscpu"]).decode().split("\n")
        lscpu = {}
        for e in output:
            e = e.strip()
            if len(e) == 0:
                continue
            tmp = e.strip().split(":")
            key = tmp[0].strip()
            value = ":".join(tmp[1:]).strip()
            lscpu[key] = value
        ncpu = int(lscpu.get("CPU(s)", -1))
        logging.debug("num of CPU(s): {}".format(ncpu))
        return ncpu

    def __get_available_memory(self):
        output = subprocess.check_output(["free", "-h"]).decode()
        mem = output.split("\n")[1].split(":")[1].split("  ")[-1].strip()

        num = 0
        exist = False
        for idx in range(len(mem)):
            m = mem[idx].lower()
            if m in ["k", "m", "g", "t"]:
                num = int(float(mem[:idx]))

                if m == "k":
                    mem = num * 2 ** 10
                elif m == "m":
                    mem = num * 2 ** 20
                elif m == "g":
                    mem = num * 2 ** 30
                elif m == "t":
                    mem = num * 2 ** 40
                else:
                    logging.error("Spurious value: {}".format(mem))
                    mem = -1
                exist = True
                break

        if not exist:
            mem = int(mem)
        logging.debug("available memory: {}".format(mem))
        return mem

    def _test_connectivity(self, request):
        ret = {}
        ret["response"] = "hello"
        return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", metavar="<configuration file>", help="Configuration file", type=str, default="agent.yaml")
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if os.geteuid() != 0:
        logging.error("Please run the agent with sudo")
        sys.exit(1)

    if not check_file_availability(args.config):
        logging.error("The configuration file ({}) does not exist.".format(args.config))
        sys.exit(1)

    conf = load_yaml_file(args.config)

    logging.debug("configuration: {}".format(conf))
    Agent(conf)

if __name__ == "__main__":
    main()
