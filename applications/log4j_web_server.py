import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = "{}/..".format(fpath)
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from applications.application import Application

class Log4jWebServer(Application):
    def __init__(self, app, **params):
        name = params.get("name", app)
        if "name" in params:
            del params["name"]
        super().__init__(app, name, **params)

    # Please revise the following functions if it is different from the default way
    def check_application(self, arch=None, os=None):
        logging.debug("Check the application: {}".format(self.app))
        cmds = []

        if os in ["debian", "ubuntu"]:
            cmd = "must"
            cmds.append(cmd)

        return cmds

    def prepare_application(self, arch=None, os=None):
        logging.debug("Prepare the application: {}".format(self.app))
        cmds = []

        if os in ["debian", "ubuntu"]:
            cmd = "apt-get update --allow-releaseinfo-change"
            cmds.append(cmd)

            cmd = "apt-get install -y git"
            cmds.append(cmd)

            # Download the vulnerable web service
            cmd = "git clone https://github.com/kozmer/log4j-shell-poc.git"
            cmds.append(cmd)

            # Download the vulnerable JAVA for aarch64
            cmd = "wget https://mirrors.huaweicloud.com/java/jdk/8u151-b12/jdk-8u151-linux-arm64-vfp-hflt.tar.gz"
            cmds.append(cmd)

            cmd = "tar xvzf jdk-8u151-linux-arm64-vfp-hflt.tar.gz"
            cmds.append(cmd)

            cmd = "export JAVA_HOME=/root/jdk1.8.0_151"
            cmds.append(cmd)

            cmd = "export PATH=$PATH:/root/jdk1.8.0_151/bin"
            cmds.append(cmd)

            # Download the tomcat 8.5.75
            cmd = "wget https://archive.apache.org/dist/tomcat/tomcat-8/v8.5.75/bin/apache-tomcat-8.5.75.tar.gz"
            cmds.append(cmd)

            cmd = "tar xvzf apache-tomcat-8.5.75.tar.gz"
            cmds.append(cmd)

            # Move the vulnerable webapp to the tomcat
            cmd = "rm -rf apache-tomcat-8.5.75/webapps/*"
            cmds.append(cmd)

            cmd = "cp log4j-shell-poc/target/log4shell-1.0-SNAPSHOT.war apache-tomcat-8.5.75/webapps/ROOT.war"
            cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []

        if os in ["debian", "ubuntu"]:
            cmd = "./apache-tomcat-8.5.75/bin/catalina.sh run &"
            cmds.append(cmd)

        return cmds
