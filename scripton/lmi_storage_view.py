'''
Created on May 23, 2013

@author: sgallagh
'''

import sys
import demoutils.democolor as democolor

class LMIStorageView:
    '''
    View storage configuration in a human-readable console
    '''

    def __init__(self, ns):
        self.ns = ns;
        pass

    def _recursive_display(self, level, extent):
        for _ in xrange(level):
            sys.stdout.write(u"    ")
        if level > 1:
            sys.stdout.write(u"\u21b3")
        # Print the name of the current extent
        sys.stdout.write(u"{0}".format(extent.Name))

        # Does this extent have a filesystem on it?
        filesystems = extent.associators(AssocClass="LMI_ResidesOnExtent",
                                       ResultClass="LMI_LocalFileSystem")
        for fs in filesystems:
            sys.stdout.write(u": {0}".format(
                democolor.hilite(fs.FileSystemType, democolor.XTERM_CYAN)))

        # Is this extent a SWAP partition?
        swaps = extent.associators(AssocClass="LMI_ResidesOnExtent",
                                   ResultClass="LMI_DataFormat")
        for swap in swaps:
            sys.stdout.write(u": {0}".format(
                democolor.hilite(swap.FormatTypeDescription,
                                 democolor.XTERM_YELLOW)))

        sys.stdout.write("\n")

        # Find all child extents
        dependent = extent.associators(AssocClass="CIM_BasedOn",
                                       ResultRole="Dependent")
        for dep in dependent:
            self._recursive_display(level + 1, dep)



    def print_all(self):
        '''
        Print the complete set of drives, partitions and arrays
        '''

        # Get the list of Primordial drives (physical block devices on
        # the system)
        drives = self.ns.wql("SELECT * FROM CIM_StorageExtent "
                             "WHERE Primordial=True")
        for drive in drives:
            level = 1;
            self._recursive_display(level, drive)
