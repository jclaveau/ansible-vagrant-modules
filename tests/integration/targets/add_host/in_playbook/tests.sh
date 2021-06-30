#!/bin/bash
cd "$(dirname "$0")"
set -e

COLLECTIONS_PATHS="$(pwd)/../../../../../"
# echo $COLLECTIONS_PATHS

# !!! This script MUST work on a MacOS environment for Github's Actions
# https://stackoverflow.com/a/41416710/2714285
# requires "brew install gnu-sed" on MacOS
if ! command -v "/usr/local/opt/gnu-sed/libexec/gnubin/gsed" &> /dev/null
then
    PATH="/usr/local/opt/gnu-sed/libexec/gnubin:$PATH"
fi


sed -i "s#^collections_paths=xxx#collections_paths=$COLLECTIONS_PATHS#g" ansible.cfg

cat ansible.cfg

ansible-playbook vagrant_from_playbook_test.yaml

sed -i "s#^collections_paths=$COLLECTIONS_PATHS#collections_paths=xxx#g" ansible.cfg
