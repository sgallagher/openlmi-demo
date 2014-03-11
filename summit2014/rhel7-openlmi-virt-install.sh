#!/bin/bash

virt-install \
    -n rhel7-openlmi \
    -r 1024 \
    --vcpus=1 \
    --os-variant=rhel7 \
    --accelerate \
    -v \
    -w network:default \
    -w network:default \
    -w network:default \
    -w network:default \
    --disk path=/var/lib/libvirt/images/rhel7-openlmi-0.img,size=4 \
    --disk path=/var/lib/libvirt/images/rhel7-openlmi-1.img,size=0.1 \
    --disk path=/var/lib/libvirt/images/rhel7-openlmi-2.img,size=0.1 \
    --disk path=/var/lib/libvirt/images/rhel7-openlmi-3.img,size=0.1 \
    --disk path=/var/lib/libvirt/images/rhel7-openlmi-4.img,size=0.1 \
    -l http://qafiler.bos.redhat.com/redhat/nightly/latest-RHEL-7/compose/Server/x86_64/os/ \
    --graphics none \
    -x "ks=https://raw.github.com/sgallagher/openlmi-demo/master/summit2014/rhel7-openlmi-virt-install.ks console=ttyS0"


