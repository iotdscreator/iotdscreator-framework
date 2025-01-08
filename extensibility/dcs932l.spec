# Hardware Resource
architecture: mipsel
cpu: 24KEc
smp: 1
memory: 32M
machine: malta
type: camera

# Software Stack
hardware security: false
url: http://files.dlink.com.au/products/DCS-932L/REV_B/Firmware/dcs932lb1_v2.14.04.bin
firmware: dcs932lb1_v2.14.04.bin
kernel: vmlinux.mipsel.2
filesystem: dcs932l.raw

# Others
append: 'firmadyne.syscall=1 root=/dev/sda1 console=ttyS0 nandsim.parts=64,64,64,64,64,64,64,64,64,64 rw debug ignore_loglevel print-fatal-signals=1'
