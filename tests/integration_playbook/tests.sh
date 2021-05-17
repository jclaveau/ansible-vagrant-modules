#!/bin/bash
cd "$(dirname "$0")"

ansible-playbook vagrant_from_playbook_test.yaml
