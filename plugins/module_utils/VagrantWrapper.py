
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.jclaveau.vagrant.plugins.module_utils.constants import DEFAULT_ROOT
from ansible.module_utils.basic import missing_required_lib  # https://docs.ansible.com/ansible-core/devel/dev_guide/testing/sanity/import.html

import os.path
import traceback
import tempfile
import re
import subprocess
import time

try:
    import vagrant
except ImportError as e:
    HAS_VAGRANT_LIBRARY = False
    VAGRANT_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_VAGRANT_LIBRARY = True


class VagrantWrapper(object):

    def __init__(self, *args, **kwargs):
        '''
        Wrapper around the python-vagrant module for use with ansible.
        Note that Vagrant itself is non-thread safe, as is the python-vagrant lib, so we need to lock on basically all operations ...
        '''

        self.module = kwargs.setdefault('module', None)
        self.root_path = os.path.abspath(kwargs.setdefault('root_path', DEFAULT_ROOT))

        self.stdout_file = tempfile.NamedTemporaryFile()  # pylint: disable=consider-using-with
        self.stdout_filename = self.stdout_file.name
        self.stderr_file = tempfile.NamedTemporaryFile()  # pylint: disable=consider-using-with
        self.stderr_filename = self.stderr_file.name

        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)

        if not HAS_VAGRANT_LIBRARY:
            self.module.fail_json(
                msg=missing_required_lib('vagrant'),
                exception=VAGRANT_LIBRARY_IMPORT_ERROR)

        vgargs = []
        vgkwargs = dict(root=self.root_path)
        vgkwargs['out_cm'] = vagrant.make_file_cm(self.stdout_filename, mode='a')
        vgkwargs['err_cm'] = vagrant.make_file_cm(self.stderr_filename, mode='a')

        self.vg = vagrant.Vagrant(*vgargs, **vgkwargs)

    def stdout(self):
        with open(self.stdout_filename, mode='r') as f:
            for line in f:
                yield re.sub('\n$', '', line)

    def stderr(self):
        with open(self.stderr_filename, mode='r') as f:
            for line in f:
                yield re.sub('\n$', '', line)

    def fail_module(self, msg):
        self.module.fail_json(
            msg=" %s\n\nCMD STDOUT\n%s\n\nCMD STDERR\n%s" % (
                msg,
                "\n".join(list(self.stdout())),
                "\n".join(list(self.stderr())),
            ),
            stdout_lines=list(self.stdout()),
            stderr_lines=list(self.stderr()),
        )

    def raw_statuses(self, name=None, must_be_present=True):
        out = {}
        try:
            # result = self.vg.status(name)[0].state
            results = self.vg.status(name)
            for result in results:
                # print(result)
                # quit(result)
                out[result.name] = {
                    'name': result.name,
                    'state': result.state,
                    'provider': result.provider,
                }
        except subprocess.CalledProcessError as e:
            if not len(e.stdout):
                self.fail_module(e)
            stderr_parts = e.stdout.split(b',')
            stderr = stderr_parts[7] + b': ' + stderr_parts[8].replace(b'\\n', b' ')
            with open(self.stderr_filename, 'a') as f:
                f.write(stderr.decode('utf-8'))
            out[name] = {
                'name': 'name',
                'state': 'absent',
                'provider': None,
            }

            if must_be_present:
                self.fail_module(stderr.decode('utf-8'))
        return out

    def status(self, name=None):
        start = time.time()
        changed = False
        statuses = self.raw_statuses(name, must_be_present=True)
        end = round(time.time(), 2)
        return (changed, end - start, list(statuses.values()))

    def port(self, name=None, guest=None):
        start = time.time()
        changed = False

        try:
            output = self.vg._run_vagrant_command([
                'port',
                name,
                '--machine-readable'
            ])

            output = self.vg._parse_machine_readable_output(output)
            ports = []
            for line in output:
                if guest and guest != int(line[3]):
                    continue
                ports.append({
                    'guest': int(line[3]),
                    'host': int(line[4]),
                })
        except subprocess.CalledProcessError as e:
            output = self.vg._parse_machine_readable_output(e.stdout.decode('utf-8'))
            stderr = output[0][3] + ": " + output[0][4]
            with open(self.stderr_filename, 'a') as f:
                f.write(stderr)
            self.fail_module(e)

        end = round(time.time(), 2)
        return (changed, end - start, ports)

    def ssh_config(self, name):
        start = time.time()
        changed = False

        ssh_configs = []
        try:
            outputs = self.vg.ssh_config(name).strip().split("\n\n")
            for output in outputs:
                config = self.vg.conf(output)

                # This option avoids "Warning: Permanently added '[127.0.0.1]:2291' (ECDSA) to the list of known hosts."
                config["NoHostAuthenticationForLocalhost"] = "yes"

                sshcmd = ("ssh %s@%s -p %s -i %s "
                          "-o StrictHostKeyChecking=%s "
                          "-o UserKnownHostsFile=%s "
                          "-o IdentitiesOnly=%s "
                          "-o NoHostAuthenticationForLocalhost=%s"
                          ) % (
                              config["User"],
                              config["HostName"],
                              config["Port"],
                              config["IdentityFile"],
                              config["StrictHostKeyChecking"],
                              config["UserKnownHostsFile"],
                              config["IdentitiesOnly"],
                              config["NoHostAuthenticationForLocalhost"])
                config['command'] = sshcmd
                ssh_configs.append(config)

        except subprocess.CalledProcessError as e:
            self.fail_module(e)

        end = round(time.time(), 2)
        return (changed, end - start, ssh_configs)

    def ssh(self, name, command):
        start = time.time()
        changed = False

        output = None
        try:
            output = self.vg.ssh(vm_name=name, command=command)
            changed = True
            with open(self.stdout_filename, 'a') as f:
                f.write(output)
        except subprocess.CalledProcessError as e:
            # print_err(e)
            # quit()
            self.fail_module(e)

        end = round(time.time(), 2)
        return (changed, end - start)

    def up(self, name=None, provider=None, provision=None, provision_with=None):
        """
        Fire up a given VM and name it, using vagrant's multi-VM mode.
            def up(self, no_provision=False, provider=None, vm_name=None,
           provision=None, provision_with=None, stream_output=False):

        """
        start = time.time()
        changed = False
        status_before = self.raw_statuses(name, must_be_present=True)[name]

        if status_before['state'] != 'running':
            try:
                self.vg.up(
                    vm_name=name,
                    provider=provider,
                    provision=provision,
                    provision_with=provision_with,
                    stream_output=False  # !!! Produces error in Ansible if true "AttributeError: 'list' object has no attribute 'splitlines'"
                )
            except subprocess.CalledProcessError as e:
                if not e.stdout:
                    self.fail_module(e)

                stderr_parts = e.stdout.split(b',')
                stderr = stderr_parts[7] + b': ' + stderr_parts[8].replace(b'\\n', b' ')
                with open(self.stderr_filename, 'a') as f:
                    f.write(stderr.decode('utf-8'))
                self.fail_module(e)

            status_after = self.raw_statuses(name, must_be_present=True)[name]
            if status_before['state'] != status_after['state']:
                changed = True
        else:
            status_after = status_before

        end = round(time.time(), 2)
        return (changed, end - start, status_before['state'], status_after['state'])

    def reload(self, name, provision=None, provision_with=None):
        start = time.time()
        changed = False
        status_before = self.raw_statuses(name=name, must_be_present=True)[name]

        if status_before['state'] == 'running':
            self.vg.reload(
                vm_name=name,
                provision=provision,
                provision_with=provision_with,
                # force=force,  # not implemented in python-vagrant
            )
            status_after = self.raw_statuses(name, must_be_present=True)[name]
            # status values "running" before AND after but the machine status has temporary been "poweroff"
            changed = True
        else:
            status_after = status_before

        end = round(time.time(), 2)
        return (changed, end - start, status_before['state'], status_after['state'])

    def halt(self, name=None, force=False):
        start = time.time()
        changed = False
        status_before = self.raw_statuses(name, must_be_present=True)[name]

        if status_before['state'] != 'poweroff':
            self.vg.halt(
                vm_name=name,
                force=force
            )
            status_after = self.raw_statuses(name, must_be_present=True)[name]
            if status_before['state'] != status_after['state']:
                changed = True
        else:
            status_after = status_before

        end = round(time.time(), 2)
        return (changed, end - start, status_before['state'], status_after['state'])

    def destroy(self, name):
        start = time.time()
        changed = False
        status_before = self.raw_statuses(name, must_be_present=True)[name]

        if status_before['state'] != 'not_created':
            self.vg.destroy(
                vm_name=name
            )
            status_after = self.raw_statuses(name, must_be_present=True)[name]
            if status_before['state'] != status_after['state']:
                changed = True
        else:
            status_after = status_before

        end = round(time.time(), 2)
        return (changed, end - start, status_before['state'], status_after['state'])

    def suspend(self, name):
        start = time.time()
        changed = False
        status_before = self.raw_statuses(name, must_be_present=True)[name]

        if status_before['state'] != 'saved':
            self.vg.suspend(
                vm_name=name
            )
            status_after = self.raw_statuses(name, must_be_present=True)[name]
            if status_before['state'] != status_after['state']:
                changed = True
        else:
            status_after = status_before

        end = round(time.time(), 2)
        return (changed, end - start, status_before['state'], status_after['state'])

    def resume(self, name):
        start = time.time()
        changed = False
        status_before = self.raw_statuses(name, must_be_present=True)[name]

        if status_before['state'] != 'running':
            self.vg.resume(
                vm_name=name
            )
            status_after = self.raw_statuses(name, must_be_present=True)[name]
            if status_before['state'] != status_after['state']:
                changed = True
        else:
            status_after = status_before

        end = round(time.time(), 2)
        return (changed, end - start, status_before['state'], status_after['state'])
