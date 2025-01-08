# Hardware Resource
architecture: mipsel
cpu: 24KEc
smp: 1
memory: 32M
machine: malta
type: camera

# Software Stack
hardware security: false
url: http://files.dlink.com.au/products/dcs-930l/REV_B/Firmware/dcs930lb1_v2.16.01.bin
firmware: dcs930lb1_v2.16.01.bin
kernel: vmlinux.mipsel.2
filesystem: dcs930lb1.raw

# Others
append: 'firmadyne.syscall=1 root=/dev/sda1 console=ttyS0 nandsim.parts=64,64,64,64,64,64,64,64,64,64 rw debug ignore_loglevel print-fatal-signals=1'
