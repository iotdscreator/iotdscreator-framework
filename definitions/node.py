import os, sys, logging
import pathlib
import platform
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from common.util import get_device_class
from common.util import get_router_class
from common.util import get_interface_class
from common.util import get_application_class
from nodes.externals.external import External
from iutils.etc import process_error

class Node:
    def __init__(self, node, ntype):
        self.name = node["name"]
        self.vtype = node["type"]
        self.ntype = ntype
        self.interfaces = {}
        self.idx_to_name = {}
        self.name_to_idx = {}
        self.applications = []
        self.pnode = None
        self.config = None
        self.shell_prompts = None
        self.host_logging = True

        self.specification = {}
        self.specification["architecture"] = node.get("architecture", None)
        self.specification["cpu"] = node.get("cpu", None)
        self.specification["memory"] = node.get("memory", "1G")
        self.specification["smp"] = node.get("smp", 1)
        self.specification["machine"] = node.get("machine", None)
        self.specification["hardware security"] = node.get("hardware security", False)
        self.specification["firmware"] = node.get("firmware", None)
        self.specification["dtb"] = node.get("dtb", None)
        self.specification["kernel"] = node.get("kernel", None)
        self.specification["operating system"] = node.get("operating system", None)
        self.specification["filesystem"] = node.get("filesystem", None)
        self.specification["interface"] = node.get("interface", None)
        self.specification["append"] = node.get("append", None)
        logging.debug("self.specification: {}".format(self.specification))

        self.image = node.get("image", None)
        if self.image:
            if "ubuntu" in self.image:
                self.specification["operating system"] = "ubuntu"
            elif "debian" in self.image:
                self.specification["operating system"] = "debian"

        if self.vtype == "docker":
            self.specification["architecture"] = platform.processor()
        logging.debug("image: {}".format(self.image))

        interfaces = node.get("interface", [])
        logging.debug("interfaces: {}".format(interfaces))
        idx = 0
        for interface in interfaces:
            intf = self._init_interface(interface["name"], interface["type"], idx)
            logging.debug("name: {}, type: {}, idx: {}".format(interface["name"], interface["type"], idx))
            if intf:
                self.interfaces[idx] = intf
                self.idx_to_name[intf.get_index()] = intf.get_name()
                self.name_to_idx[intf.get_name()] = intf.get_index()
                idx += 1

        applications = node.get("application", [])
        logging.debug("applications: {}".format(applications))
        for application in applications:
            atype = application["type"]
            name = application.get("name", atype)
            application["name"] = name
            del application["type"]
            del application["name"]
            logging.debug("atype: {}, name: {}".format(atype, name))
            app = self._init_application(atype, name, **application)
            if app:
                self.applications.append(app)
        logging.debug("self.applications: {}".format(self.applications))

        model = node.get("model", None)
        self.model = None
        if model:
            self.model = self._init_model(model)

    def _init_model(self, model):
        ret = None
        if model == "external":
            cls = External
        else:
            cls = get_device_class(model)
            if not cls:
                cls = get_router_class(model)
        if cls:
            ret = cls(self)
        return ret

    def _init_interface(self, name, itype, idx):
        ret = None
        itype = "{}_intf".format(itype)
        cls = get_interface_class(itype)
        logging.debug("cls: {}".format(cls))
        if cls:
            ret = cls(self, name, idx)
        return ret

    def _init_application(self, atype, name, **params):
        ret = None
        cls = get_application_class(atype)
        if cls:
            ret = cls(atype, name=name, **params)
        return ret

    def init(self):
        pass

    def set_pnode(self, pnode):
        self.pnode = pnode

    def get_pnode(self):
        return self.pnode

    def configure(self):
        if self.model:
            self.model.configure()

    def start(self):
        self.model.start()

    def stop(self):
        self.model.stop()

    def get_name(self):
        return self.name

    def get_virtualization_type(self):
        return self.vtype

    def get_node_type(self):
        return self.ntype

    def get_model(self):
        return self.model

    def get_specification(self):
        return self.specification

    def get_firmware_info(self):
        return self.specification.get("firmware", None)

    def get_interfaces(self):
        return self.interfaces

    def get_interface(self, name):
        ret = None
        interfaces = self.interfaces
        for idx in interfaces:
            if name == interfaces[idx].get_name():
                ret = interfaces[idx]
                break
        return ret

    def get_num_of_interfaces(self):
        return len(self.interfaces)

    def get_applications(self):
        return self.applications

    def set_configuration(self, conf):
        self.config = conf

    def get_configuration(self):
        return self.config

    def get_architecture(self):
        return self.specification.get("architecture", None)

    def get_operating_system(self):
        return self.specification.get("operating system", None)

    def set_shell_prompts(self, shell_prompts):
        self.shell_prompts = shell_prompts

    def get_shell_prompts(self):
        return self.shell_prompts

    def is_host_logging_enabled(self):
        return self.host_logging

    def set_host_logging(self, enabled):
        self.host_logging = enabled

    def set_names(self, names):
        self.names = names

    def get_names(self):
        return self.names

    def get_image(self):
        return self.image

    def get_host_info_reporter(self):
        appname = "host_info_reporter"
        app = get_application_class(appname)(appname)
        arch = self.get_architecture()
        os = self.get_operating_system()
        cmds = app.check_application(arch, os)
        pnode = self.get_pnode()
        names = self.names
        vtype = self.get_virtualization_type()

        request = {}
        request["name"] = self.get_name()
        request["shell"] = self.get_shell_prompts()
        needs_installation = False
        for cmd in cmds:
            if "must" in cmd:
                needs_installation = True
                break
            request["opcode"] = "control"
            request["type"] = vtype
            logging.debug("cmd: {}".format(cmd))
            request["command"] = cmd
            response = pnode.send_request(request)
            process_error(request, response)
            output = response["stdout"].strip()
            try:
                idx = output.find(cmd)
                if idx > 0:
                    output = output[idx+len(cmd):].strip()
                logging.debug("output: {}".format(output))

                if (app.get_application_type() not in output) or ("no such" in output.lower()):
                    needs_installation = True
                    break
            except:
                continue

        if needs_installation:
            cmds = app.prepare_application(arch, os)
            request = {}
            request["name"] = self.get_name()
            request["shell"] = self.get_shell_prompts()

            for cmd in cmds:
                logging.debug("cmd: {}".format(cmd))
                request["opcode"] = "control"
                request["type"] = vtype
                if vtype == "docker":
                    request["capture"] = False
                if "cache-address" in cmd:
                    ipaddr = self.names.get("cache-address", self.names.get("default", None))
                    cmd = cmd.replace("cache-address", ipaddr)
                if "cache-port" in cmd:
                    port = self.names.get("cache-port", 10201)
                    cmd = cmd.replace("cache-port", str(port))
                request["command"] = cmd
                response = pnode.send_request(request)
                process_error(request, response)

    def run_host_info_reporter(self, **params):
        appname = "host_info_reporter"
        app = get_application_class(appname)(appname)
        arch = self.get_architecture()
        os = self.get_operating_system()
        names = self.names
        params["arch"] = arch
        params["os"] = os
        cmds = app.run_application(**params)
        pnode = self.get_pnode()
        names = self.names
        vtype = self.get_virtualization_type()

        request = {}
        request["name"] = self.get_name()
        request["shell"] = self.get_shell_prompts()
        for cmd in cmds:
            logging.debug("cmd: {}".format(cmd))
            request["opcode"] = "control"
            request["type"] = vtype
            request["command"] = cmd
            request["background"] = True
            response = pnode.send_request(request)
            process_error(request, response)

