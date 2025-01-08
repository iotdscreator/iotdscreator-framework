import os, sys, argparse, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import camel_code

def generate_template(name, arch=None, preset=False):
    fname = "{}/nodes/devices/{}.py".format(root_directory, name)

    with open(fname, "w") as f:
        f.write("import os, sys, logging\n")
        f.write("import pathlib\n")
        f.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        f.write("root_directory = os.path.abspath(\"{}/../..\".format(fpath))\n")
        f.write("from devices.device import Device, DeviceShell\n\n")
        f.write("class {}(Device):\n".format(camel_code(name)))
        f.write("    def __init__(self, name, preset=None, shell_prompts=None, **params):\n")
        f.write("        self.preset = params.get(\"preset\", preset)\n")
        f.write("        self.net = params.get(\"net\", None)\n")
        f.write("        self.params.setdefault(\"net\", net)\n")
        f.write("        self.shell_prompts = shell_prompts\n")
        f.write("        super().__init__(name, preset=preset, shell_prompts=shell_prompts, **params)\n\n")
        f.write("    # Please revise the following functions if it is different\n")
        f.write("      from the default way\n")
        f.write("    def prepare_dtb(self):\n")
        f.write("        return super().prepare_dtb()\n\n")
        f.write("    def prepare_kernel(self):\n")
        f.write("        return super().prepare_kernel()\n\n")
        f.write("    def prepare_filesystem(self):\n")
        f.write("        return super().prepare_filesystem()\n\n")
        f.write("    def prepare_firmware(self):\n")
        f.write("        return super().prepare_firmware()\n\n")

    pname = None
    if preset:
        if not arch:
            logging.error("The architecture must be specified if you want to make a preset")
            sys.exit(1)

        pname = "{}/nodes/devices/presets/{}.spec".format(root_directory, name)

        with open(pname, "w") as f:
            f.write("# Hardware Resource\n")
            f.write("architecture: {}\n".format(arch))
            f.write("cpu: {}\n".format(cpu))
            f.write("memory: 1G\n")
            f.write("machine: {}\n".format(machine))
            f.write("\n")
            f.write("# Software Stack\n")
            f.write("hardware security: none\n")
            if firmware:
                f.write("firmware: {}\n".format(firmware))
            if dtb:
                f.write("dtb: {}\n".format(dtb))
            if kernel:
                f.write("kernel: {}\n".format(kernel))
            if filesystem:
                f.write("filesystem: {}\n".format(filesystem))
            f.write("\n")
            f.write("# Network Interface\n")
            f.write("interface:\n")
            f.write("  - name: eth0\n")
            f.write("    type: ethernet\n")
            f.write("\n")
            f.write("# Others\n")
            f.write("append: rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootdelay=1\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, metavar="<device model name>", help="Device model name", type=str)
    parser.add_argument("-a", "--architecture", dest=arch, metavar="<cpu architecture>", help="CPU architecture", type=str, default=None)
    parser.add_argument("-d", "--dtb", metavar="<dtb file>", help="DTB file", type=str, default=None)
    parser.add_argument("-f", "--firmware", metavar="<firmware file>", help="Firmware file", type=str, default=None)
    parser.add_argument("-k", "--kernel", metavar="<kernel image>", help="Kernel image file", type=str, default=None)
    parser.add_argument("-r", "--rootfs", metavar="<filesystem image>", help="Filesystem image file", type=str, default=None)
    parser.add_argument("-p", "--preset", metavar="<preset>", help="whether to make a preset (True/False)", action="store_true")
    parser.add_argument("-l", "--log", metavar="<log level=DEBUG/INFO/WARNING/ERROR>", help="Log level (DEBUG/INFO/WARNING/ERROR)", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    name = args.name

    fname = "{}/nodes/devices/{}.py".format(root_directory, name)

    if os.path.exists(fname):
        logging.error("The same name of the device exists. Please insert another name for the device")
        sys.exit(1)

    generate_template(name)

if __name__ == "__main__":
    main()
