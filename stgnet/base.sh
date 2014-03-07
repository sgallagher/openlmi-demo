#!/bin/bash
# Created on March 5, 2014
# Author: miminar

URI=${URI:-pegasus:redhat@openlmi-stgnet-demo.example.com}

if [[ $# == 1 ]]; then URI="$1"; fi

if [[ "$URI" =~ (https?://)?([^:@]+):([^:@]+)@([^:]+)(:([0-9]+))? ]]; then
    SCHEMA=${BASH_REMATCH[1]}
    USER=${BASH_REMATCH[2]}
    PASS=${BASH_REMATCH[3]}
    HOST=${BASH_REMATCH[4]}
    PORT=${BASH_REMATCH[6]}
else
    echo "Failed to match URI \"$URI\"!" >&2
    exit 1
fi

PS4=$(printf '\\n%s+ $ %s' `tput setaf 6` `tput sgr0`)

# Terminate if something fails.
set -e
# Echo commands run.
set -x
