#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [Jean Claveau (https://github.com/jclaveau/ansible-vagrant-module)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/future-import-boilerplate.html
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/metaclass-boilerplate.html

MAN = '''
Usage: vagrant port [options] [name|id]

Options:

        --guest PORT                 Output the host port that maps to the given guest port
        --machine-readable           Display machine-readable output
    -h, --help                       Print this help
'''

DOCUMENTATION = '''
---
module: port
short_description: vagrant port for only one vm
description:
     - vagrant port for only one vm
version_added: "0.0.1"
author:
    - "Jean Claveau (@jclaveau)"
options:
  name:
    description:
      - name of the VM to retrieve ports of
    type: str
  guest:
    description:
      - Output the host port that maps to the given guest port
    type: int
    required: false
    default:
  vagrant_root:
    description:
      - the folder where vagrant files will be stored
    type: str
    default: .
requirements: ["vagrant"]
'''

EXAMPLES = '''
- name: Retrieve all ports of vm_name
  jclaveau.vagrant.port:
    name: vm_name
- name: Retrieve only the port corresponding to the given guest one
  jclaveau.vagrant.port:
    name: vm_name
    guest: 443
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
            name=dict(type='str'),
            guest=dict(type='int'),
        )
    )

    vagrant_root = module.params.get('vagrant_root')
    name = module.params.get('name')
    guest = module.params.get('guest')

    vgw = VagrantWrapper(
        module=module,
        root_path=vagrant_root,
    )

    (changed, duration, ports) = vgw.port(
        name=name,
        guest=guest,
    )

    module.exit_json(
        changed=changed,
        duration=duration,
        ports=ports,
        stdout_lines=list(vgw.stdout()),
        stderr_lines=list(vgw.stderr())
    )


main()
