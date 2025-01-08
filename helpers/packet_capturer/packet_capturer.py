import os, sys, argparse, logging
import time
import subprocess
import base64
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from definitions.packet import Packet
from iutils.etc import check_file_availability
from iutils.etc import check_interface_availability
from iutils.etc import load_configuration_file

class PacketCapturer:
    def __init__(self, config, pnode, name, interface):
        self.config = config
        self.pnode = pnode
        self.name = name
        self.interface = interface

    def run(self, timestamp):
        ofprefix = self.config.get("name", "noname")
        interface = self.interface
        name = self.name
        if not name:
            name = "internet"
        self.ofname = "{}-{}-{}-{}.pcap".format(ofprefix, name, interface, timestamp)
        self.filepath = None
        request = {}
        request["opcode"] = "capture"
        request["command"] = "tcpdump -i {}".format(self.interface)
        request["filename"] = self.ofname
        request["background"] = True
        request["timeout"] = 0 

        pnode = self.pnode
        response = pnode.send_request(request)
        self.pid = response["pid"]

    def stop(self):
        request = {}
        request["opcode"] = "execute"
        request["command"] = "kill -SIGINT {}".format(self.pid)

        pnode = self.pnode
        response = pnode.send_request(request)

    def get(self):
        request = {}
        request["opcode"] = "upload"
        request["filename"] = self.ofname

        pnode = self.pnode
        response = pnode.send_request(request)
        rc = response["resultcode"]
        total = response.get("total", 1)
        if rc == 0:
            odir = self.config.get("output_directory", root_directory)
            odir = os.path.expanduser(odir)

            if not os.path.exists(odir):
                os.mkdir(odir)

            self.filepath = "{}/{}".format(odir, self.ofname)

            with open(self.filepath, "wb") as of:
                for i in range(total):
                    request["sequence"] = i
                    response = pnode.send_request(request)
    
                    if response.get("sequence", -1) == i:
                        content = base64.b64decode(response["content"].encode())
                        of.write(content)
                    else:
                        logging.error("Fail to get the packet capture file: {}".format(self.ofname))
                        sys.exit(1)
        elif rc == 1:
            logging.error("Fail to get the packet capture file: {}".format(self.ofname))
            sys.exit(1)
       
    def get_interface_name(self):
        return self.interface

    def get_network_log_filename(self):
        return self.filepath
