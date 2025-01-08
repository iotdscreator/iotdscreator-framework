import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class Flooding(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        super().__init__(app, name)
        self.atype = params.get("attack_type", "syn_flooding")
        self.duration = params.get("duration", 10)
        self.target = params.get("target", None)
        self.port = params.get("port", 22)

    # Please revise the following functions if it is different
    # from the default way
    def check_application(self, arch=None, os=None):
        logging.debug("Check the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "which nmap"
        #     cmds.append(cmd)

        if os in ["debian", "ubuntu"]:
            cmd = "cd ~"
            cmds.append(cmd)
            cmd = "./flooding"
            cmds.append(cmd)

        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "apt-get install nmap"
        #     cmds.append(cmd)

        if os in ["debian", "ubuntu"]:
            aname = None
            if arch == "aarch64":
                aname = "flooding-aarch64"
            elif arch == "x86_64":
                aname = "flooding-x86_64"

            if aname:
                cmd = "wget http://cache-address:cache-port/flooding/{} -O flooding".format(aname)
                cmds.append(cmd)
                cmd = "chmod 777 flooding"
                cmds.append(cmd)

        logging.debug("commands for {} ({}/{}): {}".format(self.app, arch, os, cmds))
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)
        
        atype = params.get("attack_type", self.atype)
        duration = params.get("duration", self.duration)
        target = params.get("target", self.target)
        port = params.get("port", self.port)

        if os in ["debian", "ubuntu"]:
            if arch in ["aarch64", "x86_64"]:
                if target and port:
                    cmd = "./flooding -a {} -d {} -i {} -p {}".format(atype, duration, target, port)
                    cmds.append(cmd)
        return cmds

