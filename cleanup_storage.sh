#!/usr/bin/env bash

modprobe raid456; modprobe raid1; modprobe raid0

mdadm -S /dev/md/myRAID

parted /dev/vdb rm 1
parted /dev/vdb mklabel msdos -s

parted /dev/vdc rm 1
parted /dev/vdc mklabel msdos -s

parted /dev/vdd rm 1
parted /dev/vdd mklabel msdos -s

dd if=/dev/zero of=/dev/vdb
dd if=/dev/zero of=/dev/vdc
dd if=/dev/zero of=/dev/vdd

systemctl restart tog-pegasus.service
