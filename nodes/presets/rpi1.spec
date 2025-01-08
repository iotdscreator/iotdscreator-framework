# Hardware Resource
architecture: arm
cpu: arm1176
memory: 256m
machine: versatilepb
device type: general

# Software Stack
hardware security: false
dtb: versatile-pb.dtb
kernel: kernel-qemu-4.19.50-buster
operating system: debian
filesystem: raspbian.qcow2

# Network Interface
interface:
  - name: eth0
    type: ethernet

# Others
append: 'rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/sda2 rootwait panic=1'
#append: console=ttyAMA0,115200
