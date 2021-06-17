#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [Jean Claveau (https://github.com/jclaveau/ansible-vagrant-module)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/future-import-boilerplate.html
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/metaclass-boilerplate.html

DOCUMENTATION = '''
---
module: vagrant
short_description: create a local instance via vagrant
description:
     - creates VM instances via vagrant and optionally waits for it to be
       'running'. This module has a dependency on python-vagrant.
version_added: "0.0.1"
author:
    - "Jean Claveau (@jclaveau)"
options:
  state:
    description: Should the VMs be "up" or "halt"
    type: str
  names:
    description:
      - name to give an associated VM
    type: str
    required: false
    default: null
    aliases: []
  log:
    description:
      - Whether or not Vagrant's logs must be stored
    type: bool
    default: false
  root:
    description:
      - the folder where vagrant files will be stored
    type: str
    default: .
requirements: [""]
'''

EXAMPLES = '''
- name: Ensure vm having the given config are present in vagrant-hosts.yml
  jclaveau.vagrant.config:
    state: present
    names:
      - "node1"
      - "node2"
    config:
        box: debian/buster64
'''

import sys
import yaml
import os.path
import copy
from deepdiff import DeepDiff # import json
# from deepdiff.model import DiffLevel # import json
from pprint import pprint
# import ast
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib  # https://docs.ansible.com/ansible-core/devel/dev_guide/testing/sanity/import.html
# import traceback
# import fcntl
from io import StringIO
from ansible_collections.jclaveau.vagrant.plugins.module_utils.Vagrantfile import VAGRANTFILE_CONTENT

class VagrantConfig(object):

    def __init__(self, *args, **kwargs):
        '''
        Bridge between https://github.com/bertvv/ansible-skeleton and Ansible
        '''
        self.module = kwargs.setdefault('module', None)
        self.root = kwargs.setdefault('root', '.')
        self.parameters_requiring_recreate = ['box', 'box_path', 'provider', 'playbook', 'shell_always']
        # for libvirt https://github.com/vagrant-libvirt/vagrant-libvirt#reload-behavior

    def turn_present_in_config(self, name, new_config, new_groups):
        found = False
        needs = []

        # The content that will be written to the yaml file
        updated_config = []

        # load the yaml file or create it
        with open(self.root + "/vagrant-hosts.yml", 'a+') as stream:
            stream.seek(0)
            try:
                existing_config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.module.fail_json(msg=e)

            if existing_config is not None:
                for existing_host in existing_config:
                    if existing_host['name'] != name:
                        # we store already existing hosts to readd them later
                        updated_config.append(existing_host)
                    else:
                        # we check the diff between the current config and the new one to know
                        # if we need a reload or a detsroy
                        found = True
                        new_config['name'] = existing_host['name']
                        updated_config.append(new_config)

                        # Defining the needs due to the config changes
                        diff = DeepDiff(existing_host, new_config)

                        # if no diff, no need, no change
                        if diff == {}:
                            continue

                        # changes requiring recreate
                        # TODO would depend on the provider
                        # TODO handle parameters which are not at root
                        for parameter in self.parameters_requiring_recreate:
                            parameter_path = "root['" + parameter + "']"
                            if (('values_changed' in diff and parameter_path in diff['values_changed'].keys())
                                    or ('dictionary_item_added' in diff and parameter_path in diff['dictionary_item_added'])
                                    or ('dictionary_item_removed' in diff and parameter_path in diff['dictionary_item_removed'])
                                    ):
                                needs.append('destroy')
                                needs.append('up')

                        # TODO changes compared to the current status instead of the current config
                        # ports, ssh private_key from ssh-config, provider from status

                        if len(needs) == 0:
                            needs.append('reload')  # vagrant reload --provision? For now provisioning change requires recreate

            if not found:  # add the new vm to the config
                new_config['name'] = name
                needs.append('up')
                updated_config.append(new_config)

            stream.truncate(0)
            yaml.dump(updated_config, stream, allow_unicode=True, default_flow_style=False)
            self.ensure_vagrantfile_present(updated_config)

        with open(self.root + "/vagrant-groups.yml", 'a+') as stream:
            stream.seek(0)
            existing_groups = yaml.safe_load(stream)
            if existing_groups is None:
                existing_groups = []
            for group in new_groups:
                if group not in existing_groups:
                    existing_groups[group] = []
                if name not in existing_groups[group]:
                    existing_groups[group].append(name)
            stream.truncate(0)
            if len(existing_groups):
                yaml.dump(existing_groups, stream, allow_unicode=True, default_flow_style=False)

        out = {
            'needs': needs
        }
        # print(out)
        return out

    def turn_absent_from_config(self, name, config_filter, groups_filter):
        found = False
        needs = []

        # The content that will be written to the yaml file
        updated_config = []

        # load the yaml file or create it
        with open(self.root + "/vagrant-hosts.yml", 'a+') as stream:
            stream.seek(0)
            try:
                existing_config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.module.fail_json(msg=e)

            if existing_config is not None:
                for existing_host in existing_config:
                    if existing_host['name'] != name:
                        # we store non existing host to add them later
                        updated_config.append(existing_host)
                    else:
                        # TODO ignore_order=True
                        diff = DeepDiff(existing_host, config_filter)
                        if 'dictionary_item_added' not in diff and 'values_changed' not in diff:  # the config filter matches the existing host
                            found = True
                            needs.append('destroy')

            stream.truncate(0)
            yaml.dump(updated_config, stream, allow_unicode=True, default_flow_style=False)
            self.ensure_vagrantfile_present(updated_config)

        out = {
            'found': found,
            'needs': needs
        }
        # print(out)
        return out

    def ensure_vagrantfile_present(self, updated_config):
        if len(updated_config) > 0 and not os.path.exists(self.root + "/Vagrantfile"):  # allows a custom Vagrantfile
            with open(self.root + "/Vagrantfile", 'w') as stream:
                stream.write(VAGRANTFILE_CONTENT)

    def dump(self, name=None, config_filter=None):
        out = []
        with open(self.root + "/vagrant-hosts.yml", 'r') as stream:
            try:
                existing_config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.module.fail_json(msg=e)

            if existing_config is not None:
                for existing_host in existing_config:
                    if name is not None and name != existing_host['name']:
                        continue
                    if config_filter is not None:
                        diff = DeepDiff(existing_host, config_filter)
                        if 'values_changed' in diff or 'dictionary_item_added' in diff:
                            continue
                    out.append(existing_host)

        return out

# --------
# MAIN
# --------
def main():

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str'),
            state=dict(),  # absent / present
            config=dict(type='dict'),
            groups=dict(type='list', default=[]),
            root=dict(default='.'),
            log=dict(default=False, type='bool'),
            apply=dict(default=False, type='bool'),
        )
    )

    name = module.params.get('name')
    state = module.params.get('state')
    config_param = module.params.get('config')
    groups_param = module.params.get('groups')
    root = module.params.get('root')
    log = module.boolean(module.params.get('log'))

    root_path = os.path.abspath(root)
    # root_path = os.path.abspath(os.path.join(root, ".vagrant"))
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    config = VagrantConfig(
        module=module,
        root=root,  # optionnal
        log=log,  # optionnal
    )

    changed = False
    if state == 'absent':
        results = config.turn_absent_from_config(name=name, config_filter=config_param, groups_filter=groups_param)
        changed = True
        module.exit_json(changed=changed, vms=results)

    elif state == 'present':  # replaces the existing config into the provided one
        results = config.turn_present_in_config(name=name, new_config=config_param, new_groups=groups_param)
        if len(results['needs']):
            changed = True
        # needs destroy / up or need reload
        module.exit_json(changed=changed, vms=results)

    elif state is None:
        results = config.dump(name=name, config_filter=config_param)
        module.exit_json(changed=False, vms=results)

    module.exit_json(status="success")

main()
