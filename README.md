# IoTDSCreator

IoTDSCreator is a tool for the automatic generation of labeled datasets able to support a diversity of devices, connectivity technologies, and attacks. This framework provides a user with DC-API (Dataset Creation-Application Programming Interface), an API (in YAML keywords) by which a user can describe a target network and an attack scenario against it. 

The current version of IoTDSCreator can generate datasets with 193 features based on 26 types of IoT devices, 3 types of communication links, and 15 types of IoT applications. Through considering the diverse of IoT environments, IoTDScreator is highly scalable with respect to two dimensions, which are the improved entity scalability, and the resource scalability to configure a large-scale virtual network.

## 1. Install necessary packages
 - `sudo apt-get update`
 - `sudo apt-get install -y ninja-build libglib2.0-dev libpixman-1-dev flex bison meson python3-pip python3-magic binwalk net-tools`
 - `sudo pip3 install argparse sqlalchemy numpy matplotlib pandas keras threadpoolctl joblib SciPy scikit-learn datatable yellowbrick dpkt scapy pyyaml`

## 2. Install QEMU 8.0.0-rc2
 - `wget https://download.qemu.org/qemu-8.0.0-rc2.tar.xz`
 - `tar -xf qemu-8.0.0-rc2.tar.xz`
 - `cd qemu-8.0.0-rc2`
 - `./configure`
 - `make -j$(nproc) && sudo make install`

## 3. Run one agent
 - Open a terminal on your experimental machine.
 - Run an agent per each machine by `sudo python3 agent.py --config agent.yaml` (sudo is necessary)
 - The agent.yaml must specify the information about an open port including the IP address and the port number. Also, it should contain the path of the working directory and the timeout value.

## 4. Run IoTDSCreator
 - Running IoTDSCreator requires a scenario description, the information about the physical machines, and the configuration file.
 - A scenario description includes the information about the (victim) network, the attacks, and the dataset. Examples of scenario descriptions are under the directory "scenarios."
 - The physical machine information describes the information about the physical machines that an experimentor provides. Examples of the physical machine information are under the directory "examples."
 - Run IoTDSCreator by `python3 iotdscreator.py -s scenarios/nmap-flooding.scenario -p examples/one.pni` (sudo is NOT required).
