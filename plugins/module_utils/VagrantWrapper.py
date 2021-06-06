
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.jclaveau.vagrant.plugins.module_utils.constants import *
from ansible_collections.jclaveau.vagrant.plugins.module_utils.Helpers import *
from ansible_collections.jclaveau.vagrant.plugins.module_utils.exceptions import MachineNotFound
from ansible_collections.jclaveau.vagrant.plugins.module_utils.exceptions import NotImplementedInPythonVagrantError

import os.path
# import ast
import traceback
import tempfile
import re
import subprocess
import time

try:
    import vagrant
except ImportError as e:
    HAS_VAGRANT_LIBRARY = False
    VAGRANT_LIBRARY_IMPORT_ERROR = e
    # VAGRANT_LIBRARY_IMPORT_ERROR = traceback.format_exc()
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

        self.stdout_file = tempfile.NamedTemporaryFile()
        self.stdout_filename = self.stdout_file.name
        self.stderr_file = tempfile.NamedTemporaryFile()
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
        self.module.fail_json(msg=" %s\n\nSTDOUT\n%s\n\nSTDERR\n%s" % (
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
                # raise MachineNotFound(stderr.decode('utf-8'))
        return out

    def status(self, name=None):
        start = time.time()
        changed = False
        statuses = self.raw_statuses(name, must_be_present=True)
        end = round(time.time(), 2)
        return (changed,  end - start, list(statuses.values()))

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
        return (changed,  end - start, ports)

    def up(self, name=None, no_provision=False, provider=None,
           provision=None, provision_with=None, parallel=False):
        """
        Fire up a given VM and name it, using vagrant's multi-VM mode.
            def up(self, no_provision=False, provider=None, vm_name=None,
           provision=None, provision_with=None, stream_output=False):

        """
        start = time.time()
        changed = False
        status_before = self.raw_statuses(name, must_be_present=True)[name]

        try:
            if status_before['state'] != 'running':
                self.vg.up(
                    vm_name=name,
                    no_provision=no_provision,
                    provider=provider,
                    provision=provision,
                    provision_with=provision_with,
                    stream_output=False  # !!! Produces error in Ansible if true "AttributeError: 'list' object has no attribute 'splitlines'"
                )
        except subprocess.CalledProcessError as e:
            print(e)
            quit()
            stderr_parts = e.stdout.split(b',')
            stderr = stderr_parts[7] + b': ' + stderr_parts[8].replace(b'\\n', b' ')
            with open(self.stderr_filename, 'a') as f:
                f.write(stderr.decode('utf-8'))
            self.fail_module(e)

        status_after = self.raw_statuses(name, must_be_present=True)[name]
        if status_before['state'] != status_after['state']:
            changed = True

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

        end = round(time.time(), 2)
        return (changed, end - start, status_before['state'], status_after['state'])

    def destroy(self, name):
        start = time.time()
        changed = False
        status_before = self.raw_statuses(name, must_be_present=True)[name]

        if status_before['state'] != 'not_created':
            self.vg.destroy(
                vm_name=name
                # fored always
                # --parallel parameter not implemented in python-vagrant
            )

        status_after = self.raw_statuses(name, must_be_present=True)[name]
        if status_before['state'] != status_after['state']:
            changed = True

        end = round(time.time(), 2)
        return (changed, end - start, status_before['state'], status_after['state'])

