
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import missing_required_lib  # https://docs.ansible.com/ansible-core/devel/dev_guide/testing/sanity/import.html
from ansible_collections.jclaveau.vagrant.plugins.module_utils.Vagrantfile import VAGRANTFILE_CONTENT

import copy
import traceback
import os.path

try:
    import yaml
except ImportError as e:
    HAS_YAML_LIBRARY = False
    YAML_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_YAML_LIBRARY = True

try:
    from deepdiff import DeepDiff
except ImportError as e:
    HAS_DEEPDIFF_LIBRARY = False
    DEEPDIFF_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_DEEPDIFF_LIBRARY = True


class VagrantConfig(object):

    def __init__(self, *args, **kwargs):
        '''
        Bridge between https://github.com/bertvv/ansible-skeleton and Ansible
        '''
        self.module = kwargs.setdefault('module', None)
        self.root = kwargs.setdefault('root', '.')
        self.parameters_requiring_recreate = ['box', 'box_path', 'provider', 'ansible', 'shell']
        # for libvirt https://github.com/vagrant-libvirt/vagrant-libvirt#reload-behavior

        root_path = os.path.abspath(self.root)
        if not os.path.exists(root_path):
            os.makedirs(root_path)

    def turn_present_in_config(self, name, new_config):
        found = False
        needs = []

        # The content that will be written to the yaml file
        updated_config = []

        # load the yaml file or create it
        with open(self.root + "/vagrant-hosts.yml", 'a+') as stream:
            stream.seek(0)
            if not HAS_YAML_LIBRARY:
                self.module.fail_json(
                    msg=missing_required_lib('yaml'),
                    exception=YAML_LIBRARY_IMPORT_ERROR)

            try:
                existing_config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.module.fail_json(msg=e)

            if not HAS_DEEPDIFF_LIBRARY:
                self.module.fail_json(
                    msg=missing_required_lib('deepdiff'),
                    exception=DEEPDIFF_LIBRARY_IMPORT_ERROR)

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

                            if (('values_changed' in diff and parameter_path in diff['values_changed'].keys()) or
                                    ('dictionary_item_added' in diff and parameter_path in diff['dictionary_item_added']) or
                                    ('dictionary_item_removed' in diff and parameter_path in diff['dictionary_item_removed'])):
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

        out = {
            'needs': needs
        }
        # print(out)
        return out

    def turn_absent_from_config(self, name, config_filter):
        found = False
        needs = []

        # The content that will be written to the yaml file
        updated_config = []

        # load the yaml file or create it
        with open(self.root + "/vagrant-hosts.yml", 'a+') as stream:
            stream.seek(0)

            if not HAS_YAML_LIBRARY:
                self.module.fail_json(
                    msg=missing_required_lib('yaml'),
                    exception=YAML_LIBRARY_IMPORT_ERROR)

            try:
                existing_config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.module.fail_json(msg=e)

            if not HAS_DEEPDIFF_LIBRARY:
                self.module.fail_json(
                    msg=missing_required_lib('deepdiff'),
                    exception=DEEPDIFF_LIBRARY_IMPORT_ERROR)

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
                stream.write(VAGRANTFILE_CONTENT)

    def dump(self, name=None, config_filter=None):
        out = []
        with open(self.root + "/vagrant-hosts.yml", 'r') as stream:

            if not HAS_YAML_LIBRARY:
                self.module.fail_json(
                    msg=missing_required_lib('yaml'),
                    exception=YAML_LIBRARY_IMPORT_ERROR)

            try:
                existing_config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.module.fail_json(msg=e)

            if not HAS_DEEPDIFF_LIBRARY:
                self.module.fail_json(
                    msg=missing_required_lib('deepdiff'),
                    exception=DEEPDIFF_LIBRARY_IMPORT_ERROR)

            if existing_config is not None:
                for existing_host in existing_config:
                    if name is not None and name != existing_host['name']:
                        continue
                    if config_filter is not None:
                        diff = DeepDiff(existing_host, config_filter)
                        if 'values_changed' in diff or 'dictionary_item_added' in diff:
                            continue
                    out.append(existing_host)

        return out
