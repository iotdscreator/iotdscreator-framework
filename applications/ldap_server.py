import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application

class LdapServer(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        super().__init__(app, name)

    # Please revise the following functions if it is different from the default way
    def check_application(self, arch=None, os=None):
        logging.debug("Check the application: {}".format(self.app))
        cmds = []

        if os in ["debian", "ubuntu"]:
            cmd = "must"
            cmds.append(cmd)
        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []
        if os in ["debian", "ubuntu"]:
            cmd = "apt-get update --allow-releaseinfo-change"
            cmds.append(cmd)

            cmd = "apt-get install -y git"
            cmds.append(cmd)
            
            cmd = "git clone https://github.com/kozmer/log4j-shell-poc.git"
            cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []

        return cmds
