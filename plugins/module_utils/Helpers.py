
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.jclaveau.vagrant.plugins.module_utils.constants import *
import ast
import traceback

try:
    import vagrant
except ImportError as e:
    HAS_VAGRANT_LIBRARY = False
    VAGRANT_LIBRARY_IMPORT_ERROR = e
    # VAGRANT_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_VAGRANT_LIBRARY = True

def prepare_names_parameter(vm_name):
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

    return vm_names

def contruct_vagrant_instance(root, log):

    if not HAS_VAGRANT_LIBRARY:
        raise VAGRANT_LIBRARY_IMPORT_ERROR

    vgargs = []
    vgkwargs = dict(root=VAGRANT_ROOT)
    if log:
        log_cm = vagrant.make_file_cm(VAGRANT_LOGFILE)
        vgkwargs['out_cm'] = log_cm
        vgkwargs['err_cm'] = log_cm

    return vagrant.Vagrant(*vgargs, **vgkwargs)
