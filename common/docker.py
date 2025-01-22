import os, sys, logging
import re
import time
import random
import psutil
import subprocess
from ipaddress import IPv4Network
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application
from iutils.etc import process_error
COMMAND_SLEEP_TIME=2

class DockerShell:
    def __init__(self, pnode, pipe_in=None, pipe_out=None):
        self.pnode = pnode
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out

    def get_pipe_in(self):
        return self.pipe_in

    def get_pipe_out(self):
        return self.pipe_out

class DockerInterface:
    def __init__(self, nname, iname, index):
        self.name = iname
        external = "veth{}".format(nname, index)
        internal = "eth{}".format(index)
        self.external = external
        self.internal = internal
        logging.debug("external: {}, internal: {}".format(external, internal))

    def get_interface_name(self):
        return self.name

    def get_external_ifname(self):
        return self.external

    def set_external_ifname(self, name):
        self.external = name

    def get_internal_ifname(self):
        return self.internal

    def set_internal_ifname(self, name):
        self.internal = name

class DockerFunctions:
    def __init__(self, node):
        self.taps = []
        self.mnum = 0
        self.bnum = 0
        self.download_server = None
        self.shell = None
        self.node = node
        logging.debug("self.node: {}".format(self.node))

        self.image = node.get_image()
        self.interfaces = node.get_interfaces()

    def make_pipe(self):
        pass

    def make_interfaces(self):
        pass

    def get_shell(self):
        pass

    def get_pipe_in(self):
        pass

    def get_pipe_out(self):
        pass

    def run_docker(self):
        logging.info(" - Running a Docker container ({})".format(self.node.get_name()))
        conf = self.node.get_configuration()
        pnode = self.node.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility".format(wdir))

        # 1. Check if Docker is installed
        request = {}
        request["opcode"] = "execute"
        request["command"] = "which docker"
        response = pnode.send_request(request)
        process_error(request, response)

        # 2. Install Docker if it is not installed
        if len(response["stdout"]) == 0:
            request["command"] = "apt-get update && apt-get install -y docker-ce"
            request["capture"] = False
            request["background"] = True
            request["timeout"] = 0
            response = pnode.send_request(request)
            process_error(request, response, ignore=True, sleep=COMMAND_SLEEP_TIME)

        # 3. Stop the docker image
        name = self.node.get_name()
        cmd = []
        cmd.append("docker")
        cmd.append("stop")
        cmd.append(name)

        request["opcode"] = "execute"
        request["command"] = ' '.join(cmd)
        request["capture"] = True
        response = pnode.send_request(request)
        process_error(request, response, ignore=True, sleep=COMMAND_SLEEP_TIME)

        # 3. Run the docker image
        image = self.node.get_image()
        ports = []
        apps = self.node.get_applications()
        for app in apps:
            port = app.get_param_value("port")
            if port:
                ports.append(port)
        cmd = []
        cmd.append("docker")
        cmd.append("run")

        for port in ports:
            cmd.append("-p")
            cmd.append("{}:{}".format(port, port))

        cmd.append("--name")
        cmd.append(name)
        cmd.append("--rm")
        cmd.append("-dit")
        cmd.append(image)

        logging.debug("cmd: {}".format(' '.join(cmd)))
        request["opcode"] = "execute"
        request["command"] = ' '.join(cmd)
        request["capture"] = False
        request["background"] = True
        request["timeout"] = 0
        response = pnode.send_request(request)
        process_error(request, response, ignore=True, sleep=COMMAND_SLEEP_TIME)

    def get_name(self):
        return self.name

    def configure(self):
        self.make_pipe()
        self.make_interfaces()

    def start(self):
        logging.debug("Running the docker")
        self.run_docker()
        logging.debug("Waiting for the images for 20 seconds")
        time.sleep(20)
        logging.debug("Setting the network interfaces")
        self.network_setting()
            
    def apply(self, dns=None):
        pass

    def stop(self):
        pnode = self.node.get_pnode()
        cmd = "docker stop {}".format(self.node.get_name())
        request = {}
        request["opcode"] = "execute"
        request["command"] = cmd
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        cmd = "docker rm {}".format(self.node.get_name())
        request["command"] = cmd
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

    def network_setting(self):
        pnode = self.node.get_pnode()
        vtype = self.node.get_virtualization_type()
        interfaces = self.interfaces
        request = {}
        request["type"] = self.node.get_virtualization_type()
        request["name"] = self.node.get_name()

        for idx in interfaces:
            intf = interfaces[idx]
            internal = intf.get_internal_ifname()
            cmd = "cat /sys/class/net/{}/iflink".format(internal)
            request["opcode"] = "control"
            request["type"] = vtype
            request["command"] = cmd
            response = pnode.send_request(request, listen=False)
            num = int(response["stdout"])

            cmd = "ip ad | grep {} | grep ': '".format(num)
            request["opcode"] = "execute"
            request["command"] = cmd
            response = pnode.send_request(request)
            output = response["stdout"]
            tmp = output.strip().split("\n")
            for e in tmp:
                e = e.strip().split(": ")
                n = int(e[0])

                if n == num:
                    ext = e[1]
                    break

            if not ext:
                logging.error("Something is wrong in Docker")
            external = ext.split("@")[0]

            intf.set_external_ifname(external)

        request["opcode"] = "control"
        request["command"] = "apt-get update"
        request["capture"] = False
        response = pnode.send_request(request, listen=False)
        process_error(request, response)

        retry = True
        while retry:
            request["command"] = "apt-get install -y net-tools"
            request["capture"] = True
            response = pnode.send_request(request, listen=False)
            process_error(request, response)

            if "are you root" in response["stdout"] or "are you root" in response["stderr"]:
                logging.info("  => Acquiring a lock is impossible. Having a cooling time")
                time.sleep(10)
            else:
                break

        request["command"] = "apt-get install -y iputils-ping"
        request["capture"] = False
        response = pnode.send_request(request, listen=False)
        process_error(request, response)

        request["command"] = "apt-get install -y wget"
        request["capture"] = False
        response = pnode.send_request(request, listen=False)
        process_error(request, response)

        request["command"] = "apt-get install -y git"
        request["capture"] = False
        response = pnode.send_request(request, listen=False)
        process_error(request, response)
