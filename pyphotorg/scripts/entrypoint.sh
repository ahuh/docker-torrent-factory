#!/usr/bin/env bash

# Set user for impersonation
. /scripts/userSetup.sh

# Start python daemon
if [[ -n $1 ]]; then
	echo "Starting python daemon $1 ..."
	sudo -E -u ${RUN_AS} python -u $1
else
	echo "Starting default python daemon ..."
	sudo -E -u ${RUN_AS} python -u /work/daemon.py
fi
