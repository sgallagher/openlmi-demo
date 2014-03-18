#!/bin/lmishell
# -*- encoding: utf-8 -*-

"""
Demonstration script for OpenLMI Storage provider.
It expects 4 pristine disks /dev/vdb, /dev/vdc, /dev/vdd, /dev/vde
to be available on remote host. Raid, volume group and logical volume
formatted with xfs will be built on top like this:

    /dev/vdb ─┐
    /dev/vdc ─┼─ microraid ─┬─ lmivg ── lmivol ── lmixfs
    /dev/vdd ─┘             │
    /dev/vde ───────────────┘

Usage:
    stg_make_lmivol.lmi <host>

Where:
    <host>  Needs to have following format:
        <username>:<password>@<hostname>

        It can be preceded with schema and suffixed with port.
"""

RAIDNAME = "microraid"
VGNAME   = "lmivg"
LVNAME   = "lmivol"
FSNAME   = "lmixfs"

import docopt
import pywbem
import re
import sys

# PYTHONPATH does not contain parent directory
sys.path.insert(0, '../summit2014')

from lmidemo.util import democolor
from lmidemo.util.lmi_storage_view import LMIStorageView

#: Regular expression for <host> argument.
RE_HOST = re.compile(
    r'^(?P<schema>https?://)?(?P<user>[^:@]+):(?P<pass>[^:@]+)@(?P<host>.*)')

def log_title(title, *args, **kwargs):
    """
    Print colored title on terminal.
    All positional arguments are used to format *title* message.
    Optional keyword arguments are:

        * color (``int``)
        * bold (``boolean``)
    """
    color = kwargs.pop('color', democolor.XTERM_MAGENTA)
    bold = kwargs.pop('bold', True)
    print democolor.hilite("\n== %s ==" % (title % args),
            color, bold)

def parse_args(args=None):
    """
    Parse arguments.

    :param list args: Argument list to process. Defaults to ``sys.argv``.
    :returns: A pair of ``(broker_uri, credentials)``.
    :rtype: tuple
    """
    if args is None:
        args = sys.argv
    options = docopt.docopt(__doc__)
    match = RE_HOST.match(options['<host>'])
    if not match:
        raise docopt.DocoptExit('Invalid host given: "%s"!' % options['<host>'])
    schema = match.group('schema')
    if not schema:
        schema = ''

    return ( schema + match.group("host")
           , (match.group("user"), match.group("pass")))

def do_make_lmivol(ns):
    """
    Do the real work.

    :returns: An instance of LMI_LocalFileSystem representing xfs file
        system created.
    """
    # Connect to the storage configuration service
    storage_service = ns.LMI_StorageConfigurationService.first_instance(
                          Key="Name",
                          Value="LMI_StorageConfigurationService")

    # Connect to the storage filesystem service
    filesystem_service = ns.LMI_FileSystemConfigurationService.first_instance(
                             Key="Name",
                             Value="LMI_FileSystemConfigurationService")

    # Find the devices we want to add to MD RAID.
    raid_devs = [
        ns.CIM_StorageExtent.first_instance({"Name": "/dev/vdb"}),
        ns.CIM_StorageExtent.first_instance({"Name": "/dev/vdc"}),
        ns.CIM_StorageExtent.first_instance({"Name": "/dev/vdd"})
        # Persistent device id can be used as well:
        #ns.CIM_StorageExtent.first_instance({"DeviceId":
        #        "/dev/disk/by-uuid/e483c616-7218-4c4e-bc40-55f55342be7"})
    ]
    # Tree calls to broker above could be reduced to one:
    #raid_devices = [  ext for ext in ns.CIM_StorageExtent.instances()
    #               if fnmatch.fnmatch(ext.Name, '/dev/vd[bcd]')]
    # And if you want to be as fast as possible:
    #raid_devices = ns.wql('SELECT * from CIM_StorageExtent WHERE '
    #        + ' OR '.join('Name="/dev/vd"' + c for c in "bcd"))
    # Filtering is done by broker for us, we just recieve the result.

    log_title("Creating RAID 5 set named \"%s\" on unused drives", RAIDNAME)
    (ret, outparams, err) = storage_service.SyncCreateOrModifyMDRAID(
            ElementName=RAIDNAME,
            InExtents=raid_devs,
            Level=storage_service.CreateOrModifyMDRAID.LevelValues.RAID5)
    # *ret* is a return value of method. Thanks to ``use_exception(True)``
    # executed before, we may safely assume it ended successfully. Exception
    # would have been raised otherwise.

    # We are interested only in created RAID device object which is again
    # ``CIM_StorageExtent``.
    raid_dev = outparams["TheElement"]

    # Devices used to create volume group.
    vg_exts = [
        raid_dev,
        ns.CIM_StorageExtent.first_instance({"Name": "/dev/vde"})
    ]

    log_title("Creating volume group \"%s\" on top with additional drive",
            VGNAME)
    _, outparams, _ = storage_service.SyncCreateOrModifyVG(
            ElementName=VGNAME,
            InExtents=vg_exts)

    # Created volume group device is available in ``Pool`` output parameter.
    vg_dev = outparams["Pool"]

    log_title("Creating logical volume named \"%s\" on volume group \"%s\"",
            LVNAME, VGNAME)
    _, outparams, _ = storage_service.SyncCreateOrModifyLV(
            ElementName=LVNAME,
            InPool=vg_dev,          # target volume group
            Size=1024**3            # 1GB in size
    )

    lv_dev = outparams["TheElement"]

    log_title("Formatting \"%s\" logical volume as xfs", LVNAME)
    _, outparams, _ = filesystem_service.SyncLMI_CreateFileSystem(
            ElementName=FSNAME,     # optional file system label
            FileSystemType=filesystem_service.LMI_CreateFileSystem. \
                    FileSystemTypeValues.XFS,
            InExtents=[lv_dev])

    # Result is just an instance name of CIM_StorageExtent, which is
    # an identification object (or reference). It's usable as a parameter
    # to methods but it contains only key properties.
    file_system_name = outparams["TheElement"]
    # If we want to inspect the object in detail, we need to request
    # corresponding instance:
    file_system = file_system_name.to_instance()
    print "File system \"%s\" (%s) created." % (
            FSNAME, file_system.ElementName)

def main():
    """
    Parse arguments, make a connection and do the work.
    """
    uri, creds = parse_args()
    # Instruct the LMIShell to throw exceptions upon an error. Otherwise
    # they are suppressed and ``None`` is a result.
    use_exceptions(True)
    connection = connect(uri, *creds)
    # CIM Namespace object we operate upon (root/cimv2).
    ns = connection.root.cimv2
    try:
        do_make_lmivol(ns)

        # print the result
        print "Resulting storage setup:"
        storage_view = LMIStorageView(ns)
        storage_view.print_all()
    except pywbem.CIMError as err:
        print >>sys.stderr, err.args[1]
        sys.exit(1)

main()

# ex: ft=python et ts=4 sw=4
