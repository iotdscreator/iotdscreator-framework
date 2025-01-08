import os, sys, logging
import errno
import time
import random
import subprocess
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application
from common.qemu import QemuFunctions
from iutils.etc import process_error

class Router:
    def __init__(self, node):
        self.node = node
        self.name = node.get_name()
        self.funcs = self._init_functions(node)

        self.shell_prompts = None
        self.emulation = False
        self.config = node.get_configuration()
        self.specification = node.get_specification()

        self.rules = []
        self.rnum = 0

    def _init_functions(self, node):
        ret = None
        ftype = node.get_virtualization_type()
        if ftype == "qemu":
            ret = QemuFunctions(node)
            self.emulation = True
        logging.debug("fytpe: {}, ret: {}".format(ftype, ret))
        return ret

    def get_configuration(self):
        return self.node.get_configuration()

    def configure(self):
        pnode = self.get_pnode()
        if pnode and self.funcs:
            self.funcs.configure()

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
        pnode = self.get_pnode()
        prompts = self.get_shell_prompts()
        if not pnode:
            logging.error("The related physical node must be specified")
            logging.error("Please try again")
            sys.exit(1)

        #1. Turn up the interfaces 
        request = {}
        interfaces = self.node.get_interfaces()
        vtype = self.node.get_virtualization_type()
        logging.debug("interfaces: {}".format(interfaces))
        for idx in interfaces:
            request["opcode"] = "control"
            request["type"] = vtype
            request["name"] = self.get_name()
            request["command"] = "ip link set {} up".format(interfaces[idx].get_internal_ifname())
            request["shell"] = prompts
            response = pnode.send_request(request)
            process_error(request, response)
            logging.debug("response: {}".format(response["stdout"]))

            request["opcode"] = "control"
            request["name"] = self.get_name()
            request["command"] = "timeout 10 dhclient {}".format(interfaces[idx].get_internal_ifname())
            request["shell"] = prompts
            response = pnode.send_request(request)
            process_error(request, response)
            logging.debug("response: {}".format(response["stdout"]))

            request["opcode"] = "control"
            request["name"] = self.get_name()
            request["command"] = "ifconfig -a"
            request["shell"] = prompts
            response = pnode.send_request(request)
            process_error(request, response)
            logging.debug("response: {}".format(response["stdout"]))

            # TODO: need to get the interface names

        #2. Run dnsmasq for each interface if it is set
        dnsmasq_installed = False
        request = {}
        request["opcode"] = "control"
        request["name"] = self.get_name()
        pnode = self.get_pnode()
        if not pnode:
            logging.error("The related physical node must be specified")
            logging.error("Please try again")
            sys.exit(1)

        # TODO: Need to implement the dnsmasq related things
        """
        for intf in self.interfaces:
            if intf.dnsmasq:
                if not dnsmasq_installed:
                    request["command"] = "killall apt apt-get"
                    response = pnode.send_request(request)
                    process_error(request, response)

                    request["command"] = "apt-get update --allow-releaseinfo-change"
                    request["capture"] = False
                    response = pnode.send_request(request)
                    process_error(request, response)

                    request["command"] = "apt-get install -y dnsmasq"
                    request["capture"] = False
                    response = pnode.send_request(request)
                    process_error(request, response)

                intf.run_dnsmasq()
        """

    def get_pnode(self):
        return self.node.get_pnode()

    def get_name(self):
        return self.name

    def get_function_type(self):
        return self.ftype

    def get_is_emulated(self):
        return self.emulation

    def get_shell_prompts(self):
        return self.shell_prompts

    def prepare_dtb(self):
        return self.funcs.prepare_dtb()

    def prepare_kernel(self):
        return self.funcs.prepare_kernel()

    def prepare_filesystem(self):
        return self.funcs.prepare_filesystem()

    def prepare_firmware(self):
        return self.funcs.prepare_firmware()
