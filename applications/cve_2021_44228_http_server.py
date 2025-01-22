import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class Cve202144228HttpServer(Application):
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
        cmds.append("must")
        # if arch == "aarch64" and os == "debian":
        #     cmd = "which nmap"
        #     cmds.append(cmd)
        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []

        cmd = "wget http://cache-address:cache-port/{}/{}.py -O ~/{}.py".format(self.app, self.app, self.name)
        cmds.append(cmd)

        cmd = "apt-get install -y python3"
        cmds.append(cmd)

        # if arch == "aarch64" and os == "debian":
        #     cmd = "apt-get install nmap"
        #     cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []

        cmd = "python3 {}.py 8001".format(self.app)
        cmds.append(cmd)
        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)
        return cmds

