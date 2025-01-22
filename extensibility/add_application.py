import os, sys, argparse, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import camel_code

def generate_template(name):
    fname = "{}/applications/{}.py".format(root_directory, name)

    with open(fname, "w") as f:
        f.write("import os, sys, logging\n")
        f.write("import pathlib\n")
        f.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        f.write("root_directory = os.path.abspath(\"{}/..\".format(fpath))\n")
        f.write("from applications.application import Application\n\n")
        f.write("class {}(Application):\n".format(camel_code(name)))
        f.write("    def __init__(self, app, **params):\n")
        f.write("        name = params.get(\"name\", app)\n")
        f.write("        if \"name\" in params:\n")
        f.write("            del params[\"name\"]\n")
        f.write("        super().__init__(app, name, **params)\n\n")
        f.write("    # Please revise the following functions if it is different\n")
        f.write("    # from the default way\n")
        f.write("    def check_application(self, arch=None, os=None):\n")
        f.write("        logging.debug(\"Check the application: {}\".format(self.app))\n")
        f.write("        cmds = []\n")
        f.write("        # if arch == \"aarch64\" and os == \"debian\":\n")
        f.write("        #     cmd = \"which nmap\"\n")
        f.write("        #     cmds.append(cmd)\n")
        f.write("        return cmds\n\n")
        f.write("    def prepare_application(self, arch=None, os=None):\n")
        f.write("        logging.debug(\"Prepare the application: {}\".format(self.app))\n")
        f.write("        cmds = []\n")
        f.write("        # if arch == \"aarch64\" and os == \"debian\":\n")
        f.write("        #     cmd = \"apt-get install nmap\"\n")
        f.write("        #     cmds.append(cmd)\n")
        f.write("        return cmds\n\n")
        f.write("    def run_application(self, arch=None, os=None, **params):\n")
        f.write("        logging.debug(\"Run the application: {}\".format(self.app))\n")
        f.write("        cmds = []\n")
        f.write("        # if arch == \"aarch64\" and os == \"debian\":\n")
        f.write("        #     cmd = \"nmap\"\n")
        f.write("        #     cmds.append(cmd)\n")
        f.write("        return cmds\n\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, metavar="<name of application>", help="Application name", type=str)
    parser.add_argument("-l", "--log", metavar="<log level=DEBUG/INFO/WARNING/ERROR>", help="Log level (DEBUG/INFO/WARNING/ERROR)", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    name = args.name

    fname = "{}/applications/{}.py".format(root_directory, name)

    if os.path.exists(fname):
        logging.error("The application with the same name exists. Please insert another name for the application")
        sys.exit(1)

    generate_template(name)

if __name__ == "__main__":
    main()
