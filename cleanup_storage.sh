#!/usr/bin/env bash

mdadm -S /dev/md/myRAID

parted /dev/vdb mklabel msdos -s
parted /dev/vdc mklabel msdos -s
parted /dev/vdd mklabel msdos -s

dd if=/dev/zero of=/dev/vdb
dd if=/dev/zero of=/dev/vdc
dd if=/dev/zero of=/dev/vdd

