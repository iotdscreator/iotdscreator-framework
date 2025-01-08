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

class QemuShell:
    def __init__(self, pnode, pipe_in, pipe_out):
        self.pnode = pnode
        self.pipe_in = pipe_in
        self.pipe_out = pipe_out

    def get_pipe_in(self):
        return self.pipe_in

    def get_pipe_out(self):
        return self.pipe_out

class QemuInterface:
    def __init__(self, nname, iname, index):
        self.name = iname
        external = "{}-tap{}".format(nname, index)
        internal = "usb{}".format(index)
        self.external = external
        self.internal = internal
        logging.debug("external: {}, internal: {}".format(external, internal))

    def get_interface_name(self):
        return self.name

    def get_external_ifname(self):
        return self.external

    def set_external_ifname(self, name):
        self.external = name

    def get_internal_ifname(self):
        return self.internal

    def set_internal_ifname(self, name):
        self.internal = name

class QemuFunctions:
    def __init__(self, node):
        self.taps = []
        self.mnum = 0
        self.bnum = 0
        self.download_server = None
        self.shell = None
        self.node = node

        self.specification = node.get_specification()
        self.interfaces = node.get_interfaces()

    def make_pipe(self):
        pnode = self.node.get_pnode()
        pname = "/tmp/{}-pipe".format(self.node.get_name())
        logging.debug("pipe name: {}".format(pname))

        try:
            pin = "{}.in".format(pname)
            pout = "{}.out".format(pname)
            logging.debug("pin: {}, pout: {}".format(pin, pout))
            request = {}
            request["opcode"] = "execute"
            request["command"] = "rm {}".format(pin)
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            request["command"] = "rm {}".format(pout)
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            request["command"] = "mkfifo {}".format(pin)
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "chmod 666 {}".format(pin)
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "mkfifo {}".format(pout)
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "chmod 666 {}".format(pout)
            response = pnode.send_request(request)
            process_error(request, response, sleep=COMMAND_SLEEP_TIME)

            logging.info(" - Creating a pipe ({}) for a node {}".format(pname, self.node.get_name()))
        except:
            logging.error("Failed to create pipe: {}".format(pname))
            logging.error("Please try again after checking if the pipe works well")
            sys.exit(1)

        self.shell = QemuShell(pnode, pin, pout)

    def make_interfaces(self):
        pnode = self.node.get_pnode()
        interfaces = self.interfaces

        request = {}
        request["opcode"] = "execute"
        for interface in interfaces:
            external = interfaces[interface].get_external_ifname()
            request["command"] = "ip tuntap add {} mode tap".format(external)
            response = pnode.send_request(request)
            process_error(request, response)
            time.sleep(0.5)

            request["command"] = "ip link set {} up".format(external)
            response = pnode.send_request(request)
            process_error(request, response)
            time.sleep(0.5)

            request["command"] = "iptables -t filter -I FORWARD 1 -i {} -o {} -j ACCEPT".format(external, external)
            response = pnode.send_request(request)
            process_error(request, response)
            time.sleep(0.5)

        time.sleep(1)

    def get_shell(self):
        return self.shell

    def get_pipe_in(self):
        return self.shell.get_pipe_in()

    def get_pipe_out(self):
        return self.shell.get_pipe_out()

    def run_vm(self):
        logging.info(" - Running VM ({})".format(self.node.get_name()))
        conf = self.node.get_configuration()
        pnode = self.node.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility".format(wdir))
        pname = "/tmp/{}-pipe".format(self.node.get_name())
        dtb = "{}/dtb/{}".format(image_directory, self.specification["dtb"])
        kernel = "{}/kernels/{}".format(image_directory, self.specification["kernel"])
        filesystem = "{}/rootfs/{}".format(image_directory, self.specification["filesystem"])

        cmd = []
        cmd.append("qemu-system-{}".format(self.specification["architecture"]))
        cmd.append("-machine")
        cmd.append(self.specification["machine"])
        cmd.append("-cpu")
        cmd.append(self.specification["cpu"])
        if "smp" in self.specification:
            cmd.append("-smp")
            cmd.append(str(self.specification["smp"]))
        cmd.append("-m")
        cmd.append(str(self.specification["memory"]))
        cmd.append("-dtb")
        cmd.append(dtb)
        cmd.append("-kernel")
        cmd.append(kernel)
        cmd.append("-drive")
        if ".img" in filesystem:
            cmd.append("file={},format=raw".format(filesystem))
        else:
            cmd.append("file={}".format(filesystem))
        cmd.append("-serial")
        cmd.append("pipe:{}".format(pname))
        cmd.append("-display")
        cmd.append("none")

        idx = 0
        for inum in self.interfaces:
            intf = self.interfaces[inum]
            self.mnum = (self.mnum + 1) % 256
            mac = intf.get_macaddr()

            cmd.append("-device")
            if self.specification["machine"] == "raspi3":
                cmd.append("usb-net,netdev=network{},mac={}".format(idx, mac))
            elif self.specification["machine"] == "raspi3b":
                cmd.append("usb-net,netdev=network{},mac={}".format(idx, mac))
            else:
                cmd.append("virtio-net-pci,netdev=network{},mac={}".format(idx, mac))
            cmd.append("-netdev")
            cmd.append("tap,id=network{},ifname={},script=no,downscript=no".format(idx, intf.get_external_ifname()))
            idx += 1

        cmd.append("-append")
        cmd.append("'{}'".format(self.specification["append"]))

        logging.debug("cmd: {}".format(' '.join(cmd)))
        request = {}
        request["opcode"] = "execute"
        request["command"] = ' '.join(cmd)
        request["capture"] = False
        request["background"] = True
        request["timeout"] = 0
        response = pnode.send_request(request)
        process_error(request, response, ignore=True, sleep=COMMAND_SLEEP_TIME)

    def get_name(self):
        return self.name

    def prepare_dtb(self):
        conf = self.node.get_configuration()
        pnode = self.node.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility/images".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility/images".format(wdir))
        dtb_directory = "{}/dtb".format(image_directory)
        return os.path.abspath("{}/{}".format(dtb_directory, self.specification["dtb"]))

    def prepare_kernel(self):
        conf = self.node.get_configuration()
        pnode = self.node.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility/images".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility/images".format(wdir))
        kernel_directory = "{}/kernel".format(image_directory)
        return os.path.abspath("{}/{}".format(kernel_directory, self.specification["kernel"]))

    def get_backing_vm_name(self):
        conf = self.node.get_configuration()
        pnode = self.node.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility/images".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility/images".format(wdir))
        rootfs_directory = "{}/rootfs".format(image_directory)

        name = self.specification["filesystem"]
        apps = [ a.get_name() for a in self.node.applications ]
        logging.debug("apps: {}".format(apps))
        # TODO: Need to log applications somewhere to remove duplications
        return "{}/{}".format(rootfs_directory, name)

    def prepare_filesystem(self):
        conf = self.node.get_configuration()
        pnode = self.node.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility/images".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility/images".format(wdir))
        rootfs_directory = "{}/rootfs".format(image_directory)

        fname, ext = self.specification["filesystem"].split(".")
        bname = self.get_backing_vm_name()
        rname = "{}/{}-{}-{}.qcow2".format(rootfs_directory, fname, self.node.get_name(), int(time.time()))
        logging.debug("bname: {}, rname: {}".format(bname, rname))

        cmd = []
        cmd.append("qemu-img")
        cmd.append("create")
        cmd.append("-f")
        cmd.append("qcow2")
        cmd.append("-F")

        bext = bname.split(".")[-1].strip()
        if "img" in bext:
            cmd.append("raw")
        elif "qcow2" in bext:
            cmd.append("qcow2")

        cmd.append("-o")
        cmd.append("backing_file={}".format(bname))
        cmd.append("{}".format(rname))
        logging.debug("cmd: {}".format(' '.join(cmd)))

        pnode = self.node.get_pnode()
        request = {}
        request["opcode"] = "execute"
        request["command"] = ' '.join(cmd)
        response = pnode.send_request(request)
        process_error(request, response, sleep=COMMAND_SLEEP_TIME)

        self.filesystem = rname

        return rname

    def configure(self):
        self.make_pipe()
        self.make_interfaces()

    def start(self):
        self.run_vm()
            
    def apply(self, dns=None):
        pass

    def stop(self):
        pnode = self.node.get_pnode()
        request = {}
        request["opcode"] = "execute"
        
        if hasattr(self, "filesystem"):
            cmd = "rm {}".format(self.filesystem)
            request["command"] = cmd
            logging.debug("cmd: {}".format(cmd))
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

        cmd = "killall qemu-system-arm"
        request["command"] = cmd
        logging.debug("cmd: {}".format(cmd))
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        cmd = "killall qemu-system-aarch64"
        request["command"] = cmd
        logging.debug("cmd: {}".format(cmd))
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

    def network_setting(self):
        assert self.shell

        cmd = "echo \"nameserver 8.8.8.8\" > /etc/resolv.conf"
        logging.debug("cmd: {}".format(cmd))
        output = self.cmd(cmd)
        cmd = "cat /etc/resolv.conf" 
        logging.debug("\n\n=====")
        logging.debug("cmd: {}".format(cmd))
        output = self.cmd(cmd)
        logging.debug("=====\n\n")

        if self.download_server is not None:
            cmd = "echo \"{} {}\" >> /etc/hosts".format(self.download_server[1], self.download_server[0])
            logging.debug("cmd: {}".format(cmd))
            output = self.cmd(cmd)

        #cmd = "ifconfig | grep mtu -A4"
        cmd = "ifconfig"
        logging.debug("cmd: {}".format(cmd))
        output = self.cmd(cmd)
        logging.debug("output: {}".format(output))
        tmp = output.split("\r\n\r\n")
        logging.debug("tmp: {}".format(tmp))
        ifinfos = []
        for ifname in tmp:
            name = ifname.split(":")[0].strip().split("\n")[-1].strip()
            logging.debug("name: {}".format(name))
            if "lo" in name:
                continue

            #if "ifconfig" in ifname:
            #    continue

            if "raspberrypi" in name:
                continue

            logging.debug("ifname: {}".format(ifname))
            addr = ifname.split("inet")[1].strip().split(" ")[0].strip()
            netmask = ifname.split("netmask")[1].strip().split(" ")[0].strip()
            nbits = IPv4Network("0.0.0.0/{}".format(netmask)).prefixlen
            mac = ifname.split("ether")[1].strip().split(" ")[0].strip()
            logging.debug("name: {}, addr: {}, nbits: {}, mac: {}".format(name, addr, nbits, mac))
            ifinfos.append((name, addr, nbits, mac))
        intfs = list(self.ports.keys())
        logging.debug("intfs: {}, ifinfos: {}".format(intfs, ifinfos))
        for i in range(len(ifinfos)):
            binding = False

            intf = None
            for interface in intfs:
                if ifinfos[i][3][10:] == interface.get_mac()[10:]:
                    binding = True
                    intf = interface
                    intfs.remove(intf)

            if not binding:
                intf = intfs.pop(0)

            logging.debug("pair: internal: {} ({}), external: {} ({})".format(ifinfos[i][0], ifinfos[i][3], intf.external, intf.mac))
            intf.set_internal(ifinfos[i][0])
            intf.ip = ifinfos[i][1]
            intf.prefixLen = ifinfos[i][2]

    def run_applications(self):
        cmd = "killall apt apt-get"
        logging.debug("cmd: {}".format(cmd))
        output = self.cmd(cmd)

        cmd = "apt-get update --allow-releaseinfo-change"
        logging.debug("cmd: {}".format(cmd))
        output = self.cmd(cmd, verbose=True)

        for a in self.applications:
            logging.debug("Run the application: {}".format(a.name))
            a.prepare_application()
            a.run_application()

    def check_shell(self):
        if self.is_running():
            if self.shell:
                self.shell.poll()
                if self.shell.returncode is not None:
                    logging.error("Shell died for the device {}".format(self.name))
                    self.shell = None
                    logging.error("Restarting the shell for the device {}".format(self.name))
                    self.startShell()
            else:
                logging.error("Restarting the shell for the device {}".format(self.name))
                self.startShell()
        else:
            logging.error("Unable to connect to the device {}".format(self.name))
            if self.shell:
                self.shell = None

    def is_running(self):
        ret = False
        for pid in psutil.pids():
            p = psutil.Process(pid)
            if "pipe:/tmp/{}-pipe".format(self.name) in p.cmdline():
                ret = True
                break
        return ret

    def set_net(self, net):
        self.net = net

    def get_net(self):
        return self.net

    def set_download_server(self, name, ipaddr):
        if name and ipaddr:
            self.download_server = (name, ipaddr)

    # Methods to be used in the scenarios 
    # (the camel code naming rule is used, following the convention of the mininet)
    def startShell(self):
        pass

    def sendCmd(self, *args, **kwargs):
        self.check_shell()
        if not self.shell:
            return

        #if self.pipe_in:
        pin = os.open(self.shell.pipe_in, os.O_WRONLY)
        logging.debug("Command to be executed: {}".format(*args))
        os.write(pin, "{}\n".format(*args).encode())
        os.close(pin)

    def waitOutput(self, verbose=True, findPid=True):
        output = ""
        if not self.shell:
            return output

        pout = os.open(self.shell.pipe_out, os.O_RDONLY)
        while True:
            out = os.read(pout, 1)
            try:
                output += out.decode()
            except:
                continue

            if re.match(self.shell_prompts, output):
                break

            #if self.shell_prompts in output:
            #    break

            if verbose:
                tmp = out.decode()
                if tmp == "\r":
                    output += "\n"
    
                if len(output) > 0 and output[-1] == "\n":
                    if len(output) > 1:
                        print (output, end="")
                    output = ""

        logging.debug("Output to be returned: {}".format(output))
        os.close(pout)
        return output

    def addIntf(self, intf, **params):
        self.taps.append(intf.external)
        super().addIntf(intf, **params)

    def showIntfs(self):
        logging.debug("{}'s interfaces >>>".format(self.get_name()))
        # self.ports: interface -> port number
        # self.intfs: port number -> interface
        for intf in self.ports:
            logging.debug("  {}: {}".format(intf.internal, intf.ip))

    def addApplication(self, app, **params):
        cls = get_application_class(app)
        if cls:
            self.applications.append(cls(app, self, **params))
        else:
            logging.error("The application {} is unavailable".format(app))
            sys.exit(1)
