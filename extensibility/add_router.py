import os, sys, argparse, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import camel_code

def generate_template(name, arch=None, preset=False):
    fname = "../nodes/routers/{}.py".format(name)

    with open(fname, "w") as f:
        f.write("import os, sys, logging\n")
        f.write("import pathlib\n")
        f.write("\n")
        f.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        f.write("root_directory = os.path.abspath(\"{}/../..\".format(fpath))\n")
        f.write("if root_directory not in sys.path:\n")
        f.write("    sys.path.insert(0, root_directory)\n")
        f.write("from nodes.routers.router import Router\n\n")
        f.write("class {}(Router):\n".format(camel_code(name)))
        f.write("    def __init__(self, node):\n")
        f.write("        super().__init__(node)\n")
        f.write("        self.shell_prompts = None\n")
        f.write("        self.pnode = node.get_pnode()\n\n")
        f.write("    # Please revise the following functions if it is different\n")
        f.write("    # from the default way\n\n")
        f.write("    def preparation(self):\n")
        f.write("        return super().prepare_image_files()\n\n")
        f.write("    def initialization(self):\n")
        f.write("        return super().initialization()\n\n")
        f.write("    def network_setting(self):\n")
        f.write("        return super().network_setting()\n\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, metavar="<device model name>", help="Device model name", type=str)
    parser.add_argument("-l", "--log", metavar="<log level=DEBUG/INFO/WARNING/ERROR>", help="Log level (DEBUG/INFO/WARNING/ERROR)", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    name = args.name

    fname = "{}/nodes/routers/{}.py".format(root_directory, name)

    if os.path.exists(fname):
        logging.error("The same name of the  exists. Please insert another name for the device")
        sys.exit(1)

    generate_template(name)

if __name__ == "__main__":
    main()
