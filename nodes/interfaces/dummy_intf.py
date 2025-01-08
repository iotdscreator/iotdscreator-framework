import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/../..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from nodes.interfaces.interface import Intf

class DummyIntf(Intf):
    def __init__(self, node, name, idx):
        super().__init__(node, name, "ethernet", idx)
