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

function title() {
    # Print colorized title.
    # By default it turns on commands echo. If you want to prevent it,
    # prepend your message with +x argument.
    {
        if [[ "$1" == "+x" ]]; then
            shift;
            setx=0;
        fi
        printf "\n%s== %s ==%s\n" `tput setaf 6` "$1" `tput sgr0`;
        if [[ "${setx:-1}" == 1 ]]; then
            unset setx
        fi
    } 2>/dev/null
}

set -T

function pause() {
    read -n1 -s
}

# Terminate if something fails.
set -e
