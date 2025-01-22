import os, sys, logging
import pathlib
import requests
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class HostInfoReporter(Application):
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
        if os in ["debian", "ubuntu"]:
            cmd = "must"
            cmds.append(cmd)
        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []
        if os in ["debian", "ubuntu"]:
            cmd = "wget http://cache-address:cache-port/{}/{}.sh -O ~/{}.sh".format(self.app, self.app, self.name)
            cmds.append(cmd)
            cmd = "chmod 777 ~/{}.sh".format(self.name)
            cmds.append(cmd)
            cmd = "apt-get install -y atop netcat"
            cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []
        dname = params.get("device name", None)
        addr = params.get("address", None)
        port = params.get("port", None)
        application = params.get("application", None)
        interval = params.get("interval", 10)
        logging.debug("dname: {}, addr: {}, port: {}, application: {}, interval: {}".format(dname, addr, port, application, interval))

        if os in ["debian", "ubuntu"]:
            cmd = "~/{}.sh {} {} {} {} {}".format(self.name, dname, addr, port, application, interval)
            logging.debug("cmd: {}".format(cmd))
            cmds.append(cmd)
        return cmds

