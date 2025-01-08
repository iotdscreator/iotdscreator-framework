import os, sys, argparse, logging
import yaml
from iutils.etc import camel_code

def prepare_devices(dname):
    ddir = dname

    dnames = []
    devices = [f for f in os.listdir(ddir) if f.endswith(".py") and f != "device.py"]

    for f in devices:
        dnames.append(f.split(".")[0])

    return dnames

def prepare_routers(rname):
    rdir = rname

    rnames = []
    routers = [f for f in os.listdir(rdir) if f.endswith(".py") and f != "router.py"]

    for f in routers:
        rnames.append(f.split(".")[0])

    return rnames

def prepare_interfaces(iname):
    idir = iname

    inames = []
    interfaces = [f for f in os.listdir(idir) if f.endswith(".py") and f != "interface.py"]

    for f in interfaces:
        inames.append(f.split(".")[0])

    return inames

def prepare_applications(aname):
    adir = "{}".format(aname)

    anames = []
    aapplications = [f for f in os.listdir(adir) if f.endswith(".py") and f != "application.py"]
    
    for f in aapplications:
        anames.append(f.split(".")[0])

    return anames

def prepare_features(dname):
    pdir = "{}/packet".format(dname)
    fdir = "{}/flow".format(dname)
    hdir = "{}/host".format(dname)
    tdir = "{}/transition".format(dname)

    pnames = []
    fnames = []
    hnames = []
    tnames = []

    pfeatures = [f for f in os.listdir(pdir) if f.endswith(".py")]
    ffeatures = [f for f in os.listdir(fdir) if f.endswith(".py")]
    hfeatures = [f for f in os.listdir(hdir) if f.endswith(".py")]
    tfeatures = [f for f in os.listdir(tdir) if f.endswith(".py")]

    for f in pfeatures:
        pnames.append(f.split(".")[0])

    for f in ffeatures:
        fnames.append(f.split(".")[0])

    for f in hfeatures:
        hnames.append(f.split(".")[0])

    for f in tfeatures:
        tnames.append(f.split(".")[0])

    return pnames, fnames, hnames, tnames

def make_class_file(cfname, dname, dnames, rname, rnames, iname, inames, aname, anames):
    dname = dname.replace("/", ".")
    logging.debug("dname: {}".format(dname))
    rname = rname.replace("/", ".")
    logging.debug("rname: {}".format(rname))
    iname = iname.replace("/", ".")
    logging.debug("iname: {}".format(dname))
    aname = aname.replace("/", ".")
    logging.debug("aname: {}".format(aname))

    with open(cfname, "w") as of:
        for d in dnames:
            of.write("from {}.{} import {}\n".format(dname, d, camel_code(d)))

        for r in rnames:
            of.write("from {}.{} import {}\n".format(rname, r, camel_code(r)))

        for i in inames:
            of.write("from {}.{} import {}\n".format(iname, i, camel_code(i)))

        for a in anames:
            of.write("from {}.{} import {}\n".format(aname, a, camel_code(a)))

        of.write("\n")
        of.write("device_classes = {}\n")
        for d in dnames:
            of.write("device_classes[\"{}\"] = {}\n".format(d, camel_code(d)))

        of.write("\n")
        of.write("router_classes = {}\n")
        for r in rnames:
            of.write("router_classes[\"{}\"] = {}\n".format(r, camel_code(r)))

        of.write("\n")
        of.write("interface_classes = {}\n")
        for i in inames:
            of.write("interface_classes[\"{}\"] = {}\n".format(i , camel_code(i)))

        of.write("\n")
        of.write("application_classes = {}\n")
        for a in anames:
            of.write("application_classes[\"{}\"] = {}\n".format(a, camel_code(a)))

        of.write("\n")
        of.write("def get_device_class(name):\n")
        of.write("    ret = None\n")
        of.write("    if name in device_classes:\n")
        of.write("        ret = device_classes[name]\n")
        of.write("    return ret\n")

        of.write("\n")
        of.write("def get_router_class(name):\n")
        of.write("    ret = None\n")
        of.write("    if name in router_classes:\n")
        of.write("        ret = router_classes[name]\n")
        of.write("    return ret\n")

        of.write("\n")
        of.write("def get_interface_class(name):\n")
        of.write("    ret = None\n")
        of.write("    if name in interface_classes:\n")
        of.write("        ret = interface_classes[name]\n")
        of.write("    return ret\n")

        of.write("\n")
        of.write("def get_application_class(name):\n")
        of.write("    ret = None\n")
        of.write("    if name in application_classes:\n")
        of.write("        ret = application_classes[name]\n")
        of.write("    return ret\n")

def make_config(ofname, pnames, fnames, hnames, tnames):
    conf = {}
    modules = ["general", "scenario_verifier", "network_abstractor", "physical_node_mapper", "virtual_network_constructor", "application_installer", "attack_scenario_executor", "data_labeler", "feature_extractor"]

    for m in modules:
        conf[m] = {}
        conf[m]["name"] = m

    conf["general"]["name"] = "iotdscreator"
    conf["general"]["timeout"] = 600

    conf["scenario_verifier"]["preset_directory"] = "nodes/presets"
    conf["scenario_verifier"]["timeout"] = 600

    conf["virtual_network_constructor"]["host_info_manager"] = {}
    conf["virtual_network_constructor"]["host_info_manager"]["name"] = "default"
    conf["virtual_network_constructor"]["host_info_manager"]["port"] = 10200

    conf["application_installer"]["application_cache"] = {}
    conf["application_installer"]["application_cache"]["name"] = "default"
    conf["application_installer"]["application_cache"]["port"] = 10201
    conf["application_installer"]["application_cache"]["cache_directory"] = "~/iotdscreator-cache"

    conf["data_labeler"]["zitter"] = 0.5

    conf["feature_extractor"]["features"] = {}

    # packet features
    conf["feature_extractor"]["features"]["packet"] = {}
    for p in pnames:
        conf["feature_extractor"]["features"]["packet"][p] = True

    # flow features
    conf["feature_extractor"]["features"]["flow"] = {}
    for f in fnames:
        conf["feature_extractor"]["features"]["flow"][f] = True

    # host features
    conf["feature_extractor"]["features"]["host"] = {}
    for f in hnames:
        conf["feature_extractor"]["features"]["host"][f] = True

    # transition features
    conf["feature_extractor"]["features"]["transition"] = {}
    for f in tnames:
        conf["feature_extractor"]["features"]["transition"][f] = True

    # window_length and sliding_window_interval are in milliseconds
    conf["feature_extractor"]["network_window_manager"] = {}
    conf["feature_extractor"]["network_window_manager"]["name"] = "network_window_manager"
    conf["feature_extractor"]["network_window_manager"]["window_length"] = 1000
    conf["feature_extractor"]["network_window_manager"]["sliding_window"] = True
    conf["feature_extractor"]["network_window_manager"]["sliding_window_interval"] = 100

    # window_length and sliding_window_interval are in milliseconds
    conf["feature_extractor"]["host_window_manager"] = {}
    conf["feature_extractor"]["host_window_manager"]["name"] = "host_window_manager"
    conf["feature_extractor"]["host_window_manager"]["window_length"] = 10000
    conf["feature_extractor"]["host_window_manager"]["sliding_window"] = True
    conf["feature_extractor"]["host_window_manager"]["sliding_window_interval"] = 1000

    with open(ofname, "w") as of:
        yaml.dump(conf, of, sort_keys=False)

def make_initializer(pnames, fnames, hnames, tnames):
    with open("iutils/futils.py", "w") as of:
        of.write("import os, sys, logging\n")
        of.write("import pathlib\n")
        of.write("fpath = pathlib.Path(__file__).parent.resolve()\n")
        of.write("root_directory = os.path.abspath(\"{}/..\".format(fpath))\n")
        of.write("if root_directory not in sys.path:\n")
        of.write("    sys.path.insert(0, root_directory)\n")
        
        for f in pnames:
            of.write("from features.packet.{} import {}\n".format(f, camel_code(f)))

        for f in fnames:
            of.write("from features.flow.{} import {}\n".format(f, camel_code(f)))

        for f in hnames:
            of.write("from features.host.{} import {}\n".format(f, camel_code(f)))

        for f in tnames:
            of.write("from features.transition.{} import {}\n".format(f, camel_code(f)))

        of.write("\n")
        of.write("def init_packet_features(feature_extractor):\n")
        names = pnames
        if len(names) > 0:
            for f in names:
                of.write("    feature_extractor.add_feature({}(\"{}\"))\n".format(camel_code(f), f))
        else:
            of.write("    pass\n")

        of.write("\n")
        of.write("def init_flow_features(feature_extractor):\n")
        names = fnames
        if len(names) > 0:
            for f in names:
                of.write("    feature_extractor.add_feature({}(\"{}\"))\n".format(camel_code(f), f))
        else:
            of.write("    pass\n")

        of.write("\n")
        of.write("def init_host_features(feature_extractor):\n")
        names = hnames
        if len(names) > 0:
            for f in names:
                of.write("    feature_extractor.add_feature({}(\"{}\"))\n".format(camel_code(f), f))
        else:
            of.write("    pass\n")

        of.write("\n")
        of.write("def init_transition_features(feature_extractor):\n")
        names = tnames
        if len(names) > 0:
            for f in names:
                of.write("    feature_extractor.add_feature({}(\"{}\"))\n".format(camel_code(f), f))
        else:
            of.write("    pass\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--applications", help="Application directory", type=str, default="applications")
    parser.add_argument("-d", "--devices", help="Device directory", type=str, default="nodes/devices")
    parser.add_argument("-r", "--routers", help="Router directory", type=str, default="nodes/routers")
    parser.add_argument("-f", "--features", help="Feature directory", type=str, default="features")
    parser.add_argument("-i", "--interfaces", help="Interface directory", type=str, default="nodes/interfaces")
    parser.add_argument("-o", "--output", help="Output filename", type=str, default="config.yaml")
    parser.add_argument("-u", "--util-filename", help="Util filename", type=str, default="common/util.py")
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", default="INFO", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()

    if not os.path.exists(args.features):
        print ("Invalid feature directory. Please insert the correct feature directory")
        sys.exit(1)

    logging.basicConfig(level=args.log)
    dnames = prepare_devices(args.devices)
    logging.debug("dnames: {}".format(dnames))
    rnames = prepare_routers(args.routers)
    logging.debug("rnames: {}".format(rnames))
    inames = prepare_interfaces(args.interfaces)
    logging.debug("inames: {}".format(inames))
    anames = prepare_applications(args.applications)
    logging.debug("anames: {}".format(anames))
    pnames, fnames, hnames, tnames = prepare_features(args.features)
    logging.debug("pnames: {}".format(pnames))
    logging.debug("fnames: {}".format(fnames))
    logging.debug("hnames: {}".format(hnames))
    logging.debug("tnames: {}".format(tnames))

    make_class_file(args.util_filename, args.devices, dnames, args.routers, rnames, args.interfaces, inames, args.applications, anames)
    make_config(args.output, pnames, fnames, hnames, tnames)
    make_initializer(pnames, fnames, hnames, tnames)

    logging.info("Please check the feature configure file: {}".format(args.output))

if __name__ == "__main__":
    main()
