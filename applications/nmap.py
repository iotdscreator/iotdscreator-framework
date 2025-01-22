import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application

class Nmap(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        if "name" in params:
            del params["name"]
        super().__init__(app, name, **params)

    # Please revise the following functions if it is different from the default way
    def check_application(self, arch="aarch64", os="debian"):
        logging.debug("Check the application: {}".format(self.app))
        cmds = []
        if os in ["debian", "ubuntu"]:
            cmd = "which nmap"
            cmds.append(cmd)
        return cmds

    def prepare_application(self, arch="aarch64", os="debian"):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []
        if os in ["debian", "ubuntu"]:
            cmd = "apt-get update --allow-releaseinfo-change"
            cmds.append(cmd)

            cmd = "apt-get install -y nmap"
            cmds.append(cmd)
        else:
            logging.error("No command is provided to prepare for {} based on {} and {}".format(self.name, arch, os))
        return cmds

    def run_application(self, arch="aarch64", os="debian", **params):
        logging.debug("Run the application: {}".format(self.app))

        target = params.get("target", None)
        scan_type = params.get("scan_type", "tcp syn")
        port_option = params.get("port_option", None)
        verbose = params.get("verbose", False)
        os_scan = params.get("os_scan", False)

        if not target:
            logging.error("{} cannot be executed".format(self.app))

        cmds = []
        if os in ["debian", "ubuntu"]:
            cmd = []
            cmd.append("nmap")
            if scan_type == "tcp syn":
                cmd.append("-sS")
            elif scan_type == "tcp":
                cmd.append("-sT")
            elif scan_type == "ping":
                cmd.append("-sP")
            elif scan_type == "ack":
                cmd.append("-sA")
            elif scan_type == "rpc":
                cmd.append("-sR")
            elif scan_type == "window":
                cmd.append("-sW")
            elif scan_type == "udp":
                cmd.append("-sU")
            elif scan_type == "fin":
                cmd.append("-sF")

            if port_option:
                cmd.append("-p")
                cmd.append(str(port_option))

            if verbose:
                cmd.append("-v")
    
            if os_scan:
                cmd.append("-O")

            cmd.append(target)
            cmds.append(' '.join(cmd))
        else:
            logging.error("No command is provided to run {} based on {} and {}".format(self.name, arch, os))
        return cmds
