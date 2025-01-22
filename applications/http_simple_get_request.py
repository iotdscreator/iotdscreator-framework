import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class HttpSimpleGetRequest(Application):
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
        cmd = "which curl"
        cmds.append(cmd)
        # if arch == "aarch64" and os == "debian":
        #     cmd = "which nmap"
        #     cmds.append(cmd)
        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []
        if os in ["debian", "ubuntu"]:
            cmd = "apt-get update --allow-releaseinfo-change"
            cmds.append(cmd)

            cmd = "apt-get install -y curl"
            cmds.append(cmd)
        else:
            logging.error("No command is provided to prepare for {} based on {} and {}".format(self.name, arch, os))
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))

        names = params.get("names", None)
        target = params.get("target", None)
        if names:
            if target in names:
                target = names[target]
        port = params.get("port", 8001)
        output = params.get("output", "index.html")
        request = "http://{}:{}".format(target, port)

        cmds = []

        if target:
            cmd = "curl {} -o {}".format(request, output)
            cmds.append(cmd)
        
            logging.error("request: {}".format(request))
            logging.error("cmd: {}".format(cmd))
        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)
        return cmds

