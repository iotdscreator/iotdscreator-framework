# Hardware Resource
architecture: arm
cpu: cortex-a7
smp: 4
memory: 1G
machine: raspi2
device type: general

# Software Stack
hardware security: false
dtb: bcm2709-rpi-2-b.dtb
kernel: kernel8.img
operating system: debian
filesystem: 2020-08-20-raspios-buster-armhf.img

# Network Interface
interface: 
  - name: eth0
    type: ethernet
  - name: wlan0
    type: wifi

# Others
append: 'rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/sda2 rootwait panic=1'
