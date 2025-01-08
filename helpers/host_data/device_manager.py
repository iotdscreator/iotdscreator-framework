import argparse
import socket
import logging
import time
import sys
import threading
import asyncio
sys.path.append("..")
from definitions.device import Device

class DeviceManager:
    def __init__(self, core):
        logging.debug("DeviceManager Initialization")
        self.core = core
        self.devices = {}
        self.serial = 0

    def put_device(self, addr, port):
        if self.get_device_by_address(addr, port) == None:
            self.serial += 1
            self.devices[self.serial] = Device(self.serial, addr, port)
        return self.devices[self.serial]

    def get_device_by_address(self, addr, port):
        ret = None
        for serial in self.devices:
            dev = self.devices[serial]
            if dev.get_address() == addr and dev.get_port() == port:
                ret = dev
        return ret

    def get_device_by_serial(self, serial):
        ret = None
        if serial in self.devices:
            ret = self.devices[serial]
        return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    DeviceManager(None)

if __name__ == "__main__":
    main()
