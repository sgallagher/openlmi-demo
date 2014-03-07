#!/bin/bash
# Created on March 5, 2014
# Author: miminar
#
# This script cleans up after running networking-demo.sh script.
# It needs to be run before any consecutive run of demo.

. base.sh

BOND='LMI Bond'

title +x "Cleaning up after networking demo"

devs=`lmi -h $URI net device list | sed -n 's/^\(eth[1-2]\).*/\1/p'`

for iface in $devs; do
    # First remove any bonding settings. Ignore slave ones for they will be
    # removed as a dependency.
    lmi -N -h $URI net setting list | \
            sed -n -e "/^$BOND\s\+Slave\s\+[0-9]\+/ d" -e "s/^\($BOND\).*/\1/p" |
            while IFS=  read setting;
    do
        printf 'Removing existing bond setting "%s".\n' "$setting"
        lmi -h $URI net setting delete "$setting"
    done
    # Second remove any other setting that my still be available for testing
    # interfaces. This ensures that devices are not active.
    for setting in `lmi -N -h $URI net device show $iface |
             sed -n 's/Available Setting\s*\(.*\)/\1/p'`; do
        printf 'Removing available setting "%s" from device "%s".\n' \
            "$setting" $iface
        # This will remove also active settings and deactivate interface if
        # active.
        lmi -h $URI net setting delete "$setting"
    done
done
