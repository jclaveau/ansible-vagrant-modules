#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [Jean Claveau (https://gist.github.com/jclaveau/af2271b9fdf05f7f1983f492af5592f8)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Example of buggy coverage file:
# !coverage.py: This is a private format, don't read it directly!{"arcs":{"/home/jean/dev/ansible_collections/jclaveau/vagrant/tests/integration/[{'started': 1, 'finished': 0, 'ansible_job_id': '627328642771.516092', 'results_file': '/home/jean/.ansible_async/627328642771.516092', 'changed': True, 'failed': False, 'item': {'name': 'srv001', 'state': 'not_created', 'provider': 'virtualbox'}, 'ansible_loop_var': 'item'}, {'started': 1, 'finished': 0, 'ansible_job_id': '602132986255.516119', 'results_file': '/home/jean/.ansible_async/602132986255.516119', 'changed': True, 'failed': False, 'item': {'name': 'srv003', 'state': 'not_created', 'provider': 'virtualbox'}, 'ansible_loop_var': 'item'}]":[[-1,1],[1,-1]],"/home/jean/dev/ansible_collections/jclaveau/vagrant/tests/integration/{'started': 1, 'finished': 0, 'ansible_job_id': '627328642771.516092', 'results_file': '/home/jean/.ansible_async/627328642771.516092', 'changed': True, 'failed': False, 'item': {'name': 'srv001', 'state': 'not_created', 'provider': 'virtualbox'}, 'ansible_loop_var': 'item'}":[[-1,1],[1,-1]],"/home/jean/dev/ansible_collections/jclaveau/vagrant/tests/integration/{'started': 1, 'finished': 0, 'ansible_job_id': '602132986255.516119', 'results_file': '/home/jean/.ansible_async/602132986255.516119', 'changed': True, 'failed': False, 'item': {'name': 'srv003', 'state': 'not_created', 'provider': 'virtualbox'}, 'ansible_loop_var': 'item'}":[[-1,1],[1,-1]]}}
# With escaped quoted strings
# !coverage.py: This is a private format, don't read it directly!{"arcs":{"/home/jean/dev/ansible_collections/jclaveau/vagrant/tests/integration/{'results': [{'changed': True, 'duration': 71.62376117706299, 'status_before': 'not_created', 'status_after': 'running', 'stdout_lines': [\"Bringing machine 'srv001' up with 'virtualbox' provider...\", \"==> srv001: Importing base box 'debian/buster64'...\", '', '\\x1b[KProgress: 30%', '\\x1b[KProgress: 40%', '\\x1b[KProgress: 70%', '\\x1b[KProgress: 80%', '\\x1b[KProgress: 90%', '\\x1b[K==> srv001: Matching MAC address for NAT networking...', \"==> srv001: Checking if box 'debian/buster64' version '10.20210409.1' is up to date...\", '==> srv001: Setting the name of the VM: integration_srv001_1624002971381_58925', '==> srv001: Clearing any previously set network interfaces...', '==> srv001: Preparing network interfaces based on configuration...', '    srv001: Adapter 1: nat', '    srv001: Adapter 2: hostonly', '==> srv001: Forwarding ports...', '    srv001: 22 (guest) => 2290 (host) (adapter 1)', '    srv001: 80 (guest) => 8080 (host) (adapter 1)', '    srv001: 443 (guest) => 8043 (host) (adapter 1)', \"==> srv001: Running 'pre-boot' VM customizations...\", '==> srv001: Booting VM...', '==> srv001: Waiting for machine to boot. This may take a few minutes...', '    srv001: SSH address: 127.0.0.1:2290', '    srv001: SSH username: vagrant', '    srv001: SSH auth method: private key', '    srv001: ', '    srv001: Vagrant insecure key detected. Vagrant will automatically replace', '    srv001: this with a newly generated keypair for better security.', '    srv001: ', '    srv001: Inserting generated public key within guest...', \"    srv001: Removing insecure key from the guest if it's present...\", '    srv001: Key inserted! Disconnecting and reconnecting using new SSH key...', '==> srv001: Machine booted and ready!', '==> srv001: Checking for guest additions in VM...', '    srv001: The guest additions on this VM do not match the installed version of', '    srv001: VirtualBox! In most cases this is fine, but in rare cases it can', '    srv001: prevent things such as shared folders from working properly. If you see', '    srv001: shared folder errors, please make sure the guest additions within the', '    srv001: virtual machine match the version of VirtualBox you have installed on', '    srv001: your host and reload your VM.', '    srv001: ', '    srv001: Guest Additions Version: 5.2.0 r68940', '    srv001: VirtualBox Version: 6.1', '==> srv001: Setting hostname...', '==> srv001: Configuring and enabling network interfaces...', '==> srv001: Installing rsync to the VM...', '==> srv001: Rsyncing folder: /home/jean/dev/ansible_collections/jclaveau/vagrant/tests/integration/ => /vagrant', '==> srv001: Running provisioner: shell...', '    srv001: Running: inline script', '    srv001: srv001', '', \"==> srv001: Machine 'srv001' has a post `vagrant up` message. This is a message\", '==> srv001: from the creator of the Vagrantfile, and not from Vagrant itself:', '==> srv001: ', '==> srv001: Vanilla Debian box. See https:/app.vagrantup.com/debian for help and bug reports'], 'stderr_lines': [], 'invocation': {'module_args': {'name': 'srv001', 'vagrant_root': '.', 'provider': None, 'provision': None, 'provision_with': None}}, 'finished': 1, 'ansible_job_id': '102460403381.516632', 'failed': False, 'attempts': 60, 'item': {'started': 1, 'finished': 0, 'ansible_job_id': '102460403381.516632', 'results_file': '/home/jean/.ansible_async/102460403381.516632', 'changed': True, 'failed': False, 'item': 'srv001', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'}, {'changed': True, 'duration': 48.87693905830383, 'status_before': 'not_created', 'status_after': 'running', 'stdout_lines': [\"Bringing machine 'srv002' up with 'virtualbox' provider...\", \"==> srv002: Importing base box 'debian/buster64'...\", '', '\\x1b[KProgress: 30%', '\\x1b[KProgress: 40%', '\\x1b[KProgress: 50%', '\\x1b[KProgress: 80%', '\\x1b[KProgress: 90%', '\\x1b[K==> srv002: Matching MAC address for NAT networking...', \"==> srv002: Checking if box 'debian/buster64' version '10.20210409.1' is up to date...\", '==> srv002: Setting the name of the VM: integration_srv002_1624002971362_44244', '==> srv002: Clearing any previously set network interfaces...', '==> srv002: Preparing network interfaces based on configuration...', '    srv002: Adapter 1: nat', '    srv002: Adapter 2: hostonly', '==> srv002: Forwarding ports...', '    srv002: 22 (guest) => 2291 (host) (adapter 1)', '    srv002: 80 (guest) => 8081 (host) (adapter 1)', '    srv002: 443 (guest) => 8143 (host) (adapter 1)', \"==> srv002: Running 'pre-boot' VM customizations...\", '==> srv002: Booting VM...', '==> srv002: Waiting for machine to boot. This may take a few minutes...', '    srv002: SSH address: 127.0.0.1:2291', '    srv002: SSH username: vagrant', '    srv002: SSH auth method: private key', '    srv002: ', '    srv002: Vagrant insecure key detected. Vagrant will automatically replace', '    srv002: this with a newly generated keypair for better security.', '    srv002: ', '    srv002: Inserting generated public key within guest...', \"    srv002: Removing insecure key from the guest if it's present...\", '    srv002: Key inserted! Disconnecting and reconnecting using new SSH key...', '==> srv002: Machine booted and ready!', '==> srv002: Checking for guest additions in VM...', '    srv002: The guest additions on this VM do not match the installed version of', '    srv002: VirtualBox! In most cases this is fine, but in rare cases it can', '    srv002: prevent things such as shared folders from working properly. If you see', '    srv002: shared folder errors, please make sure the guest additions within the', '    srv002: virtual machine match the version of VirtualBox you have installed on', '    srv002: your host and reload your VM.', '    srv002: ', '    srv002: Guest Additions Version: 5.2.0 r68940', '    srv002: VirtualBox Version: 6.1', '==> srv002: Setting hostname...', '==> srv002: Configuring and enabling network interfaces...', '==> srv002: Installing rsync to the VM...', '==> srv002: Rsyncing folder: /home/jean/dev/ansible_collections/jclaveau/vagrant/tests/integration/ => /vagrant', '==> srv002: Running provisioner: shell...', '    srv002: Running: inline script', '    srv002: srv002', '', \"==> srv002: Machine 'srv002' has a post `vagrant up` message. This is a message\", '==> srv002: from the creator of the Vagrantfile, and not from Vagrant itself:', '==> srv002: ', '==> srv002: Vanilla Debian box. See https:/app.vagrantup.com/debian for help and bug reports'], 'stderr_lines': [], 'invocation': {'module_args': {'name': 'srv002', 'vagrant_root': '.', 'provider': None, 'provision': None, 'provision_with': None}}, 'finished': 1, 'ansible_job_id': '530404870597.516659', 'failed': False, 'attempts': 1, 'item': {'started': 1, 'finished': 0, 'ansible_job_id': '530404870597.516659', 'results_file': '/home/jean/.ansible_async/530404870597.516659', 'changed': True, 'failed': False, 'item': 'srv002', 'ansible_loop_var': 'item'}, 'ansible_loop_var': 'item'}], 'changed': True, 'msg': 'All items completed'}":[[-1,1],[1,-1]]}}
# With True
# integration=commands=local-3.8=python-3.8=coverage.jean-ThinkPad-X1-Carbon-6th.516001.592705:1:!coverage.py: This is a private format, don't read it directly!{"arcs":{"/home/jean/dev/ansible_collections/jclaveau/vagrant/tests/integration/True":[[-1,1],[1,-1]]}}

import subprocess
import os
import re
import json


script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir + '/../')

coverage_path = 'tests/output/coverage/'
coverage_files = os.listdir(coverage_path)

# coverage_files = [
#     'integration=commands=local-3.8=python-3.8=coverage.jean-ThinkPad-X1-Carbon-6th.516129.646545'
# ]

for coverage_file in coverage_files:
    with open(coverage_path + coverage_file, 'r') as f:
        coverage_file_content = f.read()
        fixed = False

        for pattern, replacement in {
            r'\\"[^"]*\\"': "''",  # replace all escaped double-quoted strings by simple-quoted empty strings
            r'"/[^"]+/(\[[^"]+\])"': '',  # remove [] json content in paths
            r'"/[^"]+/(\{[^"]+\})"': '',  # remove {} json content in paths
            r'"/[^"]+/(True)"': '',  # remove True json content in paths
            r'"/[^"]+/(False)"': '',  # remove False json content in paths (never found until now but could occure)
        }.items():
            # print(pattern)
            # print(replacement)
            # quit()
            re_results = re.findall(pattern, coverage_file_content)

            # print(json.dumps(re_results, indent=4))
            # print("\n")

            if len(re_results):
                for re_result in re_results:
                    print('Replacing ' + re_result)
                    print('By ' + replacement)
                    fixed = True
                    coverage_file_content = coverage_file_content.replace(re_result, replacement)

        if fixed:
            os.remove(coverage_path + coverage_file)
            print("Coverage file invalid thus removed '%s'" % coverage_file)
            continue

        # Check json validity
        coverage_file_content_json_part = coverage_file_content.replace('!coverage.py: This is a private format, don\'t read it directly!', '')

        if coverage_file_content_json_part == '{"arcs":{}}':
            os.remove(coverage_path + coverage_file)
            print("Coverage file empty thus removed '%s'" % coverage_file)
            continue

        try:
            json_content = json.loads(coverage_file_content_json_part)
        except json.decoder.JSONDecodeError:
            print("Invalid JSON remains in repaired coverage file '%s'" % coverage_file)
            continue

        if len(json_content['arcs']) == 1:
            for covered_file in json_content['arcs']:
                # just retrieving the first key of the dict
                break

            if os.path.isdir(covered_file):
                os.remove(coverage_path + coverage_file)
                print("Coverage file targets directory. Removing it '%s'" % coverage_file)
                continue

        print("Coverage file repaired '%s'" % coverage_file)
        with open(coverage_path + coverage_file, 'w') as f:
            f.write(coverage_file_content)
