import os, sys, logging, argparse
from subprocess import check_output
from iutils.etc import process_error
from iutils.etc import load_yaml_file
from iutils.etc import check_file_availability
from definitions.pnode import PNode

def clean(pnodes):
    ret = True

    request = {}
    request["opcode"] = "execute"
    for pnode in pnodes:
        # 1. Kill dnsmasq
        request["command"] = "killall dnsmasq"
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        # 2. Remove the internet interface
        request["command"] = "ip link del internet"
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        # 3. Find the main interface toward the Internet
        request["command"] = "which route"
        response = pnode.send_request(request)
        process_error(request, response)
        if len(response["stdout"].strip()) == 0 and len(response["stderr"].strip()) == 0:
            logging.debug("The iproute2 package is not installed")
            request["command"] = "apt-get install iproute2"
            response = pnode.send_request(request)
            process_error(request, response)

        request["command"] = "route -n"
        response = pnode.send_request(request)
        process_error(request, response)
        output = response["stdout"].split("\n")
        minterface = None
        for line in output:
            tokens = line.strip().split(" ")
            if tokens[0] == "0.0.0.0":
                minterface = tokens[-1]
                break
        logging.debug("minterface: {}".format(minterface))

        # 4. Remove the iptable rule set for the internet interface and the main interface
        request["command"] = "iptables -t nat -D POSTROUTING -o {} -j MASQUERADE".format(minterface)
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        request["command"] = "iptables -D FORWARD -i {} -o internet -m state --state RELATED,ESTABLISHED -j ACCEPT".format(minterface)
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        request["command"] = "iptables -D FORWARD -i internet -o {} -j ACCEPT".format(minterface)
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        # 5. Remove all links of the pattern foo-tapX
        request["command"] = "ip link show | egrep -o [-_.[:alnum:]]+-tap[[:digit:]]+"
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        taps = response["stdout"].strip().split("\n")
        for tap in taps:
            if len(tap.strip()) == 0:
                continue
            request["command"] = "ip link del {}".format(tap)
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

            request["command"] = "iptables -t filter -D FORWARD -i {} -o {} -j ACCEPT".format(tap, tap)
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

        # 6. Remove all links of the pattern foo-brX
        request["command"] = "ip link show | egrep -o [-_.[:alnum:]]+br[[:digit:]]+"
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

        brs = response["stdout"].strip().split("\n")
        for br in brs:
            if len(br.strip()) == 0:
                continue
            request["command"] = "ip link del {}".format(br)
            response = pnode.send_request(request)
            process_error(request, response, ignore=True)

        # 7. Remove all pipes used to communicate with qemu devices
        request["command"] = "rm /tmp/*-pipe.*"
        response = pnode.send_request(request)
        process_error(request, response, ignore=True)

    return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--physical-node-information", metavar="<physical node information file>", help="Physical node information file", type=str, required=True)
    parser.add_argument("-t", "--timeout", metavar="<timeout>", help="Timeout", type=int, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if not check_file_availability(args.physical_node_information):
        logging.error("The physical node information file ({}) does not exist.".format(args.physical_node_information))
        sys.exit(1)

    pni = load_yaml_file(args.physical_node_information)
    pnodes = []
    for node in pni["nodes"]:
        p = PNode(node, args.timeout)
        pnodes.append(p)
    clean(pnodes)

if __name__ == "__main__":
    main()
