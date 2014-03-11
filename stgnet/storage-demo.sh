#!/bin/bash
# Created on March 5, 2014
# Author: miminar
#
# Usage:
#   storage-demo.sh [(-m|--meta-command)] [<host>]
#
# Where:
#   <host> is a remote host to connect to. It can be specified also with
#	   HOST environment variable. It needs to contain credentials as
#          as well. Example: user:password@hostname.example.com

# Handle command line arguments.
if [[ "$1" =~ ^(-m|--meta-command)$ ]]; then
    USE_LMISHELL=0; shift
fi
. base.sh

set -x      # echo commands

# Following devices are available on remote host
# /dev/vda     MS-DOS partition table
# ├─/dev/vda1  ext3
# ├─/dev/vda2  swap
# └─/dev/vda3  ext4
# /dev/vdb     Unknown
# /dev/vdc     Unknown
# /dev/vdd     Unknown
# /dev/vde     Unknown

# *****************************************************************************
title "Inspecting storage."
# *****************************************************************************
# Let's check out, what informations can we get about /dev/vda
lmi -h $URI storage show vda

# Command operates on partitions as well:
lmi -h $URI storage show vda1

# There are various ways of specifying device. It's all described in
# the help of storage command:
#   lmi help storage
#
# There you can find:
#
#    * DeviceID of appropriate CIM_StorageExtent object. This is
#      internal OpenLMI ID of the device and it should be stable
#      across system reboots.
#
#    * Device name directly in /dev directory, such as '/dev/sda'.
#      This device name is available as Name property of
#      CIM_StorageExtent object.
#
#    * Name of MD RAID or logical volume. This method cannot be used
#      when the name is not unique, for example when there are two
#      logical volumes with the same name, allocated from different
#      volume groups. This name is available as ElementName
#      property of CIM_StorageExtent object.
#
# So the previous command can be written also like this:
#lmi -h $URI storage show /dev/vda

# To get a similar tree listing as in the first comment, use tree command:
lmi -H -h $URI storage tree
# '-H' option turns on human readable output which adds units to volume sizes.

{ set +x; } 2>/dev/null	    # suppress echo for next condition
if [[ ${USE_LMISHELL:-1} = 1 ]];
then    # Let's switch to LMIShell.

    # *************************************************************************
    title "Configuring RAID and LVM with LMIShell."
    # *************************************************************************

    # This scripts will:
    #  * create RAID 5 named "microraid" on vdb, vdc and vdd
    #  * create "lmivg" volume group on "microraid" and vde devices
    #  * create one logical volume "lmivol" in "lmivg" group
    #  * format it as xfs
    lmishell stg_make_lmivol.lmi $URI

else    # The same can be achieved with LMI Meta-command.

    # *************************************************************************
    title "Configuring RAID and LVM."
    # *************************************************************************

    # We have four unpartitioned disks we can freely use. Let's create RAID 5
    # called "microraid" on three of them:
    lmi -h $URI storage raid create --name microraid 5 vdb vdc vdd

    # Let's check the storage tree again:
    lmi -H -h $URI storage tree

    # Let's get more details about the raid:
    lmi -H -h $URI storage show microraid

    # *************************************************************************
    title "Creating volume group \"lmivg\"."
    # *************************************************************************
    # And make it into LVM physical volume together with the last physical
    # device. Let's name it "lmivg".
    lmi -h $URI storage vg create lmivg microraid vde

    # *************************************************************************
    title "Creating logical volume \"lmivol\"."
    # *************************************************************************
    # Empty volume group is not much useful:
    lmi -h $URI storage lv create lmivg lmivol 1G
    # This creates logical volumne "lmivol" in "lmivg" volume group !G large.
    # Storage sizes specification is quite flexible. Check the help of
    # `storage lv` command where you can find:
    #
    #    size        Size of the new logical volume, by default in bytes.
    #                'T', 'G', 'M' or 'K' suffix can be used to specify other
    #                units (TiB, GiB, MiB and KiB) - '1K' specifies 1 KiB
    #                (= 1024 bytes).
    #                The suffix is case insensitive, i.e. 1g = 1G = 1073741824
    #                bytes.
    #
    #                'E' suffix can be used to specify number of volume group
    #                extents, '100e' means 100 extents.

    # Let's see what we've just created
    lmi -H -h $URI storage vg list
    lmi -H -h $URI storage vg show lmivg
    lmi -H -h $URI storage lv show lmivol

    # *************************************************************************
    title "Formatting volume \"lmivol\" as xfs."
    # *************************************************************************
    # Still it's not usable without a proper file system:
    lmi -H -h $URI storage fs create --label lmixfs xfs lmivol
    # This will format our "lmivol" volume with xfs. That's just one out of
    # plenty supported. For complete list, check the output of:
    #lmi -h $URI storage fs list-supported

    # Now the tree view will be more interesting:
    lmi -H -h $URI storage tree

    # In complex setups you may be interested just in a subtree:
    lmi -H -h $URI storage tree microraid

fi

# *****************************************************************************
title "Mounting filesystem \"lmivol\"."
# *****************************************************************************
# Finally let's mount it. There are two steps involed. First is making the
# mount point (with a check for existence)
{ set +x; } 2>/dev/null	    # suppress echo
if ! lmi -h $URI file show /mnt/lmivol 2>/dev/null; then
    { set -x; } 2>/dev/null     # reenable echo
    lmi -h $URI file createdir /mnt/lmivol
fi
{ set -x; } 2>/dev/null     # reenable echo

# Second is the mount command:
lmi -h $URI storage mount create /dev/mapper/lmivg-lmivol /mnt/lmivol

# If you don't believe the exit code of the last command, you can always
# check it:
lmi -h $URI storage mount show /dev/mapper/lmivg-lmivol
