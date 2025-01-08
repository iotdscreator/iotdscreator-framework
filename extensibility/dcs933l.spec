# Hardware Resource
architecture: mipsel
cpu: 24KEc
smp: 1
memory: 64M
machine: malta
type: camera

# Software Stack
hardware security: false
url: http://files.dlink.com.au/products/DCS-933L/REV_A/Firmware/dcs933l_v1.14.11.bin
firmware: dcs933l_v1.14.11.bin
kernel: vmlinux.mipsel.2
filesystem: dcs933la1.raw

# Others
append: 'firmadyne.syscall=1 root=/dev/sda1 console=ttyS0 nandsim.parts=64,64,64,64,64,64,64,64,64,64 rw debug ignore_loglevel print-fatal-signals=1'
