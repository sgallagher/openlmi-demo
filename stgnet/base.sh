#!/bin/bash
# Created on March 5, 2014
# Author: miminar

HOST=${HOST:-pegasus:redhat@openlmi-stgnet-demo.example.com}

# Handle command line arguments.
if [[ "$1" =~ ^(-m|--meta-command)$ ]]; then
    USE_LMISHELL=0; shift
fi
if [[ $# == 1 ]]; then HOST="$1"; fi

PS4=$(printf '\\n%s+ $ %s' `tput setaf 6` `tput sgr0`)

# Terminate if something fails.
set -e
# Echo commands run.
set -x
