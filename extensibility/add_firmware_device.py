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
from iutils.etc import load_yaml_file, camel_code

archs = {}
archs["MIPS64"] = "mips64"
archs["MIPS"] = "mips"
archs["ARM64"] = "arm64"
archs["ARM"] = "arm"
archs["Intel 80386"] = "intel"
archs["x86-64"] = "intel64"
archs["PowerPC"] = "ppc"
archs["unknown"] = "unknown"

endians = {}
endians["LSB"] = "el"
endians["MSB"] = "eb"

def get_architecture(fpath):
    logging.debug("fpath: {}".format(fpath))
    tar = tarfile.open(fpath, "r")
    infos = []
    fname = fpath.split("/")[-1]

    for info in tar.getmembers():
        if any([info.name.find(binary) != -1 for binary in ["/busybox", "/alphapd", "/boa", "/http", "/hydra", "/helia", "/webs"]]):
            infos.append(info)
        elif any([info.name.find(path) != -1 for path in ["/sbin/", "/bin/"]]):
            infos.append(info)

    arch = None
    endian = None

    for info in infos:
        tar.extract(info, path="/tmp/" + fname)
        path = "/tmp/{}/{}".format(fname, info.name)
        ftype = subprocess.check_output(["file", path]).decode()

        if not arch:
            for a in archs:
                if a in ftype:
                    arch = archs[a]
                    break

        if not endian:
            for e in endians:
                if e in ftype:
                    endian = endians[e]
                    break
    
    return arch + endian

def download_firmware(url, wdir):
    output = subprocess.check_output(["wget", url, "-P", wdir])
    if len(output.strip()) > 0:
        logging.error("Some error happend: {}".format(output))
        sys.exit(1)

    fname = url.split("/")[-1]
    fpath = "{}/{}".format(wdir, fname)
    fpath = os.path.abspath(fpath)

    if ".zip" in fpath:
        output = subprocess.check_output(["unzip", fpath, "-d", wdir])
        lst = output.decode().split("\n")
        for e in lst:
            if "inflating" in e and ".img" in e:
                fpath = e.split(":")[1].strip()

    logging.debug("fname: {}".format(fname))
    logging.debug("fpath: {}".format(fpath))

    return fpath

def extract(fpath):
    tmp = fpath.split("/")
    wdir = '/'.join(tmp[:-1])
    fname = tmp[-1]
    logging.debug("wdir: {}, fname: {}".format(wdir, fname))
    output = subprocess.check_output(["timeout", "--preserve-status", "--signal", "SIGINT", "60", "./extractor.py", fpath, wdir])
    logging.info("output in extract_filesystem(): {}".format(output))

    if len(output.strip()) != 0:
        logging.error("error happened: {}".format(output))
        return None

    lst = [f for f in os.listdir(wdir) if fname in f and ".kernel" in f]
    kname = lst[0]
    kpath = "{}/{}".format(wdir, kname)

    lst = [f for f in os.listdir(wdir) if fname in f and ".tar.gz" in f]
    rname = lst[0]
    rpath = "{}/{}".format(wdir, rname)

    return kpath, rpath

def make_image(name, arch, wdir):
    #output = subprocess.check_output(["sudo", "./scripts/makeImage.sh", str(iid), arch, fname])
    logging.debug("name: {}, arch: {}, wdir: {}".format(name, arch, wdir))
    sname = "{}/extensibility/scripts/makeImage.sh".format(root_directory)
    cmd = ["sudo", sname, name, arch, wdir]
    logging.debug("cmd: {}".format(" ".join(cmd)))
    output = subprocess.check_output(["sudo", sname, name, arch, wdir])
    logging.info("output in make_image(): {}".format(output))

def make_temporary_specification(pdir, name, arch, url, fname, cpu="none", memory="none", smp=1, dtype="none", machine=None):
    ofname = "{}/{}.spec".format(pdir, name)
    rname = "{}.raw".format(name)
    kname = "none"
    rf_disk = "none"
    smp = 1

    if arch == "armel":
        if cpu == "none":
            kname = "zImage.{}".format(arch)
        if machine == None:
            machine = "virt"
        rf_disk = "/dev/vda1"
    elif arch == "mipseb":
        if cpu == "none":
            kname = "vmlinux.{}.4".format(arch)
        if machine == None:
            machine = "malta"
        rf_disk = "/dev/sda1"
    elif arch == "mipsel":
        if cpu == "none":
            kname = "vmlinux.{}.4".format(arch)
        if machine == None:
            machine = "malta"
        rf_disk = "/dev/sda1"

    with open(ofname, "w") as of:
        of.write("# Hardware Resource\n")
        of.write("architecture: {}\n".format(arch))
        of.write("cpu: {}\n".format(cpu))
        of.write("smp: {}\n".format(smp))
        of.write("memory: {}\n".format(memory))
        of.write("machine: {}\n".format(machine))
        of.write("device type: {}\n\n".format(dtype))
        of.write("# Software Stack\n")
        of.write("hardware security: false\n")
        of.write("url: {}\n".format(url))
        of.write("firmware: {}\n".format(fname))
        of.write("kernel: {}\n".format(kname))
        of.write("filesystem: {}.raw\n\n".format(name))
        of.write("# Others\n")
        of.write("append: \'firmadyne.syscall=1 root={} console=ttyS0 nandsim.parts=64,64,64,64,64,64,64,64,64,64 rw debug ignore_loglevel print-fatal-signals=1\'\n".format(rf_disk))

    return ofname

def generate_device(name, arch, wdir, url, fname):
    fname = "{}/nodes/devices/{}.py".format(root_directory, name)

    with open(fname, "w") as f:
        f.write("import os, sys, logging\n")
        f.write("import pathlib, subprocess\n")
        f.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        f.write("root_directory = os.path.abspath(\"{}/../..\".format((fpath))\n")
        f.write("from devices.device import Device, DeviceShell\n\n")
        f.write("class {}(Device):\n".format(camel_code(name)))
        f.write("    def __init__(self, name, preset=None, shell_prompts=None, **params):\n")
        f.write("        self.preset = params.get(\"preset\", {})\n")
        f.write("        self.config = params.get(\"config\", {})\n")
        f.write("        self.net = params.get(\"net\", None)\n")
        f.write("        self.params.setdefault(\"net\", net)\n")
        f.write("        self.shell_prompts = shell_prompts\n")
        f.write("        super().__init__(name, preset=preset, shell_prompts=shell_prompts, **params)\n\n")
        f.write("    def prepare_dtb(self):\n")
        f.write("        return super().prepare_dtb()\n\n")
        f.write("    def prepare_kernel(self):\n")
        f.write("        return super().prepare_kernel()\n\n")
        f.write("    def prepare_filesystem(self):\n")
        f.write("        return super().prepare_filesystem()\n\n")
        f.write("    def prepare_firmware(self):\n")
        f.write("        wdir = self.config.get(\"working_directory\", \"{}/scratch\").format(root_directory)\n")
        f.write("        cmd = [\"wget\", {}, \"-O\", \"{}/{}\"]\n".format(url, wdir, fname))
        f.write("        output = subprocess.check_output(cmd)\n")

    # TODO: Need to complete the above auto-generation code

def generate_router():
    pass

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", metavar="<model name>", help="Model name", type=str, required=True)
    parser.add_argument("-t", "--type", metavar="<model name>", help="Model type", type=str, choices=["device", "router", "all"], required=True)
    parser.add_argument("-d", "--dtype", metavar="<device name>", help="Device type", type=str, required=True)
    parser.add_argument("-c", "--cpu", metavar="<cpu freq>", help="CPU frequency", type=str, default="none")
    parser.add_argument("-m", "--memory", metavar="<memory size>", help="Memory size", type=str, default="none")
    parser.add_argument("-s", "--smp", metavar="<smp>", help="SMP", type=int, default=1)
    parser.add_argument("-v", "--version", metavar="<version>", help="Version", type=str, default="v1.0")
    parser.add_argument("-u", "--url", metavar="<firmware url>", help="Firmware URL", type=str, required=True)
    parser.add_argument("-p", "--preset-dir", metavar="<preset directory>", help="Preset directory", type=str, default="{}/nodes/presets".format(root_directory))
    parser.add_argument("-i", "--image-dir", metavar="<image directory>", help="Image directory", type=str, default=".")
    parser.add_argument("-w", "--work-dir", metavar="<working directory>", help="Working directory", type=str, default="scratch")
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    if os.geteuid() != 0:
        logging.error("You should run this script with the root privilege.")
        sys.exit(0)

    args = command_line_args()
    logging.basicConfig(level=args.log)
    mtype = args.type
    
    wdir = os.path.abspath(args.work_dir)
    if os.path.exists(wdir):
        shutil.rmtree(wdir)
        os.mkdir(wdir)

    idir = os.path.abspath(args.image_dir)
    if not os.path.exists(idir):
        os.mkdir(idir)
    kdir = "{}/kernels".format(idir)
    if not os.path.exists(kdir):
        os.makedirs(kdir)
        cmd = ["scripts/download_kernels.sh", kdir]
        logging.debug("cmd: {}".format(' '.join(cmd)))
        output = subprocess.check_output(cmd)

    rdir = "{}/rootfs".format(idir)
    if not os.path.exists(rdir):
        os.makedirs(rdir)
    fdir = "{}/firmwares".format(idir)
    if not os.path.exists(fdir):
        os.makedirs(fdir)

    url = args.url
    if "?" in url:
        url = url.split("?")[0]

    name = args.name
    fpath = download_firmware(url, wdir)
    logging.info("fpath: {}".format(fpath))
    fname = fpath.split("/")[-1]
    logging.info("fname: {}".format(fname))
    kpath, rpath = extract(fpath)
    path = "{}/{}.kernel".format(wdir, name)
    os.rename(kpath, path)
    kpath = path
    path = "{}/{}.tar.gz".format(wdir, name)
    os.rename(rpath, path)
    rpath = path
    logging.info("kpath: {}, rpath: {}".format(kpath, rpath))
    
    arch = get_architecture(rpath)
    logging.info("architecture: {}".format(arch))

    make_image(name, arch, wdir)
    rfspath = "{}/{}.raw".format(wdir, name)
    path = "{}/rootfs/{}.raw".format(idir, name)
    os.rename(rfspath, path)

    path = "{}/firmwares/{}".format(idir, fname)
    os.rename(fpath, path)

    tname = make_temporary_specification(args.preset_dir, args.name, arch, args.url, fname, args.cpu, args.memory, args.smp, args.dtype)
    logging.info("Specification generated for {} is {}".format(name, tname))

    """
    if mtype == "device":
        generate_device()
    elif mtype == "router":
        generate_router()
    else:
        generate_device()
        generate_router()
    """
    shutil.rmtree(wdir)

if __name__ == "__main__":
    main()
