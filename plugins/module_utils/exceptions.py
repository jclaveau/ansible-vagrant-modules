from __future__ import absolute_import, division, print_function
__metaclass__ = type

# from ansible_collections.jclaveau.vagrant.plugins.module_utils.constants import *

# class VagrantImportError(ImportError):
#    def __init__(self, arg):
#        VAGRANT_LIBRARY_IMPORT_ERROR
#       self.args = arg

class MachineNotFound(RuntimeError):
    """Raised when a targetted Vagrant machine doesn't exist"""
    pass

class NotImplementedInPythonVagrantError(NotImplementedError):
    """Raised when a Vagrant parameter is not implement because it's not in python-vagrant"""
    pass


        # Error example with missing Vagrantfile:

        #     $ vagrant status --machine-readable
        #     1424099094,,error-exit,Vagrant::Errors::NoEnvironmentError,A Vagrant environment or target machine is required to run this\ncommand. Run `vagrant init` to create a new Vagrant environment. Or%!(VAGRANT_COMMA)\nget an ID of a target machine from `vagrant global-status` to run\nthis command on. A final option is to change to a directory with a\nVagrantfile and to try again.
