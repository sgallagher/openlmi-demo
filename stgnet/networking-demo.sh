#!/bin/bash
# Created on March 5, 2014
# Author: miminar

# Usage:
#   networking-demo.sh [<host>]
#
# Where:
#   <host> is a remote host to connect to. It can be specified also with
#	   HOST environment variable. It needs to contain credentials as
#          as well. Example: user:password@hostname.example.com
#
# This demo expects two inactive interfaces eth1 and eth2 to be available
# on remote host. It will bind them together into signle bonding interface
# bond0. Then it will run some data through it and again after one slave
# device is deactivated.

. base.sh

BOND='LMI Bond'
# Static address to assign to created bond interface.
BONDIP=${BONDIP:-192.168.122.80}
# Name of bond interface assigned by provider.
BONDIFACE=bond0

devs=`lmi -h $URI net device list | sed -n 's/^\(eth[1-2]\).*/\1/p'`
if [[ `echo "$devs" | wc -w` -lt 2 ]]; then
    echo "Expected eth1 and eth2 to be available." >&2
    exit 1
fi

set -x      #echo commands

# *****************************************************************************
title "Setting up bond."
# *****************************************************************************
# We've got eth0 interface we use for management. Then there are two inactive
# interfaces eth1 and eth2.
lmi -h $URI net device list

# Let's bind them together. Interfaces are configured with assignment of some
# setting to them. Setting tells Network Manger how to configure particular
# interface. There are various type of settings available for IPv4 and IPv6
# address types. For details consult:
#lmi help net setting
# Next line creates a bonding setting with statically assigned IPv4 address.
lmi -h $URI net setting create "$BOND" eth1 --bonding --ipv4 static
# In consequent commands we will reference it with its name (LMI Bond). It
# needs at least one slave device which in this case is eth1. This command
# causes 1 master bonding setting and 1 slave bonding setting for eth1 to be
# created.

# Having just one slave device for bonding interface is meaningless. Let's add
# one more. It creates another slave bonding setting for eth2.
lmi -h $URI net enslave "$BOND" eth2

# Since we've chosen static address for Master setting but haven't specified any yet,
# some random was selected for us. Let's change it to one we really want.
lmi -h $URI net address replace "$BOND" ${BONDIP} 24

# Creation of setting does not change current setup of interfaces. Settings are
# stored in persistent storage, waiting for their activation. Following command
# makes master bonding setting active together with all its dependent slave
# settings. It also creates new interface (bond0).
lmi -h $URI net activate "$BOND"

# *****************************************************************************
title "Inspecting configuration."
# *****************************************************************************
# This prents us nice overview:
lmi -h $URI net device list
# Looks like bond0 is really there.

# Now let's take a look on what we've done. Master bond setting looks like
# this:
lmi -h $URI net setting show "$BOND"

# We may use following to inspect our new virtual interface (or any other).
lmi -h $URI net device show $BONDIFACE

# *****************************************************************************
title "Testing connection."
# *****************************************************************************
# To be sure our setup really works, let's run a trivial test. This will launch
# python module that will spawn http server serving files on port 8080.
expect -f spawn_file_serving_service.exp root $PASS $HOST / &

{ 
    set +x;
    sleep 1;                # Wait for service to start.
    # Stop the file serving service before exit.
    trap "{ set +x; kill %1; } 2>/dev/null" EXIT;
    set -x;
} 2>/dev/null

# GET a file /etc/system-release and print its contents.
curl -m 5 -G $BONDIP:8080/etc/system-release
# Notice we're useing bond's static address we've chosen for interfacing with
# our server. Above command should produce one line with a name of
# distribution.

# Shutdown one of bond's interfaces. One reason for using bonding interfaces is
# its ability to operate when one of its slaves is down. Shutting down an
# interface is simply making the currently active setting an inactive. Let's
# shutdown eth2.
lmi -h $URI net deactivate "$BOND Slave 2" eth2
lmi -h $URI net device list

{ set +x; sleep 1; set -x; } 2>/dev/null # let the change settle down

# GET the same file again. Bond has still one interface active - it should
# work.
curl -m 5 -G $BONDIP:8080/etc/system-release

# Now shutdown the other interface.
lmi -h $URI net deactivate "$BOND Slave 1" eth1
lmi -h $URI net device list

# GET the same file again. This will timeout after 5 seconds.
curl -m 5 -G $BONDIP:8080/etc/system-release || true
# Bond simply can not work with all of its slaves down.

# Reenable one interface and try again.
lmi -h $URI net activate "$BOND Slave 1" eth1
lmi -h $URI net device list
lmi -h $URI net device show $BONDIFACE

curl -m 5 -G $BONDIP:8080/etc/system-release
