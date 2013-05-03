#!/usr/bin/env lmishell

'''
Created on Apr 8, 2013

@author: sgallagh
'''

import sys
import time
from scripton.lmi_sync_job import LMISyncJob

# Drives to work with
avail_drives = ["/dev/vdb", "/dev/vdc", "/dev/vdd"]

# Connect to the example VM
c = connect("openlmi-demo", "root", "redhat")

# Shorthand the cimv2 namespace
ns = c.root.cimv2

# Connect to the partitioning service
partitioning_service = ns.LMI_DiskPartitionConfigurationService.first_instance(
                           Key="Name",
                           Value="LMI_DiskPartitionConfigurationService")

# Connect to the storage configuration service
storage_service = ns.LMI_StorageConfigurationService.first_instance(
                      Key="Name",
                      Value="LMI_StorageConfigurationService")

# Connect to the storage filesystem service
filesystem_service = ns.LMI_FileSystemConfigurationService.first_instance(
                         Key="Name",
                         Value="LMI_FileSystemConfigurationService")

# Get the GPT partition type object
gpt_caps = ns.LMI_DiskPartitionConfigurationCapabilities.first_instance(
               Key="InstanceID",
               Value="LMI:LMI_DiskPartitionConfigurationCapabilities:GPT")

# Prep the first three drives
for drive in avail_drives:
    print "Processing drive {0}".format(drive)
    physical_device = ns.LMI_StorageExtent.first_instance(
                          Key="Name",
                          Value=drive)

    # Create a new GPT partition table on this disk
    print "Creating GPT partition table on {0}".format(physical_device.DeviceID)
    job = LMISyncJob(ns,
                     partitioning_service.SetPartitionStyle(
                                Extent=physical_device,
                                PartitionStyle=gpt_caps))
    (ret, outparams, err) = job.process()
    if ret != LMISyncJob.SUCCESS:
        print "Error creating partition table: {0}({1})".format(err, ret)
        sys.exit(1)
    
    # Create a single partition covering the whole disk
    print "Creating partition on {0}".format(physical_device.DeviceID)
    job = LMISyncJob(ns,
                     partitioning_service.LMI_CreateOrModifyPartition(
                                              extent=physical_device))
    (ret, outparams, err) = job.process()
    if (ret != LMISyncJob.SUCCESS):
        # Job did not complete successfully
        print "Error creating partition on {0}: {1}({2})".format(
               drive, err, ret)
        sys.exit(2)

# Find the devices we want to add to MD RAID
# (filtering one CIM_StorageExtent.instances()
# call would be faster, but this is easier to read)

vdb1 = ns.CIM_StorageExtent.first_instance(
        Key="Name", Value="/dev/vdb1")
vdc1 = ns.CIM_StorageExtent.first_instance(
        Key="Name", Value="/dev/vdc1")
vdd1 = ns.CIM_StorageExtent.first_instance(
        Key="Name", Value="/dev/vdd1")

# Create the RAID set
print "Creating raid set on {0}, {1}, {2}".format(vdb1.Name, vdc1.Name,
                                                  vdd1.Name)

job = LMISyncJob(ns,
                 storage_service.CreateOrModifyMDRAID(
                     ElementName = "myRAID",
                     InExtents = [vdb1.path, vdc1.path, vdd1.path],
                     Level=5))
(ret, outparams, err) = job.process()

if ret != LMISyncJob.SUCCESS:
    # Job did not complete successfully
    print "Error creating RAID set: {0}({1})".format(err, ret)
    sys.exit(2)

raid = ns.LMI_StorageExtent.first_instance(Key="Name", Value="/dev/md/myRAID")
print "Created RAID device {0} at level {1} of size {2} MB".format(
       raid.DeviceID, raid.Level,
       raid.BlockSize * raid.NumberOfBlocks / 1024 / 1024)


print "Creating EXT4 file system"
job = LMISyncJob(ns,
                 filesystem_service.LMI_CreateFileSystem(
                     FileSystemType = 32769, # 32769 = EXT4
                     InExtents= [raid.path]))
(ret, outparams, err) = job.process()
if (ret != LMISyncJob.SUCCESS):
    # Job did not complete successfully
    print "Error creating filesystem: {0}({1})".format(err, ret)
    sys.exit(2)
    
print "Filesystem created on {0}".format(raid.Name)