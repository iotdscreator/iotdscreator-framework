# Hardware Resource
architecture: aarch64
cpu: cortex-a7
smp: 4
memory: 1G
machine: raspi3b
device type: general

# Software Stack
hardware security: false
dtb: bcm2710-rpi-3-b-plus.dtb
kernel: kernel8.img
operating system: debian
filesystem: 2020-08-20-raspios-buster-arm64.img

# Others
append: 'rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootdelay=1'
