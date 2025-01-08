import os, sys, logging
import time
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/../..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import process_error
from nodes.devices.device import Device

class Rpi3(Device):
    def __init__(self, node, **params):
        super().__init__(node, **params)
        self.shell_prompts = params.get("shell_prompts", "[\w\W]*root@raspberrypi:[\w\W]+# ")
        self.emulation = True
        self.need_expand = False
        self.account = "pi"
        self.password = "raspberry"
        node.set_shell_prompts(self.shell_prompts)

    def preparation(self):
        self.prepare_dtb()
        self.prepare_kernel()
        self.prepare_filesystem()
        super().preparation()

    # Please revise the following functions if it is different from the default way
    def prepare_dtb(self):
        conf = self.config
        pnode = self.node.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility".format(wdir))
        dtb_directory = "{}/dtb".format(image_directory)

        if pnode:
            request = {}
            request["opcode"] = "execute"
            request["command"] = "file {}/{}".format(dtb_directory, self.specification["dtb"])
            response = pnode.send_request(request, listen=False)
            process_error(request, response)

            if "No such file" in response["stdout"]:
                request["command"] = "wget https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/native-emulation/dtbs/bcm2710-rpi-3-b-plus.dtb -O {}/{}".format(dtb_directory, self.specification["dtb"])
                request["capture"] = False
                response = pnode.send_request(request, listen=False)
                process_error(request, response)

    def prepare_kernel(self):
        conf = self.config
        pnode = self.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility".format(wdir))
        kernel_directory = "{}/kernels".format(image_directory)

        if pnode:
            request = {}
            request["opcode"] = "execute"
            request["command"] = "file {}/{}".format(kernel_directory, self.specification["kernel"])
            response = pnode.send_request(request, listen=False)
            process_error(request, response)

            if "No such file" in response["stdout"]:
                request["command"] = "wget https://github.com/dhruvvyas90/qemu-rpi-kernel/raw/master/native-emulation/5.4.51%20kernels/kernel8.img -O {}/{}".format(kernel_directory, self.specification["kernel"])
                request["capture"] = False
                response = pnode.send_request(request, listen=False)
                process_error(request, response)

    def prepare_filesystem(self):
        conf = self.config
        pnode = self.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility".format(wdir))
        rootfs_directory = "{}/rootfs".format(image_directory)

        if pnode:
            request = {}
            request["opcode"] = "execute"
            request["command"] = "file {}/{}".format(rootfs_directory, self.specification["filesystem"])
            response = pnode.send_request(request, listen=False)
            process_error(request, response)

            if "No such file" in response["stdout"]:
                request["command"] = "wget https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2020-08-24/2020-08-20-raspios-buster-arm64.zip -O {}/2020-08-20-raspios-buster-arm64.zip".format(rootfs_directory)
                request["capture"] = False
                response = pnode.send_request(request, listen=False)
                process_error(request, response)

                request["command"] = "unzip {}/2020-08-20-raspios-buster-arm64.zip -d {}".format(rootfs_directory, rootfs_directory)
                request["capture"] = False
                response = pnode.send_request(request, listen=False)
                process_error(request, response)

                request["command"] = "rm {}/2020-08-20-raspios-buster-arm64.zip".format(rootfs_directory)
                response = pnode.send_request(request, listen=False)
                process_error(request, response)

                request["command"] = "qemu-img resize {}/{} 4G".format(rootfs_directory, self.specification["filesystem"])
                request["capture"] = False
                response = pnode.send_request(request, listen=False)
                process_error(request, response)

                self.need_expand = True

    def login(self):
        account = self.account
        password = self.password
        shell = False
        panic = False
        insert_account = False
        insert_password = False

        pnode = self.get_pnode()
        vtype = self.node.get_virtualization_type()
        request = {}

        while True:
            output = ""

            while True:
                request["opcode"] = "listen"
                request["type"] = vtype
                request["name"] = self.get_name()
                request["amount"] = 3800
                response = pnode.send_request(request, listen=False)
                out = response["stdout"]
                try:
                    output += out
                except:
                    continue

                if "Kernel panic" in output:
                    logging.debug(output)
                    panic = True
                    break

                if "raspberrypi login:" in output:
                    logging.debug("output: {}".format(output))
                    request["opcode"] = "control"
                    request["command"] = account
                    pnode.send_request(request, listen=False)
                    process_error(request, response)
                    insert_account = True
                    break

                elif "Password:" in output:
                    logging.debug("output: {}".format(output))
                    request["opcode"] = "control"
                    request["command"] = password
                    pnode.send_request(request, listen=False)
                    process_error(request, response)
                    insert_password = True
                    break
                
                elif "pi@raspberrypi:~$" in output:
                    logging.debug("output: {}".format(output))
                    request["opcode"] = "control"
                    request["command"] = "sudo su"
                    pnode.send_request(request, listen=False)
                    process_error(request, response)
                    break

                elif "root@raspberrypi:/home/pi#" in output:
                    logging.debug("output: {}".format(output))
                    request["opcode"] = "control"
                    request["command"] = "cd ~"
                    pnode.send_request(request, listen=False)
                    process_error(request, response)
                    break

                elif "root@raspberrypi:~#" in output:
                    logging.debug("output: {}".format(output))
                    if insert_account and insert_password:
                        shell = True
                    break

                elif "\n" in output:
                    if "My IP address is " in output:
                        tmp = output.split(" ")
                        for e in tmp:
                            if "." in e:
                                ipaddr = e
                        logging.info("Set default IP address: {}".format(ipaddr))
                        inf = self.get_default_interface().set_ip_address(ipaddr)
                    logging.debug(output)
                    break

            if shell or panic:
                break

        if shell:
            logging.info("  => Signing in succeed ({})".format(self.get_name()))
        elif panic:
            logging.info("  => Failing to sign in ({})".format(self.get_name()))

    def initialization(self):
        conf = self.config
        pnode = self.get_pnode()
        wdir = pnode.get_working_directory()
        image_directory = "{}/extensibility".format(wdir)
        if conf:
            image_directory = conf.get("image_directory", "{}/extensibility".format(wdir))
        rootfs_directory = "{}/rootfs".format(image_directory)
        vtype = self.node.get_virtualization_type()

        self.login()

        logging.debug("self.need_expand: {}".format(self.need_expand))
        if self.need_expand:
            logging.debug("need to expand the rootfs")

            request = {}
            request["opcode"] = "control"
            request["type"] = vtype
            request["name"] = self.get_name()
            request["command"] = "raspi-config nonint do_expand_rootfs"
            response = pnode.send_request(request, listen=False)
            process_error(request, response)

            request["command"] = "reboot"
            response = pnode.send_request(request, listen=False)
            process_error(request, response)

            self.login()

            """
            request["opcode"] = "execute"
            tname1 = "{}/tmp1.qcow2".format(rootfs_directory)
            tname2 = "{}/tmp2.qcow2".format(rootfs_directory)
            request["command"] = "cp {} {}".format("{}/{}".format(rootfs_directory, self.specification["filesystem"]),  tname1)
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "qemu-img convert -f qcow2 -O raw {} {}".format(tname1, tname2)
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "rm {}/{}".format(rootfs_directory, self.specification["filesystem"])
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "mv {} {}/{}".format(tname2, rootfs_directory, self.specification["filesystem"])
            response = pnode.send_request(request)
            process_error(request, response)

            request["command"] = "rm {}".format(tname1)
            response = pnode.send_request(request)
            process_error(request, response)
            """

            self.need_expand = False

            logging.debug("expand the rootfs success")
