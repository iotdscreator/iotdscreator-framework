import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from links.link import Link

class Wifi(Link):
    def __init__(self, node1, node2):
        super().__init__("wifi", node1, node2)
