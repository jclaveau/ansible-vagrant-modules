#!/usr/bin/env bash
set -e

./tests/integration/integration_config.sh

# integration tests
# --no-temp-workdir avoids Vagrant creation of vms in directories which are deleted after the run
ansible-test integration --python 3.8 --coverage --color --no-temp-workdir
ansible-test coverage xml --color

# integration tests which MUST be run from a playbook
./tests/integration/targets/add_host/in_playbook/tests.sh

# sanity tests
ansible-test sanity --python 3.8