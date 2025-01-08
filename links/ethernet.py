import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from links.link import Link
from iutils.etc import process_error

class Ethernet(Link):
    def __init__(self, node1, node2):
        super().__init__("ethernet", node1, node2)
        n1 = self.get_node1()
        n2 = self.get_node2()

        if n1 and n2:
            self.name = "link-{}-eth-{}".format(n1.get_name(), n2.get_name())

    def create(self):
        i1 = self.get_intf1()
        i2 = self.get_intf2()

        n1 = self.get_node1()
        n2 = self.get_node2()

        pnode1 = None
        pnode2 = None

        if n1:
            pnode1 = n1.get_pnode()
        if n2:
            pnode2 = n2.get_pnode()

        if not pnode1 and not pnode2:
            logging.error("There are no corresponing physical nodes")
            sys.exit(1)

        if i1.get_name() == "internet" or i2.get_name() == "internet":
            self._create_internet_link()
        elif not pnode1 or not pnode2:
            self._create_intra_link()
        elif pnode1.get_name() == pnode2.get_name():
            self._create_intra_link()
        else:
            self._create_inter_link()

    def _create_internet_link(self):
        logging.debug("Start: _create_internet_link()")
        i1 = self.get_intf1()
        i2 = self.get_intf2()

        iname = i1.get_external_ifname()
        if i1.get_name() == "internet":
            iname = i2.get_external_ifname()
        
        n1 = self.get_node1()
        n2 = self.get_node2()
        if n1:
            n = n1
        else:
            n = n2

        pnode = n.get_pnode()
        vtype = n.get_virtualization_type()
        
        if vtype == "qemu":
            request = {}
            request["opcode"] = "execute"
            request["command"] = "ip link set {} master internet".format(iname)
            response = pnode.send_request(request)
            process_error(request, response)
            logging.debug("Finish: _create_internet_link()")

    def _create_intra_link(self):
        logging.debug("Start: _create_intra_link()")
        n1 = self.get_node1()
        n2 = self.get_node2()

        if not n1:
            n = n2
        else:
            n = n1

        pnode = n.get_pnode()
        name = self.get_name()

        i1 = self.get_intf1()
        i2 = self.get_intf2()

        request = {}
        request["opcode"] = "execute"
        request["command"] = "ip link add {} type bridge".format(name)
        response = pnode.send_request(request)
        process_error(request, response)

        request["command"] = "ip link set {} up".format(name)
        response = pnode.send_request(request)
        process_error(request, response)

        request["command"] = "ip link {} set master {}".format(i1.get_name(), name)
        response = pnode.send_request(request)
        process_error(request, response)

        request["command"] = "ip link {} set master {}".format(i2.get_name(), name)
        response = pnode.send_request(request)
        process_error(request, response)
        logging.debug("Finish: _create_intra_link()")

    def _create_inter_link(self):
        pass
