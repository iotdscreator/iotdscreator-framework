#!/bin/bash

if [ -n "$2" ]; then
    qemu-system-$1 -machine $2 -cpu help
else
    qemu-system-$1 -machine help
fi