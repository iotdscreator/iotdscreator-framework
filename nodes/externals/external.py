import os, sys, logging
import errno
import time
import random
import re
from subprocess import Popen, PIPE, run
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/../..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import process_error
from applications.application import Application
from common.qemu import QemuFunctions
from common.docker import DockerFunctions

class External:
    def __init__(self, node):
        self.name = node.get_name()
        self.funcs = self._init_functions(node)
        self.shell = None
        self.shell_prompts = None
        self.node = node
        self.config = node.get_configuration()
        self.specification = node.get_specification()

        self.emulation = False
        if self.node.get_virtualization_type() == "qemu":
            self.emulation = True

    def _init_functions(self, node):
        ret = None
        ftype = node.get_virtualization_type()
        logging.debug("ftype: {} in _init_functions() in device.py".format(ftype))
        if ftype == "qemu":
            ret = QemuFunctions(node)
        elif ftype == "docker":
            ret = DockerFunctions(node)
        return ret

    def get_configuration(self):
        return self.node.get_configuration()

    def configure(self):
        pnode = self.get_pnode()
        if pnode and self.funcs:
            self.funcs.configure()
            self.shell = self.funcs.get_shell()

    def start(self):
        self.run_machine()
        self.initialization()
        self.network_setting()

    def stop(self):
        pnode = self.get_pnode()
        if pnode:
            self.funcs.stop()

    def run_machine(self):
        pnode = self.get_pnode()
        if pnode:
            self.preparation()
            self.funcs.start()
        else:
            logging.error("Unable to start the machine as there is no communication channel between IoTDSCreator and Agent")
            sys.exit(1)

    def preparation(self):
        pass

    def initialization(self):
        pass

    def network_setting(self):
        interfaces = self.node.get_interfaces()
        pnode = self.get_pnode()
        vtype = self.node.get_virtualization_type()

        request = {}
        request["opcode"] = "control"
        request["command"] = "ifconfig | grep \": \" -A1"
        request["name"] = self.name
        request["shell"] = self.shell_prompts
        request["type"] = vtype
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        time.sleep(1)

        output = response["stdout"]
        logging.debug("final output: {}".format(output))
        internals = {}
        if output:
            tmp = output.split("\n")
            lst = []
            for t in tmp:
                t = t.strip()
                lst.append(t)

            ifname = None
            ipaddr = None
            for e in lst:
                if ": flags" in e:
                    ifname = e.split(": ")[0]
                if "inet " in e:
                    ipaddr = e.split("netmask")[0].strip().split(" ")[1]
                if "--" in e:
                    internals[ifname] = ipaddr
                    ifname = None
                    ipaddr = None
            internals[ifname] = ipaddr

            if "lo" in internals:
                del internals["lo"]

            ifnames =  list(internals.keys())
            logging.debug("internals: {}".format(internals))
            logging.debug("ifnames: {}".format(ifnames))

            for idx in range(len(interfaces)):
                intf = interfaces.get(idx, None)
                logging.debug("interface {} (before)> name: {}, external: {}, internal: {}, ipaddr: {}".format(idx, intf.get_name(), intf.get_external_ifname(), intf.get_internal_ifname(), intf.get_ipaddr()))
                intf.set_internal_ifname(ifnames[idx])
                intf.set_ipaddr(internals[ifnames[idx]])
                logging.debug("interface {} (after)> name: {}, external: {}, internal: {}, ipaddr: {}".format(idx, intf.get_name(), intf.get_external_ifname(), intf.get_internal_ifname(), intf.get_ipaddr()))

                ifname = intf.get_internal_ifname()
                ipaddr = intf.get_ipaddr()

                if "169.254." in ipaddr:
                    request["opcode"] = "control"
                    request["command"] = "ifconfig {} 0".format(internals[idx])
                    request["name"] = self.name
                    request["shell"] = self.shell_prompts
                    response = pnode.send_request(request)
                    process_error(request, response)

                    time.sleep(1)

                    request["command"] = "dhclient {}".format(internals[idx])
                    request["timeout"] = 10
                    request["name"] = self.name
                    request["shell"] = self.shell_prompts
                    response = pnode.send_request(request)
                    process_error(request, response)

                    time.sleep(1)

            request["opcode"] = "control"
            request["command"] = "route -n"
            request["name"] = self.name
            request["shell"] = self.shell_prompts
            response = pnode.send_request(request)
            process_error(request, response)

            time.sleep(1)

            logging.debug("route: {}".format(output))

    def get_shell(self):
        return self.shell

    def get_pipe_in(self):
        return self.shell.get_pipe_in()

    def get_pipe_out(self):
        return self.shell.get_pipe_out()

    def get_pnode(self):
        return self.node.get_pnode()

    def get_name(self):
        return self.name

    def get_function_type(self):
        return self.ftype

    def get_is_emulated(self):
        return self.emulation

    def prepare_dtb(self):
        return self.funcs.prepare_dtb()

    def prepare_kernel(self):
        return self.funcs.prepare_kernel()

    def prepare_filesystem(self):
        return self.funcs.prepare_filesystem()

    def prepare_firmware(self):
        return self.funcs.prepare_firmware()
