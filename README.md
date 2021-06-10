<!---
This file is auto-generate by a github hook please modify readme.md if you don't want to loose your work
-->
# WIP: Ansible Collection - [jclaveau.vagrant](git@github.com:jclaveau/ansible-vagrant.git)
[![Sanity Tests](https://github.com/jclaveau/ansible-vagrant/actions/workflows/sanity-tests.yaml/badge.svg?branch=refacto_vagrantfile_control)](https://github.com/jclaveau/ansible-vagrant/actions/workflows/sanity-tests.yaml?query=branch%3Arefacto_vagrantfile_control)
[![Integration Tests](https://github.com/jclaveau/ansible-vagrant/actions/workflows/integration-tests.yaml/badge.svg?branch=refacto_vagrantfile_control)](https://github.com/jclaveau/ansible-vagrant/actions/workflows/integration-tests.yaml?query=branch%3Arefacto_vagrantfile_control)
[![Coverage](https://codecov.io/gh/jclaveau/ansible-vagrant/branch/master/graph/badge.svg?token=qlZsPUMdwP)](https://codecov.io/gh/jclaveau/ansible-vagrant)


This collection of modules provide access to [Vagrant](http://vagrantup.com/) commands and configuration of the Vagrantfile from [ansible](http://ansible.cc) playbooks and roles.

By allowing you to run guests on your local system, this module facilitates testing and development of orchestrated, distributed applications via ansible.

## Need
It's first goal is to provide the possibility of simulating cluster nodes failure to anticipate their recovery.

 - [molecule](https://molecule.readthedocs.io/en/latest/) and [ansible-test](https://docs.ansible.com/ansible/latest/dev_guide/testing.html) do not allow dynamic modifications of the platforms or hosts you play your roles / playbooks on so they do not fit my needs.
 - Running vagrant from the shell module generated permission issues on Ubuntu
 - There is a well written role [amtega/ansible_role_vagrant_provisioner](https://github.com/amtega/ansible_role_vagrant_provisioner) as well but it doesn't
   support Ubuntu, probably because it calls 'vagrant' from the shell too

This collection should not be confused with [vagrant-ansible](https://github.com/dsander/vagrant-ansible) which allows you to run ansible playbooks on vagrant-launched hosts.

## Dependencies & Installation
Before this work is ready to be shared on ansible-galaxy, you could include it in yor playbooks this way
```yaml
collections:
  - name: git@github.com:jclaveau/ansible-vagrant.git
    type: git
    version: 0
```

```sh
ansible-galaxy collection install jclaveau.vagrant
pip install -r requirements.txt
```

[Vagrant](http://vagrantup.com/) will require at least one [provider](https://www.vagrantup.com/docs/providers) like [VirtualBox](https://www.virtualbox.org), [Libvirt](https://github.com/vagrant-libvirt/vagrant-libvirt), [Docker](https://www.docker.io/) or [VMware](https://www.vmware.com/)

## Getting started with ansible-vagrant

```yaml
- name: Add a vm to the Vagrantfile
  jclaveau.vagrant.config:
  args:
    state: "present"
    name: "srv001"
    config:
      box: boxomatic/debian-11
      ansible:
        playbook: "srv001_provisionning_playbook.yml"
      shell:
        inline: "shell provisionning command"
      forwarded_ports:
        - host: "8080"
          guest: 80
        - host: "8043"
          guest: 443

  - name: starting the node
    jclaveau.vagrant.up:
    args:
      name: srv001
      provision: true
    register: up_result

# check the output of your provisionning scripts
# check that a cluster works

# destroy
# recreate


# check the output of your provisionning scripts
# check that a cluster works

```

### Know important issues
+ Paralellism
+ Usage in roles with add_host
### TODO
 + Missing commands
 + Parralelism for 'up', 'destroy' and others
 + Missing plateforms windows

### Contributing
clone
hooks
tests
 - At least integration tests
guidelines
 - open an issue to discuss the way of implementing your needs. Ansible has a specific philosophy and we must follow it
 - make the code that will ask you for less maintainance a possible

### Licence
As every Ansible module, this code is distributed under [GPLv3.0+ licence](https://www.gnu.org/licenses/gpl-3.0.txt).

### Credits

#### 2014 - [Rob Parrot](https://github.com/robparrott/ansible-vagrant)
* initial working poc
#### 2015 - [caljess599](https://github.com/caljess599/ansible-vagrant)
* modified Vagrantfile output to use API version 2
* disabled synced folders on all VMs created by Vagrantfile
* specified that forwarded port # specified on guest will be forwarded on host to 10000+# (e.g., guest: 80, host: 10080)
* added VAGRANT_ROOT variable to control where script-generated files are placed, update paths accordingly
* passed in vm_name without relying on argument order; changed status variable definition so 'if not running' check works
* changed count logic so if count on inventory is 1, doesn't change the vm name
* added logic to check if box image has changed
* repaired prepare_box logic to check if base image is already downloaded

#### 2015 - [Majid alDosari](https://github.com/majidaldo/ansible-vagrant)
* added log file. log: true|false
* added share_folder and share_mount nfs sharing (see module documentation)
* added config_code. custom configuation code that goes in the vagrantfile. the word config. will be converted to config_"machine" so that you can have machine-specific options. great for hypervisor options such as config.vm.memory ...

#### 2017 - [Tomas Kadlec](https://github.com/majidaldo/ansible-vagrant/commits?author=tomaskadlec)
* added provider option, default value is virtualbox

#### 2021 - [Jean Claveau](https://github.com/jclaveau/ansible-vagrant-module)
* integrate `ansible-test` and setup CI with github actions
* integration tests and sanity tests
* Python 3 support
* replace the json and lock parts by integrating Vagrantfile driven by Yaml from [ansible-skeleton](https://github.com/bertvv/ansible-skeleton)
* full rewrite to reduce the code responsability thus improve it's maintainability: one module per vagrant command.
  A lot of the previous work has been suppressed here but it has been a huge source of inspiration for a nice workflow.
* vagrant stdout and stderr made available in ansible results
* rewrite simplified docs
* adding some missing Vagrant commands: suspend, resume, port, reload, ssh
* multi-provisionning support
