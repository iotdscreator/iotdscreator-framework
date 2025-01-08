import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from links.ethernet import Ethernet
from links.wifi import Wifi

class Edge:
    def __init__(self, etype, node1, intf1, node2, intf2):
        self.node = {}
        self.node[0] = {}
        self.node[0]["node"] = node1
        self.node[0]["interface"] = intf1

        self.node[1] = {}
        self.node[1]["node"] = node2
        self.node[1]["interface"] = intf2

        self.link = self._init_link(etype)

    def _init_link(self, etype):
        ret = None
        if etype == "ethernet":
            ret = Ethernet(self.node[0], self.node[1])
        elif etype == "wifi":
            ret = Wifi(self.node[0], self.node[1])
        return ret

    def get_node(self, idx):
        return self.node[idx]

    def get_link(self):
        return self.link

    def create(self):
        self.link.create()
