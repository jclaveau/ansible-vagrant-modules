# Ansible Collection - [jclaveau.vagrant]({{ remote.origin.url }})
[![Sanity Tests](https://github.com/{{ repository.name }}/actions/workflows/sanity-tests.yaml/badge.svg?branch={{ current.branch }})](https://github.com/{{ repository.name }}/actions/workflows/sanity-tests.yaml?query=branch%3A{{ current.branch }})
[![Integration Tests](https://github.com/{{ repository.name }}/actions/workflows/integration-tests.yaml/badge.svg?branch={{ current.branch }})](https://github.com/{{ repository.name }}/actions/workflows/integration-tests.yaml?query=branch%3A{{ current.branch }})
[![Coverage](https://codecov.io/gh/{{ repository.name }}/branch/master/graph/badge.svg?token=qlZsPUMdwP)](https://codecov.io/gh/{{ repository.name }})



This collection of modules provide access to [Vagrant](http://vagrantup.com/) commands and configuration of the Vagrantfile.

It's first goal is to provide the possibility of simulating cluster nodes failure to anticipate their recovery.


## Overview
Ansible-vagrant is a module for [ansible](http://ansible.cc) that allows you to create VMs on your local system using [Vagrant](http://vagrantup.com/).


## Need
 - molecule and ansible-test do not allow dynamic modification of the platforms/cluster you play your roles / playbooks on

This allows you to write ansible [playbooks](http://ansible.github.com/playbooks.html) that dynamically create local guests and configure them via the ansible playbook(s).
By allowing you to run guests on your local system, this module facilitates testing and development of orchestrated, distributed applications via ansible.

Ansible-vagrant should not be confused with [vagrant-ansible](https://github.com/dsander/vagrant-ansible) which allows you to run ansible playbooks on vagrant-launched hosts.

## Dependencies & Installation

```
ansible-galaxy collection install jclaveau.vagrant
pip install -r requirements.txt
```

 * a working [Vagrant](http://vagrantup.com/) install, which will itself
   require [VirtualBox](https://www.virtualbox.org/wiki/Downloads).


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
