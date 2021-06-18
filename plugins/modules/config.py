#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [Jean Claveau (https://github.com/jclaveau/ansible-vagrant-modules)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This module is an integration and update of the excellent work of Bert Van Vreckem:
# https://github.com/bertvv/ansible-skeleton

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/future-import-boilerplate.html
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/metaclass-boilerplate.html

DOCUMENTATION = '''
---
module: config
short_description: Manage VMs in the Vagrantfile
description:
     - Controls the content of the vagrant-hosts.yml file wich will be parsed by the Vagrantfile
version_added: "0.0.1"
author:
    - "Jean Claveau (@jclaveau)"
options:
  state:
    description: Should the VMs be "present" or "absent" from the vagrant-hosts.yml file
    type: str
  name:
    description:
      - name to give to the VM
    type: str
    required: false
    default: null
  config:
    description:
      - The configuration for the VM
    type: dict
    required: false
    default: null
  vagrant_root:
    description:
      - the folder where vagrant files will be stored
    type: str
    default: .
requirements: ["deepdiff", "yaml"]
'''

EXAMPLES = '''
- name: Ensure a vm having the given config and name is present in vagrant-hosts.yml
  jclaveau.vagrant.config:
    state: present
    name:
      - "node1"
    config:
      box: boxomatic/debian-11
      cpus: 2
      shell:
        inline: hostname
      ansible:
        playbook: 'my_provisionning_playbook.yml'
      forwarded_ports:
      - guest: 80
        host: '8080'
      - guest: 443
        host: '8043'
      ip: 192.168.10.0
      mac: 00:50:56:3a:2d:1c
      memory: 2048
      netmask: 255.255.255.0
      synced_folders:
      - dest: /tmp/srv001
        src: /tmp
      - dest: /tmp/srv001/www/html
        options:
          :create: true
          :group: root
          :mount_options:
          - dmode=0755
          - fmode=0644
          :owner: root
        src: /var/www
- name: Remove a vm from vagrant-hosts.yml
  jclaveau.vagrant.config:
    state: absent
    name:
      - "node1"
- name: Dumps the content of vagrant-hosts.yml
  jclaveau.vagrant.config:
    name:
      - "node1"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.jclaveau.vagrant.plugins.module_utils.VagrantConfig import VagrantConfig


def main():

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str'),
            state=dict(),  # absent / present
            config=dict(type='dict'),
            vagrant_root=dict(default='.'),
        )
    )

    name = module.params.get('name')
    state = module.params.get('state')
    config_param = module.params.get('config')
    root = module.params.get('vagrant_root')

    config = VagrantConfig(
        module=module,
        root=root,  # optionnal
    )

    changed = False
    if state == 'absent':
        results = config.turn_absent_from_config(name=name, config_filter=config_param)
        changed = True
        module.exit_json(changed=changed, vms=results)

    elif state == 'present':  # replaces the existing config into the provided one
        results = config.turn_present_in_config(name=name, new_config=config_param)
        if len(results['needs']):
            changed = True
        # needs destroy / up or need reload
        module.exit_json(changed=changed, vms=results)

    elif state is None:
        results = config.dump(name=name, config_filter=config_param)
        module.exit_json(changed=False, vms=results)


main()
