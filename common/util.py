from nodes.devices.rpi3 import Rpi3
from nodes.routers.rpi3router import Rpi3router
from nodes.interfaces.dummy_intf import DummyIntf
from nodes.interfaces.ethernet_intf import EthernetIntf
from nodes.interfaces.wifi_intf import WifiIntf
from applications.log4j import Log4j
from applications.mqtt_broker import MqttBroker
from applications.flooding import Flooding
from applications.temperature import Temperature
from applications.cve_2021_44228_http_server import Cve202144228HttpServer
from applications.airconditioner import Airconditioner
from applications.nmap import Nmap
from applications.openssh_server import OpensshServer
from applications.iot_hub import IotHub
from applications.cve_2021_44228_ldap_server import Cve202144228LdapServer
from applications.host_info_reporter import HostInfoReporter
from applications.ldap_server import LdapServer
from applications.wget import Wget
from applications.malware_server import MalwareServer
from applications.ping import Ping
from applications.java8 import Java8
from applications.maven import Maven
from applications.log4j_web_server import Log4jWebServer
from applications.cve_2021_44228_vulnerable_client import Cve202144228VulnerableClient
from applications.http_simple_get_request import HttpSimpleGetRequest

device_classes = {}
device_classes["rpi3"] = Rpi3

router_classes = {}
router_classes["rpi3router"] = Rpi3router

interface_classes = {}
interface_classes["dummy_intf"] = DummyIntf
interface_classes["ethernet_intf"] = EthernetIntf
interface_classes["wifi_intf"] = WifiIntf

application_classes = {}
application_classes["log4j"] = Log4j
application_classes["mqtt_broker"] = MqttBroker
application_classes["flooding"] = Flooding
application_classes["temperature"] = Temperature
application_classes["cve_2021_44228_http_server"] = Cve202144228HttpServer
application_classes["airconditioner"] = Airconditioner
application_classes["nmap"] = Nmap
application_classes["openssh_server"] = OpensshServer
application_classes["iot_hub"] = IotHub
application_classes["cve_2021_44228_ldap_server"] = Cve202144228LdapServer
application_classes["host_info_reporter"] = HostInfoReporter
application_classes["ldap_server"] = LdapServer
application_classes["wget"] = Wget
application_classes["malware_server"] = MalwareServer
application_classes["ping"] = Ping
application_classes["java8"] = Java8
application_classes["maven"] = Maven
application_classes["log4j_web_server"] = Log4jWebServer
application_classes["cve_2021_44228_vulnerable_client"] = Cve202144228VulnerableClient
application_classes["http_simple_get_request"] = HttpSimpleGetRequest

def get_device_class(name):
    ret = None
    if name in device_classes:
        ret = device_classes[name]
    return ret

def get_router_class(name):
    ret = None
    if name in router_classes:
        ret = router_classes[name]
    return ret

def get_interface_class(name):
    ret = None
    if name in interface_classes:
        ret = interface_classes[name]
    return ret

def get_application_class(name):
    ret = None
    if name in application_classes:
        ret = application_classes[name]
    return ret
