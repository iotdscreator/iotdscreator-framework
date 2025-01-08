import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class Ping(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        super().__init__(app, name)

    # Please revise the following functions if it is different
    # from the default way
    def check_application(self, arch=None, os=None):
        logging.debug("Check the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "which nmap"
        #     cmds.append(cmd)

        if os in ["debian", "ubuntu"]:
            cmd = "which ping"
            cmds.append(cmd)

        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "apt-get install nmap"
        #     cmds.append(cmd)

        if os in ["debian", "ubuntu"]:
            cmd = "apt-get install -y iputils-ping"
            cmds.append(cmd)

        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("self: {}, arch: {}, os: {}, params: {}".format(self, arch, os, params))
        logging.debug("Run the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)

        count = params.get("count", None)
        target = params.get("target", "www.google.com")

        clst = ["ping"]
        if count:
            clst.append("-c")
            clst.append(str(count))
        clst.append(target)
        cmd = ' '.join(clst)
        cmds.append(cmd)
        
        return cmds

