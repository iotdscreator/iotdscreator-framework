import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application

class MqttBroker(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        if "name" in params:
            del params["name"]
        super().__init__(app, name, **params)

    # Please revise the following functions if it is different from the default way
    def prepare_application(self):
        logging.debug("Prepare the application: {}".format(self.app))
        if self.node.shell:
            cmd = "apt-get update --allow-releaseinfo-change"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "apt-get install -y software-properties-common"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "apt-key add mosquitto-repo.gpg.key"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "pushd /etc/apt/sources.list.d/"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "wget http://repo.mosquitto.org/debian/mosquitto-jessie.list"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "wget http://repo.mosquitto.org/debian/mosquitto-stretch.list"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "wget http://repo.mosquitto.org/debian/mosquitto-buster.list"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "popd"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "apt-get update --allow-releaseinfo-change"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

            cmd = "apt-get install -y mosquitto"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)

        else:
            logging.error("The shell is not ready")
        super().prepare_application()

    def run_application(self):
        logging.debug("Run the application: {}".format(self.app))
        if self.node.shell:
            cmd = "mosquitto -v &"
            logging.debug("cmd: {}".format(cmd))
            self.node.cmd(cmd, verbose=True)
        else:
            logging.error("The shell is not ready")
        super().run_application()

