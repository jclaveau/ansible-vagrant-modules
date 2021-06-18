#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [Jean Claveau (https://github.com/jclaveau/ansible-vagrant-module)]
# Copyright: (c) 2017, [Tomas Kadlec (https://github.com/majidaldo/ansible-vagrant/commits?author=tomaskadlec)]
# Copyright: (c) 2015, [Majid alDosari (https://github.com/majidaldo/ansible-vagrant)]
# Copyright: (c) 2015, [caljess599 (https://github.com/caljess599/ansible-vagrant)]
# Copyright: (c) 2014, [Rob Parrot (https://github.com/robparrott/ansible-vagrant)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/future-import-boilerplate.html
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/metaclass-boilerplate.html

MAN = '''
Usage: vagrant up [options] [name|id]

Options:

        --[no-]provision             Enable or disable provisioning
        --provision-with x,y,z       Enable only certain provisioners, by type or by name.
        --[no-]destroy-on-error      Destroy machine if any fatal error happens (default to true)
        --[no-]parallel              Enable or disable parallelism if provider supports it
        --provider PROVIDER          Back the machine with a specific provider
        --[no-]install-provider      If possible, install the provider if it isn't installed
    -h, --help                       Print this help
'''

DOCUMENTATION = '''
---
module: up
short_description: vagrant up for Ansible
description:
     - vagrant up for Ansible
version_added: "0.0.1"
author:
    - "Jean Claveau (@jclaveau)"
options:
  name:
    description:
      - name of the VM to start
    type: str
    required: true
  provision:
    description:
      - Enable or disable provisioning
      - Force if true, disables if false and do it if not already provision if unspecified
    type: bool
  provision_with:
    description:
      - Enable only certain provisioners, by type or by name (shell and Ansible are supported; feel free to PR new ones).
    type: list
    elements: str
  provider:
    type: str
    description:
      - a provider to use instead of default virtualbox
  vagrant_root:
    description:
      - the folder where vagrant files will be stored
    type: str
    default: .
requirements: ["vagrant"]
'''


EXAMPLES = '''
- name: Spawn a new VM instance
  jclaveau.vagrant.up:
    names:
      - vm_name
- name: up with a specific provider
  jclaveau.vagrant.up:
  args:
    name: vm_name
    provider: docker
- name: up with forced provisioning
  jclaveau.vagrant.up:
  args:
    name: vm_name
    provision: true
- name: up with provisionning for shell only
  jclaveau.vagrant.up:
  args:
    name: vm_name
    provision_with: shell
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib  # https://docs.ansible.com/ansible-core/devel/dev_guide/testing/sanity/import.html
from ansible_collections.jclaveau.vagrant.plugins.module_utils.constants import DEFAULT_ROOT
from ansible_collections.jclaveau.vagrant.plugins.module_utils.VagrantWrapper import VagrantWrapper


def main():

    module = AnsibleModule(
        argument_spec=dict(
            vagrant_root=dict(default=DEFAULT_ROOT),
            name=dict(type='str', required=True),
            provider=dict(type='str'),
            provision=dict(type='bool'),
            provision_with=dict(type='list', elements='str'),
        )
    )

    vagrant_root = module.params.get('vagrant_root')
    name = module.params.get('name')
    provider = module.params.get('provider')
    provision = module.params.get('provision')
    provision_with = module.params.get('provision_with')

    vgw = VagrantWrapper(
        module=module,
        root_path=vagrant_root,
    )

    (changed, duration, status_before, status_after) = vgw.up(
        name=name,
        provider=provider,
        provision=provision,
        provision_with=provision_with,
        # parallel=parallel # Not supported by python-vagrant
        # destroy-on-error # Not supported by python-vagrant
        # install-provider # Not supported by python-vagrant
    )

    module.exit_json(
        changed=changed,
        duration=duration,
        status_before=status_before,
        status_after=status_after,
        stdout_lines=list(vgw.stdout()),
        stderr_lines=list(vgw.stderr())
    )


main()
