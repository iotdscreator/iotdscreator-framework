import os, sys, logging
import pathlib
import random
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/../..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from common.qemu import QemuInterface
from common.docker import DockerInterface
from common.dummy import DummyInterface

class Intf:
    def __init__(self, node, name, itype, index):
        self.node = node
        self.name = name
        self.itype = itype
        self.index = index
        self.funcs = self._init_functions()
        self.ipaddr = None
        self.nbits = 0

        m = []
        for _ in range(6):
            m.append("{:#04x}".format(random.randint(0, 256))[-2:])
        self.macaddr = ":".join(m)
        self.link = None

    def _init_functions(self):
        ret = None
        nname = None
        if self.node:
            nname = self.node.get_name()
        iname = self.get_name()
        ftype = self.get_ftype()
        idx = self.get_index()

        if ftype == "qemu":
            ret = QemuInterface(nname, iname, idx)
        elif ftype == "docker":
            ret = DockerInterface(nname, iname, idx)
        elif ftype == "dummy":
            ret = DummyInterface(nname, iname, idx)
        return ret

    def get_name(self):
        return self.name

    def get_itype(self):
        return self.itype

    def get_index(self):
        return self.index

    def get_ftype(self):
        ret = "dummy"
        if self.node:
            ret = self.node.get_virtualization_type()
        return ret

    def set_ipaddr(self, ipaddr):
        self.ipaddr = ipaddr

    def get_ipaddr(self):
        return self.ipaddr
    
    def set_macaddr(self, macaddr):
        self.macaddr = macaddr

    def get_macaddr(self):
        return self.macaddr

    def set_link(self, link):
        self.link = link

    def get_link(self):
        return self.link

    def get_external_ifname(self):
        ret = None
        if self.funcs:
            ret = self.funcs.get_external_ifname()
        return ret

    def set_external_ifname(self, name):
        if self.funcs:
            self.funcs.set_external_ifname(name)

    def get_internal_ifname(self):
        ret = None
        if self.funcs:
            ret = self.funcs.get_internal_ifname()
        return ret

    def set_internal_ifname(self, name):
        if self.funcs:
            self.funcs.set_internal_ifname(name)
