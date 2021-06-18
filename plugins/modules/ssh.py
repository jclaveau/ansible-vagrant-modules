#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [Jean Claveau (https://github.com/jclaveau/ansible-vagrant-module)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/future-import-boilerplate.html
# https://docs.ansible.com/ansible/2.10/dev_guide/testing/sanity/metaclass-boilerplate.html

MAN = '''
Usage: vagrant ssh [options] [name|id] [-- extra ssh args]

Options:

    -c, --command COMMAND            Execute an SSH command directly
    -p, --plain                      Plain mode, leaves authentication up to user
    -t, --[no-]tty                   Enables tty when executing an ssh command (defaults to true)
    -h, --help                       Print this help
'''

DOCUMENTATION = '''
---
module: ssh
short_description: vagrant ssh to a vm
description:
     - vagrant ssh to a vm
version_added: "0.0.1"
author:
    - "Jean Claveau (@jclaveau)"
options:
  name:
    description:
      - name of the VM to start
    type: str
    required: true
  command:
    description:
      - The shell command to run on the vm
    type: str
    required: true
  vagrant_root:
    description:
      - the folder where vagrant files will be stored
    type: str
    default: .
requirements: ["vagrant"]
'''

EXAMPLES = '''
- name: Displays the hostname of the vm as seen from itself
  jclaveau.vagrant.ssh:
    name: vm_name
    command: hostname
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
            command=dict(type='str', required=True),
        ),
    )

    vagrant_root = module.params.get('vagrant_root')
    name = module.params.get('name')
    command = module.params.get('command')

    vgw = VagrantWrapper(
        module=module,
        root_path=vagrant_root,
    )

    (changed, duration) = vgw.ssh(
        name=name,
        command=command,
        # extra_ssh_args I don't see the benefit compared to command
    )

    module.exit_json(
        changed=changed,
        duration=duration,
        stdout_lines=list(vgw.stdout()),
        stderr_lines=list(vgw.stderr())
    )


main()
