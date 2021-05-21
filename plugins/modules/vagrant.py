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

DOCUMENTATION = '''
---
module: vagrant
short_description: create a local instance via vagrant
description:
     - creates VM instances via vagrant and optionally waits for it to be
       'running'. This module has a dependency on python-vagrant.
version_added: "0.0.1"
author:
    - "Rob Parrott (@robparrott)"
    - "caljess599 (@caljess599)"
    - "Majid alDosari (@majidaldo)"
    - "Tomas Kadlec (@tomaskadlec)"
    - "Jean Claveau (@jclaveau)"
options:
  state:
    description: Should the VMs be "up" or "halt"
    type: str
  cmd:
    description:
      - vagrant subcommand to execute. Can be "up," "status," "config,"
        "ssh_command," "halt," "destroy" or "clear."
    type: str
    required: false
    default: null
    aliases: ['command']
  box_name:
    description:
      - vagrant boxed image to start
    type: str
    required: false
    default: null
    aliases: ['image']
  box_path:
    description:
      - path to vagrant boxed image to start
    type: str
    required: false
    default: null
    aliases: []
  vm_name:
    description:
      - name to give an associated VM
    type: str
    required: false
    default: null
    aliases: []
  count:
    description:
      - number of instances to launch
    type: int
    required: False
    default: 1
    aliases: []
  forward_ports:
    description:
      - comma separated list of ports to forward to the host
    type: str
    required: False
    aliases: []
  log:
    description:
      - Whether or not Vagrant's logs must be stored
    type: bool
    default: false
  share_folder:
    default:
    description:
      - shared folder directory which mounts to /vagrant on the machine
        by default
    type: str
  share_mount:
    description:
      - A shared mount
    type: str
    default: /vagrant
  vagrant_root:
    description:
      - the folder where vagrant files will be stored
    type: str
    default: .
  config_code:
    default: ""
    description:
      - custom configuation code that goes in the vagrantfile such as
        hypervisor options.
        The word config will be converted to config_"machine" so that
        you can have machine-specific options.
    type: str
  provider:
    default: virtualbox
    type: str
    description:
      - a provider to use instead of default virtualbox
requirements: ["vagrant, lockfile"]
'''


EXAMPLES = '''
- name: Spawn a new VM instance
  jclaveau.vagrant.vagrant:
    state: up
    vm_name: my_vm
    boc_name: debian/buster64
'''

import sys
import subprocess
import os.path
import json
import ast
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib  # https://docs.ansible.com/ansible-core/devel/dev_guide/testing/sanity/import.html
import traceback
import fcntl
from io import StringIO

try:
    import vagrant
except ImportError:
    HAS_VAGRANT_LIBRARY = False
    VAGRANT_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_VAGRANT_LIBRARY = True

try:
    import lockfile
except ImportError:
    HAS_LOCKFILE_LIBRARY = False
    LOCKFILE_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_LOCKFILE_LIBRARY = True

VAGRANT_FILE_HEAD = "Vagrant.configure(\"2\") do |config|\n"
VAGRANT_FILE_BOX_NAME = "  config.vm.box = \"%s\"\n"
VAGRANT_FILE_VM_STANZA_HEAD = """
  config.vm.define :%s do |%s_config|
    %s_config.vm.network "private_network", ip: "%s"
    %s_config.vm.box = "%s"
    %s_config.vm.synced_folder ".", "/vagrant", disabled: true
"""
VAGRANT_FILE_HOSTNAME_LINE = "    %s_config.vm.host_name = \"%s\"\n"
VAGRANT_FILE_PORT_FORWARD_LINE = "    %s_config.vm.network \"forwarded_port\", guest: %s, host: %s\n"
VAGRANT_FILE_SYNCED_FOLDER_LINE = "    %s_config.vm.synced_folder \"%s\", \"%s\", type: \"nfs\" , disabled: %s"
VAGRANT_FILE_VM_STANZA_TAIL = "  end\n"
VAGRANT_FILE_TAIL = "\nend\n"

VAGRANT_LOG_FN = 'vagrant.log'

# If this is already a network on your machine, this may fail ... change it here.
VAGRANT_INT_IP = "192.168.179.%s"

DEFAULT_VM_NAME = "ansiblevagrant"


class VagrantWrapper(object):

    def __init__(self, *args, **kwargs):
        '''
        Wrapper around the python-vagrant module for use with ansible.
        Note that Vagrant itself is non-thread safe, as is the python-vagrant lib, so we need to lock on basically all operations ...
        '''

        log = kwargs.setdefault('log', False)
        self.config_code = kwargs.setdefault('config_code', "\n;\n;")
        self.share_folder = kwargs.setdefault('share_folder', ".")
        self.share_mount = kwargs.setdefault('share_mount', "/vagrant")
        self.provider = kwargs.setdefault('provider', "virtualbox")
        self.module = kwargs.setdefault('module', None)

        # Get a lock
        self.lock = None

        if not HAS_VAGRANT_LIBRARY:
            self.module.fail_json(
                msg=missing_required_lib('vagrant'),
                exception=VAGRANT_LIBRARY_IMPORT_ERROR)

        try:
            self.lock = lockfile.FileLock(VAGRANT_LOCKFILE)
            self.lock.acquire()
        except Exception:
            # fall back to using flock instead ...
            try:
                with open(VAGRANT_LOCKFILE, 'w') as self.lock:
                    fcntl.flock(self.lock, fcntl.LOCK_EX)
            except Exception:
                self.module.debug(
                    "failed=True msg='Could not get "
                    + "a lock for using vagrant. Install python "
                    + "module \"lockfile\" to use vagrant on non-POSIX filesytems.'"
                )
                self.module.fail_json()

        # Initialize vagrant and state files

        vgargs = []
        vgkwargs = dict(root=VAGRANT_ROOT)
        if log:
            log_cm = vagrant.make_file_cm(VAGRANT_LOGFILE)
            vgkwargs['out_cm'] = log_cm
            vgkwargs['err_cm'] = log_cm

        self.vg = vagrant.Vagrant(*vgargs, **vgkwargs)

        # operation will create a default data structure if none present
        self._deserialize()
        self._serialize()

    def __del__(self):
        "Clean up file locks"
        try:
            self.lock.release()
        except Exception:
            os.close(self.lock)
            os.unlink(self.lock)

    def prepare_box(self, box_name, box_path):
        """
        Given a specified name and URL, import a Vagrant "box" for use.
        """
        changed = False
        if box_name is None:
            raise Exception("You must specify a box_name with a box_path for vagrant.")

        # get vagrant's list of boxes
        boxlist = self.vg.box_list()

        # make a list of just the 'name' attribute
        boxnamelist = []
        for Box in boxlist:
            boxname = Box.name
            boxnamelist.append(boxname)

        # check to see if 'box_name' is in this list
        if box_name not in boxnamelist:
            self.vg.box_add(box_name, box_path)
            changed = True

        return changed

    def up(self, box_name, vm_name=None, count=1, box_path=None, ports=None, share_folder=None):
        """
        Fire up a given VM and name it, using vagrant's multi-VM mode.
        """
        new_port = False
        new_box = False
        changed = False

        if vm_name is None:
            vm_name = DEFAULT_VM_NAME
        if box_name is None:
            raise Exception("You must specify a box name for Vagrant.")
        if box_path is not None:
            changed = self.prepare_box(box_name, box_path)

        for c in range(int(count)):

            self._deserialize()

            d = self._get_instance(vm_name, c)
            # vm_name is new, so assign box_name and ports
            if 'box_name' not in d:
                d['box_name'] = box_name
                d['forward_ports'] = ports
            # vm_name is not new, let's check for changes
            else:
                if d['box_name'] != box_name:
                    d['box_name'] = box_name
                    new_box = True
                if d['forward_ports'] != ports:
                    d['forward_ports'] = ports
                    new_port = True

            # Save our changes and run
            inst_array = self._instances()[vm_name]
            inst_array[c] = d

            self._serialize()

            # See what steps we need to take to get the newer ones running
            vgn = d['vagrant_name']
            status = self.vg.status(vgn)[0].state
            if new_box:
                if status in ['running', 'poweroff', 'saved']:
                    self.vg.destroy(vm_name=d['vagrant_name'])
                self.vg.up(False, vm_name=d['vagrant_name'], provider=self.provider)
                changed = True

            # not new box
            else:
                if status != 'running':
                    # bring it up, new port will take care of itself
                    self.vg.up(False, vm_name=d['vagrant_name'], provider=self.provider)
                    changed = True
                else:
                    if new_port:
                        self.vg.reload(vm_name=d['vagrant_name'])
                        changed = True
                    # do nothing

        ad = self._build_instance_array_for_ansible(vm_name)
        return (changed, ad)

    def names_to_instance_names(self, vm_name=None):
        if isinstance(vm_name, str):
            try:
                vm_names = ast.literal_eval(vm_name)
            except ValueError:
                vm_names = [vm_name]
        elif isinstance(vm_name, list):
            vm_names = vm_name
        else:
            vm_names = [vm_name]

        if len(vm_names) == 0:
            vm_names.append(None)  # [None] if no vm specified
        # print(vm_names)
        # quit()
        # else:
        #     vm_names = list(self._instances().keys())

        return vm_names

    def status(self, vm_name=None):
        """
        Return the run status of the VM instance. If no instance N is given, returns first instance.
        """
        vm_names = self.names_to_instance_names(vm_name)

        out = {}
        for vm_name in vm_names:
            try:
                status_results = self.vg.status(vm_name)
            except subprocess.CalledProcessError as e:
                stderr = e.stdout.split(b'\n')[1].split(b',')
                self.module.fail_json(msg=stderr[3] + b': ' + stderr[4].replace(b'\\n', b' '))
            for status_result in status_results:
                out[status_result[0]] = status_result._asdict()

        return (False, out)

    def config(self, vm_name, n=-1):
        """
        Return info on SSH for the running instance.
        """
        vm_names = self.names_to_instance_names(vm_name)

        configs = {}
        for vmn in vm_names:
            conf_array = []
            instance_array = self.vg_data['instances'][vmn]
            if n >= 0:
                instance_array = [self._get_instance(vmn, n)]
            for inst in instance_array:
                cnf = self.vg.conf(None, inst['vagrant_name'])
                conf_array.append(cnf)
            configs[vmn] = conf_array

        return (False, configs)

    def halt(self, vm_params=None):
        """
        Shuts down a vm_name or all VMs.
        """
        statuses_before = self.status(vm_params)[1]
        vm_names = statuses_before.keys()
        for vm_name in vm_names:
            self.vg.halt(vm_name)

        changed = False
        statuses_after = self.status(vm_params)[1]
        for vm_name in vm_names:
            if statuses_before[vm_name]['state'] != statuses_after[vm_name]['state'] and statuses_after[vm_name]['state'] == 'poweroff':
                statuses_before[vm_name]['changed'] = True
                changed = True
            else:
                statuses_before[vm_name]['changed'] = False
            statuses_before[vm_name]['state'] = statuses_after[vm_name]['state']

        return (changed, statuses_before)  # We use statuses_before as output in case statuses_after has more vms due to concurrency

    def destroy(self, vm_name=None, n=-1):
        """
        Destroy a VM, or all VMs.
        """
        changed = False
        vm_names = self.names_to_instance_names(vm_name)


        statuses = {}
        for vmn in vm_names:
            stat_array = []
            instance_array = self.vg_data['instances'][vmn]
            if n > 1:
                if len(self.vg_data['instances'][vmn]) < n:
                    self.module.fail_json(msg="failed=True msg='VM to destroy cannot be found: %s_inst%d'" % (vmn, n))
                instance_array = [self.vg_data['instances'][vmn][n - 1]]
            for inst in instance_array:
                vgn = inst['vagrant_name']
                if self.vg.status(vgn)[0].state != 'not_created':
                    self.vg.destroy(vgn)
                    self.vg.halt(vgn)
                    changed = True
                stat_array.append(self.vg.status(vgn))
            statuses[vmn] = stat_array

        return (changed, statuses)

    def clear(self):
        """
        Destroy all VMs and clear all state data and configuration files
        """
        (changed, statuses) = self.destroy()

        for af in [VAGRANT_FILE, VAGRANT_DICT_FILE, VAGRANT_LOGFILE]:
            if os.path.isfile(af):
                changed = True
                os.remove(af)

        return (changed, statuses)

#
# Helper Methods
#
    def _instances(self):
        return self.vg_data['instances']

    def _get_instance(self, vm_name, n):
        instances = self._instances()

        inst_array = []
        if vm_name in instances:
            inst_array = instances[vm_name]

        if len(inst_array) > n:
            return inst_array[n]

        #
        # otherwise create one afresh
        #

        d = dict()
        N = self.vg_data['num_inst'] + 1
        # n = len(instances.keys())+1
        d['n'] = n
        d['N'] = N
        d['name'] = vm_name
        if n > 0:
            d['vagrant_name'] = "%s_inst%d" % (vm_name.replace("-", "_"), n + 1)
        else:
            d['vagrant_name'] = "%s" % (vm_name.replace("-", "_"))
        d['internal_ip'] = VAGRANT_INT_IP % (255 - N)
        d['forward_ports'] = []
        d['config_code'] = self.config_code
        d['share_folder'] = self.share_folder
        d['share_mount'] = self.share_mount
        self.vg_data['num_inst'] = N

        inst_array.append(d)
        self._instances()[vm_name] = inst_array

        return d

    # Serialize/Deserialize current state to a JSON representation, and
    #  a file format for Vagrant.
    #
    # This is where we need to deal with file locking, since multiple threads/procs
    #  may be trying to operate on the same files
    #
    def _serialize(self):
        self._save_state()
        self._write_vagrantfile()

    def _deserialize(self):
        self._load_state()

    # Manage a JSON representation of vagrantfile for statefulness across invocations.
    #
    def _load_state(self):
        self.vg_data = dict(num_inst=0, instances={})
        if os.path.isfile(VAGRANT_DICT_FILE):
            with open(VAGRANT_DICT_FILE) as json_file:
                self.vg_data = json.load(json_file)
                json_file.close()

    def _state_as_string(self, d):
        io = StringIO()
        json.dump(self.vg_data, io)
        return io.getvalue()

    def _save_state(self):
        with open(VAGRANT_DICT_FILE, 'w') as json_file:
            json.dump(self.vg_data, json_file, sort_keys=True, indent=4, separators=(',', ': '))
            json_file.close()

    #
    # Translate the state dictionary into the Vagrantfile
    #
    def _write_vagrantfile(self):
        with open(VAGRANT_FILE, 'w') as vfile:
            vfile.write(VAGRANT_FILE_HEAD)

            instances = self._instances()
            for vm_name in list(instances.keys()):
                inst_array = instances[vm_name]
                for c in range(len(inst_array)):
                    d = inst_array[c]
                    name = d['vagrant_name']
                    ip = d['internal_ip']
                    box_name = d['box_name']

                    vfile.write(VAGRANT_FILE_VM_STANZA_HEAD %
                                (name, name, name, ip, name, box_name, name))

                    vfile.write(VAGRANT_FILE_HOSTNAME_LINE % (name, name.replace('_', '-')))

                    if self.share_folder == "":
                        sfd = 'true'  # share folder disabled =
                        sf = '.'  # just whatever fill it w/ something valid
                    else:
                        sfd = 'false'
                        sf = self.share_folder
                    vfile.write(VAGRANT_FILE_SYNCED_FOLDER_LINE % (name, sf, self.share_mount, sfd))

                    if 'forward_ports' in d:
                        for p in d['forward_ports']:
                            if p:
                                vfile.write(VAGRANT_FILE_PORT_FORWARD_LINE % (name, p, (int(p) + 10000)))

                    config_code = ""
                    for aline in d['config_code'].splitlines():
                        if len(aline) == 0:
                            continue
                        if aline.lstrip()[0] != ';':  # ruby comment line
                            config_code += '\n    '
                            if 'config.' in aline:
                                config_code += (aline.replace('config.', '%s_config.')) % name
                            else:
                                config_code += aline
                        else:
                            continue
                    vfile.write(config_code + '\n' + VAGRANT_FILE_VM_STANZA_TAIL)

            vfile.write(VAGRANT_FILE_TAIL)
            vfile.close()

    #
    # To be returned to ansible with info about instances
    #
    def _build_instance_array_for_ansible(self, vmname=None):

        vm_names = []
        instances = self._instances()
        if vmname is not None:
            vm_names = [vmname]
        else:
            vm_names = list(instances.keys())

        ans_instances = []
        for vm_name in vm_names:
            for inst in instances[vm_name]:
                vagrant_name = inst['vagrant_name']
                cnf = self.vg.conf(None, vagrant_name)
                vg_data = instances[vm_name]
                if cnf is not None:
                    d = {
                        'name': vm_name,
                        'vagrant_name': vagrant_name,
                        'hostname': vagrant_name.replace('_', '-'),
                        'id': cnf['Host'],
                        'public_ip': cnf['HostName'],
                        'internal_ip': inst['internal_ip'],
                        'public_dns_name': cnf['HostName'],
                        'port': cnf['Port'],
                        'username': cnf['User'],
                        'key': cnf['IdentityFile'],
                        'status': self.vg.status(vagrant_name)
                    }
                    ans_instances.append(d)

        return ans_instances


# --------
# MAIN
# --------
def main():

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(),
            cmd=dict(required=False, aliases=['command']),
            box_name=dict(required=False, aliases=['image']),
            box_path=dict(),
            vm_name=dict(),  # Can also be a list of vm_names
            forward_ports=dict(),
            count=dict(default=1, type='int'),
            vagrant_root=dict(default='.'),
            log=dict(default=False, type='bool'),
            config_code=dict(default=""),
            # "" for None as i'm not sure of the None behavior python  <-> json
            share_folder=dict(default=""),
            share_mount=dict(default='/vagrant'),
            provider=dict(default="virtualbox")
        )
    )

    state = module.params.get('state')
    cmd = module.params.get('cmd')
    box_name = module.params.get('box_name')
    box_path = module.params.get('box_path')
    vm_name = module.params.get('vm_name')
    forward_ports = module.params.get('forward_ports')
    vagrant_root = module.params.get('vagrant_root')
    log = module.boolean(module.params.get('log'))
    config_code = module.params.get('config_code')
    share_folder = module.params.get('share_folder')
    share_mount = module.params.get('share_mount')
    provider = module.params.get('provider')
    count = module.params.get('count')

    global VAGRANT_ROOT
    VAGRANT_ROOT = os.path.abspath(os.path.join(vagrant_root, ".vagrant"))
    if not os.path.exists(VAGRANT_ROOT):
        os.makedirs(VAGRANT_ROOT)

    global VAGRANT_FILE
    VAGRANT_FILE = VAGRANT_ROOT + "/Vagrantfile"
    global VAGRANT_DICT_FILE
    VAGRANT_DICT_FILE = VAGRANT_ROOT + "/Vagrantfile.json"
    global VAGRANT_LOCKFILE
    VAGRANT_LOCKFILE = VAGRANT_ROOT + "/.vagrant-lock"
    global VAGRANT_LOGFILE
    VAGRANT_LOGFILE = VAGRANT_ROOT + '/vagrant.log'

    if forward_ports is not None:
        forward_ports = forward_ports.split(',')
    if forward_ports is None:
        forward_ports = []

    # Initialize vagrant
    vgw = VagrantWrapper(
        module=module,
        log=log, config_code=config_code, share_folder=share_folder,
        share_mount=share_mount, provider=provider
    )

    #
    # Check if we are being invoked under an idempotency idiom of "state=present" or "state=absent"
    #
    try:
        if state is not None:
            possible_states = ['running', 'poweroff', 'not_created']
            if state not in possible_states:
                module.fail_json(msg="State must be one of [%s] instead of '%s'" % (", ".join(possible_states), state))

            if state == 'running':
                changd, insts = vgw.up(box_name, vm_name, count, box_path, forward_ports)
                module.exit_json(changed=changd, instances=insts)

            if state == 'poweroff':
                (changd, stats) = vgw.halt(vm_name)
                module.exit_json(changed=changd, status=stats)

            if state == 'not_created':
                (changd, stats) = vgw.destroy(vm_name, count)
                module.exit_json(changed=changd, status=stats)
        else:
            if cmd == 'up':
                # print "I am running cmd up"
                if count is None:
                    count = 1
                (changd, insts) = vgw.up(box_name, vm_name, count, box_path, forward_ports)
                module.exit_json(changed=changd, instances=insts)

            elif cmd == 'status':
                (changd, result) = vgw.status(vm_name)
                module.exit_json(changed=changd, status=result)

            elif cmd == "config" or cmd == "conf":
                if vm_name is None:
                    module.fail_json(msg="Error: you must specify a vm_name when calling config.")
                (changd, cnf) = vgw.config(vm_name)
                module.exit_json(changed=changd, config=cnf)

            elif cmd == 'ssh_command':
                if vm_name is None:
                    module.fail_json(msg="Error: you must specify a vm_name when calling ssh_command.")

                (changd, cnf) = vgw.config(vm_name)
                sshcmd = ("ssh %s@%s -p %s -i %s "
                          "-o StrictHostKeyChecking=no "
                          "-o NoHostAuthenticationForLocalhost=yes "
                          "-o IdentitiesOnly=yes"
                          ) % (
                              cnf[vm_name][0]["User"],
                              cnf[vm_name][0]["HostName"],
                              cnf[vm_name][0]["Port"],
                              cnf[vm_name][0]["IdentityFile"])
                sshmsg = "To connect to %s, execute in your shell the given command" % (vm_name)
                module.exit_json(changed=changd, msg=sshmsg, ssh_command=sshcmd)

#            elif cmd == "load_key":
#                if vm_name is None:
#                    module.fail_json(msg = "Error: you must specify a vm_name when calling load_key." )
#
#                cnf = vg.config(vm_name)
#                keyfile=cnf["IdentityFile"]
#
#                # Get loaded keys ...
#                loaded_keys = subprocess.check_output(["ssh-add", "-l"])
#                module.exit_json(changed = True, msg = loaded_keys)
#
#                subprocess.call(["ssh-add", keyfile])
#
#                module.exit_json(changed = True, msg = sshmsg, SshCommand = sshcmd)

            elif cmd == 'halt':
                (changd, stats) = vgw.halt(vm_name)
                module.exit_json(changed=changd, status=stats)

            elif cmd == 'destroy':
                (changd, stats) = vgw.destroy(vm_name, count)
                module.exit_json(changed=changd, status=stats)

            elif cmd == 'clear':
                (changd, stats) = vgw.clear()
                module.exit_json(changed=changd, status=stats)

            else:
                module.fail_json(msg="Unknown vagrant subcommand: \"%s\"." % (cmd))

    except subprocess.CalledProcessError as e:
        module.fail_json(msg="Vagrant command failed: %s\n%s" % (
            e,
            'Details in: ' + VAGRANT_LOGFILE if log
            else 'Add "log: true" option to find log in: ' + VAGRANT_LOGFILE
        ))
    # except Exception as e:
    #     module.fail_json(msg = e.__str__())
    module.exit_json(status="success")


main()
