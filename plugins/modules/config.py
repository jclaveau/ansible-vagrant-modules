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

VAGRANT_FILE = """
# One Vagrantfile to rule them all!
#
# This is a generic Vagrantfile that can be used without modification in
# a variety of situations. Hosts and their properties are specified in
# `vagrant-hosts.yml`. Provisioning is done by an Ansible playbook,
# `ansible/site.yml`.
#
# See https://github.com/bertvv/ansible-skeleton/ for details

require 'rbconfig'
require 'yaml'

# set default LC_ALL for all BOXES
ENV["LC_ALL"] = "en_US.UTF-8"

# Set your default base box here
DEFAULT_BASE_BOX = 'bento/centos-7.6'

# When set to `true`, Ansible will be forced to be run locally on the VM
# instead of from the host machine (provided Ansible is installed).
FORCE_LOCAL_RUN = false

#
# No changes needed below this point
#

VAGRANTFILE_API_VERSION = '2'
PROJECT_NAME = '/' + File.basename(Dir.getwd)

# set custom vagrant-hosts file
vagrant_hosts = ENV['VAGRANT_HOSTS'] ? ENV['VAGRANT_HOSTS'] : 'vagrant-hosts.yml'
hosts = YAML.load_file(File.join(__dir__, vagrant_hosts))

vagrant_groups = ENV['VAGRANT_GROUPS'] ? ENV['VAGRANT_GROUPS'] : 'vagrant-groups.yml'
groups = YAML.load_file(File.join(__dir__, vagrant_groups))

# {{{ Helper functions

def run_locally?
  windows_host? || FORCE_LOCAL_RUN
end

def windows_host?
  Vagrant::Util::Platform.windows?
end

# https://github.com/hashicorp/vagrant/issues/8878
class VagrantPlugins::ProviderVirtualBox::Action::Network
  def dhcp_server_matches_config?(dhcp_server,config)
    true
  end
end

# Set options for the network interface configuration. All values are
# optional, and can include:
# - ip (default = DHCP)
# - netmask (default value = 255.255.255.0
# - mac
# - auto_config (if false, Vagrant will not configure this network interface
# - intnet (if true, an internal network adapter will be created instead of a
#   host-only adapter)
def network_options(host)
  options = {}

  if host.key?('ip')
    options[:ip] = host['ip']
    options[:netmask] = host['netmask'] ||= '255.255.255.0'
  else
    options[:type] = 'dhcp'
  end

  options[:mac] = host['mac'].gsub(/[-:]/, '') if host.key?('mac')
  options[:auto_config] = host['auto_config'] if host.key?('auto_config')
  options[:virtualbox__intnet] = true if host.key?('intnet') && host['intnet']
  options
end

def custom_synced_folders(vm, host)
  return unless host.key?('synced_folders')
  folders = host['synced_folders']

  folders.each do |folder|
    vm.synced_folder folder['src'], folder['dest'], folder['options']
  end
end

# }}}


# Set options for shell provisioners to be run always. If you choose to include
# it you have to add a cmd variable with the command as data.
#
# Use case: start symfony dev-server
#
# example:
# shell_always:
#   - cmd: php /srv/google-dev/bin/console server:start 192.168.52.25:8080 --force
def shell_provisioners_always(vm, host)
  if host.has_key?('shell_always')
    scripts = host['shell_always']

    scripts.each do |script|
      vm.provision "shell", inline: script['cmd'], run: "always"
    end
  end
end

# }}}

# Adds forwarded ports to your Vagrant machine
#
# example:
#  forwarded_ports:
#    - guest: 88
#      host: 8080
def forwarded_ports(vm, host)
  if host.has_key?('forwarded_ports')
    ports = host['forwarded_ports']

    ports.each do |port|
      vm.network "forwarded_port", guest: port['guest'], host: port['host']
    end
  end
end

def provision_ansible(node, host, groups)
  return unless host.key?('playbook')
  ansible_mode = run_locally? ? 'ansible_local' : 'ansible'
  node.vm.provision ansible_mode do |ansible|
    ansible.compatibility_mode = '2.0'
    if ! groups.nil?
      ansible.groups = groups
    end
    ansible.playbook = host.key?('playbook') ?
        "ansible/#{host['playbook']}" :
        "ansible/site.yml"
    ansible.become = true
  end
end

# }}}

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  hosts.each do |host|
    config.vm.define host['name'] do |node|
      node.vm.box = host['box'] ||= DEFAULT_BASE_BOX
      node.vm.box_url = host['box_url'] if host.key? 'box_url'

      node.vm.hostname = host['name']
      node.vm.network :private_network, **network_options(host)
      custom_synced_folders(node.vm, host)
      shell_provisioners_always(node.vm, host)
      forwarded_ports(node.vm, host)

      node.vm.provider :virtualbox do |vb|
        vb.memory = host['memory'] if host.key? 'memory'
        vb.cpus = host['cpus'] if host.key? 'cpus'

        # Add VM to a VirtualBox group
        # WARNING: if the name of the current directory is the same as the
        # host name, this will fail.
        vb.customize ['modifyvm', :id, '--groups', PROJECT_NAME]
      end

      # Ansible provisioning
      provision_ansible(node, host, groups)
    end
  end
end

# -*- mode: ruby -*-
# vi: ft=ruby :
"""

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
                stream.write(VAGRANT_FILE)

    def dump(self, name=None):
        out = []
        with open(self.root + "/vagrant-hosts.yml", 'r') as stream:
            try:
                existing_config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.module.fail_json(msg=e)

            if existing_config is not None:
                for existing_host in existing_config:
                    if name is None or name == existing_host['name']:
                        out.append(existing_host)
        # print(out)
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
        results = config.dump(name=name)
        module.exit_json(changed=False, vms=results)

    module.exit_json(status="success")

main()
