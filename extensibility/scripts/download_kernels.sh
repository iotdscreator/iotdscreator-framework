#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Illegal number of parameters"
  echo "Usage: ./download_kernels.sh [target directory]"
  exit 0
fi

ODIR=`realpath ${1}`

# Download a kernel for mipsel 2.6
wget https://people.debian.org/~aurel32/qemu/mipsel/vmlinux-2.6.32-5-4kc-malta -O ${ODIR}/vmlinux-mipsel.2.6.32-malta

# Download a kernel for mipseb 2.6
wget https://people.debian.org/~aurel32/qemu/mips/vmlinux-2.6.32-5-4kc-malta -O ${ODIR}/vmlinux-mipseb.2.6.32-malta

# Copy kernel images to the target directory
cp -rf ${PWD}/kernels/* ${ODIR}
