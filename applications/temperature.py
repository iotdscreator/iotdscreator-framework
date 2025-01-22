import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application

class Temperature(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        if "name" in params:
            del params["name"]
        super().__init__(app, name, **params)
        self.broker = params.get("broker", "localhost")
        self.port = params.get("port", 1883)
        self.domain = params.get("domain", "home")

    # Please revise the following functions if it is different from the default way
    def prepare_application(self):
        logging.debug("Prepare the application: {}".format(self.app))
        if self.node.shell:
            cmd = "cd ~"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd)

            cmd = "git clone https://github.com/hw5773/simple-mqtt-applications.git"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "python3 -m pip install paho-mqtt"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)
        else:
            logging.error("The shell is not ready")
        super().prepare_application()

    def run_application(self):
        logging.debug("Run the application: {}".format(self.app))
        if self.node.shell:
            if not self.broker:
                logging.error("Cannot run the application {} since it does not know the broker".format(self.app))
            else:
                cmd = "cd ~/simple-mqtt-applications/temperature"
                logging.debug("cmd: {}".format(cmd))
                self.node.cmd(cmd, verbose=True)

                cmd = "python3 temperature.py -a {} -p {} -d {} -n {} &".format(self.broker, self.port, self.domain, self.name)
                logging.debug("cmd: {}".format(cmd))
                self.node.cmd(cmd)
        else:
            logging.error("The shell is not ready")
        super().run_application()
