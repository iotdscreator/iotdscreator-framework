import os, sys, logging
import re
import time
import random
import psutil
import subprocess
from ipaddress import IPv4Network
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application
from iutils.etc import process_error
COMMAND_SLEEP_TIME=2

class DummyInterface:
    def __init__(self, nname, iname, index):
        self.name = iname

    def get_interface_name(self):
        return self.name
