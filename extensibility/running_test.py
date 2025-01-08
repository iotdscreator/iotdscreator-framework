import os, sys, argparse, logging
import subprocess
import tarfile
import shutil
import pathlib
import yaml
path = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(path))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from iutils.etc import load_yaml_file

def running_test(sname, kdir, rdir):
    config = load_yaml_file(sname)
    logging.debug("config: {}".format(config))
    binary = "qemu-system-{}".format(config["architecture"])
    cmd = [binary, "-cpu", config["cpu"], "-m", config["memory"], "-M", config["machine"], "-kernel", "{}/{}".format(kdir, config["kernel"]), "-drive", "if=ide,format=raw,file={}/{}".format(rdir, config["filesystem"]), "-append", "\'{}\'".format(config["append"]), "-serial", "stdio"]
    logging.debug("lst: {}".format(cmd))
    logging.debug("cmd: {}".format(' '.join(cmd)))
    os.system(' '.join(cmd))

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--spec", metavar="<spec name>", help="Specification name", type=str, required=True)
    parser.add_argument("-k", "--kdir", metavar="<kernel directory>", help="Kernel directory", type=str, required=True)
    parser.add_argument("-r", "--rdir", metavar="<rootfs directory>", help="Rootfs directory", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    if os.geteuid() != 0:
        logging.error("You should run this script with the root privilege.")
        sys.exit(0)

    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    running_test(args.spec, args.kdir, args.rdir)

if __name__ == "__main__":
    main()
