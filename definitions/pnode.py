import os, sys, logging
import socket
import json
import pathlib
import re
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import process_error

class PNode:
    def __init__(self, info, timeout=5):
        self.ipaddr = info.get("ipaddr", None)
        self.port = info.get("port", None)
        self.timeout = timeout

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

        self.resource = {}

    def send_request(self, request, listen=True):
        if not isinstance(request, dict):
            return None
        response = None
        retry = 0
        sock = self.socket

        logging.debug("Request: {}".format(request))
        while not response and retry < 3:
            sock.sendto(json.dumps(request).encode(), (self.ipaddr, self.port))
            response, _ = sock.recvfrom(4096)
        if response:
            logging.debug("Response: {}".format(response))
            response = json.loads(response)

        if request.get("opcode", None) == "control" and request.get("type", None) == "qemu":
            if listen:
                output = self.receive_response(request)
                response["stdout"] = output
        return response

    def receive_response(self, request):
        logging.debug("command in receive_response(): {}".format(request["command"]))
        request["opcode"] = "listen"
        request["amount"] = 3800
        if "name" not in request:
            logging.error("The name of the device must be specified if you want to listen to the device")
            sys.exit(1)

        if "shell" not in request:
            logging.error("The shell prompt must be specified if you want to listen to the device")
            sys.exit(1)

        shell = request["shell"].strip()
        output = ""
        while True:
            response = self.send_request(request)
            process_error(request, response)
            out = response["stdout"]
            output += out

            if re.match(shell, output):
                logging.debug("output: {}".format(output))
                break
        return output

    def set_working_directory(self, wdir):
        self.working_directory = wdir

    def get_name(self):
        return "pnode-{}:{}".format(self.ipaddr, self.port)

    def get_working_directory(self):
        return self.working_directory

    def get_ip_address(self):
        return self.ipaddr

    def get_port(self):
        return self.port

    def set_timeout(self, timeout):
        self.timeout = timeout
        self.socket.settimeout(timeout)

    def get_timeout(self):
        return self.timeout

    def get_socket(self):
        return self.socket

    def set_resource(self, key, value):
        self.resource[key] = value

    def get_resource(self, key):
        return self.resource[key]

    def get_resources(self):
        return self.resource
