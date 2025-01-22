import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class ModbusServer(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        if "name" in params:
            del params["name"]
        super().__init__(app, name, **params)

    # Please revise the following functions if it is different
    # from the default way
    def check_application(self, arch=None, os=None):
        logging.debug("Check the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "which nmap"
        #     cmds.append(cmd)
        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "apt-get install nmap"
        #     cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)
        return cmds

