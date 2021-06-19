#!/usr/bin/env bash

# integration tests
ansible-test integration --python 3.8 --coverage --color
ansible-test coverage xml --color

# integration tests which MUST be run from a playbook
./tests/integration_playbook/tests.sh

# sanity tests
ansible-test sanity --python 3.8