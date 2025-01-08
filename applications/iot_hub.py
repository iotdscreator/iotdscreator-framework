import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application

class IotHub(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        super().__init__(app, name)
        self.broker = params.get("broker", "0.0.0.0")
        self.port = params.get("port", 1883)
        self.domain = params.get("domain", "home")

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
            cmd = "apt-get install -y git"
            cmds.append(cmd)
            cmd = "apt-get install -y python3-pip"
            cmds.append(cmd)
            cmd = "cd ~"
            cmds.append(cmd)
            cmd = "git clone https://github.com/hw5773/simple-mqtt-applications.git"
            cmds.append(cmd)
            cmd = "python3 -m pip install paho-mqtt"
            cmds.append(cmd)

        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []
        broker = params.get("broker", "0.0.0.0")
        port = params.get("port", 1883)
        domain = params.get("domain", "home")
        
        if os in ["debian", "ubuntu"]:
            cmd = "cd ~/simple-mqtt-applications/iot_hub"
            cmds.append(cmd)

            if not self.broker:
                self.broker = broker

            if not self.port:
                self.port = port

            if not self.domain:
                self.domain = domain

            cmd = "python3 iot_hub.py -a {} -p {} -d {} -n {} &".format(self.broker, self.port, self.domain, self.name)
            cmds.append(cmd)

        return cmds
