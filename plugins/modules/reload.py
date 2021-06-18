#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [Jean Claveau (https://github.com/jclaveau/ansible-vagrant-module)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/future-import-boilerplate.html
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/metaclass-boilerplate.html

MAN = '''
Usage: vagrant reload [vm-name]

        --[no-]provision             Enable or disable provisioning
        --provision-with x,y,z       Enable only certain provisioners, by type or by name.
    -f, --force                      Force shut down (equivalent of pulling power)
    -h, --help                       Print this help
'''

DOCUMENTATION = '''
---
module: reload
short_description: vagrant reload of only one vm
description:
     - vagrant reload of only one vm
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
      - Enable only certain provisioners, by type or by name.
    type: list
    elements: str
  vagrant_root:
    description:
      - the folder where vagrant files will be stored
    type: str
    default: .
requirements: ["vagrant"]
'''

EXAMPLES = '''
- name: Relaod VM instance
  jclaveau.vagrant.reload:
    name: vm_name
- name: Relaod VM instance with provisionning enabled
  jclaveau.vagrant.reload:
    name: vm_name
    provision: true
- name: Relaod VM instance with provisionning for shell only
  jclaveau.vagrant.reload:
    name: vm_name
    provision_with: shell
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib  # https://docs.ansible.com/ansible-core/devel/dev_guide/testing/sanity/import.html

from ansible_collections.jclaveau.vagrant.plugins.module_utils.constants import DEFAULT_ROOT
from ansible_collections.jclaveau.vagrant.plugins.module_utils.VagrantWrapper import VagrantWrapper


# --------
# MAIN
# --------
def main():

    module = AnsibleModule(
        argument_spec=dict(
            vagrant_root=dict(default=DEFAULT_ROOT),
            name=dict(type='str', required=True),
            provision=dict(type='bool'),
            provision_with=dict(type='list', elements='str'),
        )
    )

    vagrant_root = module.params.get('vagrant_root')

    name = module.params.get('name')
    provision = module.params.get('provision')
    provision_with = module.params.get('provision_with')

    vgw = VagrantWrapper(
        module=module,
        root_path=vagrant_root,
    )

    (changed, duration, status_before, status_after) = vgw.reload(
        name=name,
        provision=provision,
        provision_with=provision_with,
        # force=force,  # not implemented in python-vagrant
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
