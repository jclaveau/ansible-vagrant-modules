<!---
This file is auto-generate by a github hook please modify readme.md if you don't want to loose your work
-->
# Ansible Collection - [jclaveau.vagrant](git@github.com:jclaveau/ansible-vagrant.git)
[![Sanity Tests](https://github.com/jclaveau/ansible-vagrant-module/actions/workflows/sanity-tests.yaml/badge.svg?branch=refacto_vagrantfile_control)](https://github.com/jclaveau/ansible-vagrant-module/actions/workflows/sanity-tests.yaml?query=branch%3Arefacto_vagrantfile_control)
[![Integration Tests](https://github.com/jclaveau/ansible-vagrant-module/actions/workflows/integration-tests.yaml/badge.svg?branch=refacto_vagrantfile_control)](https://github.com/jclaveau/ansible-vagrant-module/actions/workflows/integration-tests.yaml?query=branch%3Arefacto_vagrantfile_control)
[![Coverage](https://codecov.io/gh/jclaveau/ansible-vagrant-module/branch/master/graph/badge.svg?token=qlZsPUMdwP)](https://codecov.io/gh/jclaveau/ansible-vagrant-module)



This collection of modules provide access to Vagrant commands.

It also provides a "config" module generating a vagrant-hosts.yml file that will be parsed by the Vagrantfile.

Forked from https://github.com/robparrott/ansible-vagrant

## Overview
Ansible-vagrant is a module for [ansible](http://ansible.cc) that allows you to create VMs on your local system using [Vagrant](http://vagrantup.com/).
This allows you to write ansible [playbooks](http://ansible.github.com/playbooks.html) that dynamically create local guests and configure them via the ansible playbook(s).
By allowing you to run guests on your local system, this module facilitates testing and development of orchestrated, distributed applications via ansible.

Ansible-vagrant should not be confused with [vagrant-ansible](https://github.com/dsander/vagrant-ansible) which allows you to run ansible playbooks on vagrant-launched hosts.

## Dependencies & Installation

The vagrant module for ansible requires:

 * a working [Vagrant](http://vagrantup.com/) install, which will itself
   require [VirtualBox](https://www.virtualbox.org/wiki/Downloads).
 * that the [vagrant-python](https://github.com/todddeluca/python-vagrant) is installed and in your python path

To install, couple the file "vagrant" to your ansible isntallation, under the "./library" directory.

To run the tests from the repository, cd into "./test" and run

    ansible-playbook -v -i hosts vagrant-test.yaml

## Getting started with ansible-vagrant

### Playbooks

### Parallel



### Changes

#### by caljess599:
* modified Vagrantfile output to use API version 2
* disabled synced folders on all VMs created by Vagrantfile
* specified that forwarded port # specified on guest will be forwarded on host to 10000+# (e.g., guest: 80, host: 10080)
* added VAGRANT_ROOT variable to control where script-generated files are placed, update paths accordingly
* passed in vm_name without relying on argument order; changed status variable definition so 'if not running' check works
* changed count logic so if count on inventory is 1, doesn't change the vm name
* added logic to check if box image has changed
* repaired prepare_box logic to check if base image is already downloaded

#### by majidaldo
* added log file. log: true|false
* added share_folder and share_mount nfs sharing (see module documentation)
* added config_code. custom configuation code that goes in the vagrantfile. the word config. will be converted to config_"machine" so that you can have machine-specific options. great for hypervisor options such as config.vm.memory ...


#### by tomaskadlec
* added provider option, default value is virtualbox

The following documentation is a lightly revised version of original.

