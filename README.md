<!---
This file is auto-generate by a github hook please modify readme.md if you don't want to loose your work
-->
# ALPHA: Ansible Collection - [jclaveau.vagrant](git@github.com:jclaveau/ansible-vagrant-modules.git)
[![Sanity Tests](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/sanity-tests.yaml/badge.svg?branch=configurable_providers)](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/sanity-tests.yaml?query=branch%3Aconfigurable_providers)
[![Coverage](https://codecov.io/gh/jclaveau/ansible-vagrant-modules/branch/configurable_providers/graph/badge.svg?token=qlZsPUMdwP)](https://app.codecov.io/gh/jclaveau/ansible-vagrant-modules/branch/configurable_providers)
[![Integration Tests (MacOS/VirtualBox)](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/integration-tests-macos-virtualbox.yaml/badge.svg?branch=configurable_providers)](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/integration-tests-macos-virtualbox.yaml?query=branch%3Aconfigurable_providers)

#### Providers Integration Tests
[![Ubuntu/Libvirt](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/provider-integration-tests-ubuntu-libvirt.yaml/badge.svg?branch=configurable_providers)](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/provider-integration-tests-ubuntu-libvirt.yaml?query=branch%3Aconfigurable_providers)
[![Ubuntu/Docker](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/provider-integration-tests-ubuntu-docker.yaml/badge.svg?branch=configurable_providers)](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/provider-integration-tests-ubuntu-docker.yaml?query=branch%3Aconfigurable_providers)
[![MacOS/Virtualbox](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/provider-integration-tests-macos-virtualbox.yaml/badge.svg?branch=configurable_providers)](https://github.com/jclaveau/ansible-vagrant-modules/actions/workflows/provider-integration-tests-macos-virtualbox.yaml?query=branch%3Aconfigurable_providers)



This collection of modules provide access to [Vagrant](http://vagrantup.com/) commands and configuration of the Vagrantfile from [ansible](http://ansible.cc) playbooks and roles.

By allowing you to run guests on your local system, this module facilitates testing and development of orchestrated, distributed applications via ansible.

This collection should not be confused with [vagrant-ansible](https://github.com/dsander/vagrant-ansible) which allows you to run ansible playbooks on vagrant-launched hosts.

## Need
Preparing a GlusterFS cluster, I want to test it including the worst scenarios:
+ when a node need to reboot due to updates for example
+ when a node crashes and need to be reinstalled from scratch
+ when a split-brain occurs
+ If any of these critical case happends, I want to recieve notifications

For all these cases, I want the required provisionning playbooks/roles to handle all the typical recovery steps.

 - [molecule](https://molecule.readthedocs.io/en/latest/) and [ansible-test](https://docs.ansible.com/ansible/latest/dev_guide/testing.html) do not allow dynamic modifications of the platforms or hosts you play your roles / playbooks on, so they do not fit my needs.
 - Running vagrant from the shell module generated permission issues on Ubuntu
 - There is a well written role [amtega/ansible_role_vagrant_provisioner](https://github.com/amtega/ansible_role_vagrant_provisioner) as well but it doesn't support Ubuntu, probably because it calls `vagrant` from the shell too
 - The most trendy solution today seems to be [Terraform](https://github.com/hashicorp/terraform) used with [Terratest](https://github.com/gruntwork-io/terratest) but my goal here is to use `ansible-test` assertions instead of tests written in `golang`. Also the `Virtualbox` provider for `Terraform` doesn't work properly for now.

## Dependencies & Installation
Before this work is ready to be shared on [ansible-galaxy](https://galaxy.ansible.com/), you can include it in yor playbooks this way
```yaml
collections:
  - name: git@github.com:jclaveau/ansible-vagrant-modules.git
    type: git
    version: 0
```
Afterwards this should work
```sh
ansible-galaxy collection install jclaveau.vagrant
pip install -r requirements.txt
```

[Vagrant](http://vagrantup.com/) will require at least one [provider](https://www.vagrantup.com/docs/providers) like [VirtualBox](https://www.virtualbox.org), [Libvirt](https://github.com/vagrant-libvirt/vagrant-libvirt), [Docker](https://www.docker.io/) or [VMware](https://www.vmware.com/)

## Getting started with ansible-vagrant
This could be a test case for a GlusterFS role + playbook

```yaml
  # TODO chercher exemple de Playbook de provisionning lancé depuis Vagrant
- name: Add a vm to the Vagrantfile
  jclaveau.vagrant.config:
  args:
    state: "present"
    name: "{{ item }}"
    config:
      box: boxomatic/debian-11
      ansible:
        playbook: "glusterfs_provisionning_playbook.yml"
      shell:
        inline: 'echo "provisionning done"'
      forwarded_ports:
        - host: "808{{ i }}"
          guest: 80
        - host: "8{{ i }}43"
          guest: 443
    loop:
     - srv001
     - srv002
  loop_control:
    index_var: "i"

  - name: starting the node
    jclaveau.vagrant.up:
    args:
      name: "{{ item }}"
      provision: true
    register: up_result
    loop:
     - srv001
     - srv002

  - name: Check the status of the gluster peers
    shell: "gluster peer status"
    register: peers_status

  - name: show peers_status
    dbg:
      var: peers_status

  - name: Assert that all peers are available
      assert:
        that: '...'

  # destroy
  - name: destroy one node
    jclaveau.vagrant.destroy:
    args:
      name: srv001

  # check it's absence and throw a notification
  - name: Check the status of the gluster peers
    shell: "gluster peer status"
    register: peers_status

  - name: show peers_status
    dbg:
      var: peers_status

  - name: Assert that one peer is missing
        assert:
          that: '...'

  # recreate and reprovision it
  - name: recreate and reprovision it
    jclaveau.vagrant.up:
    args:
      name: srv001

  # check that the cluster works and the node is replaced
  - name: Check the status of the gluster peers
    shell: "gluster peer status"
    register: peers_status

  - name: show peers_status
    dbg:
      var: peers_status

  - name: Assert that all peers are available again
      assert:
        that: '...'
```

## Configuration examples

```yaml
  # TODO chercher exemple de Playbook de provisionning lancé depuis Vagrant
- name: Add a vm to the Vagrantfile
  jclaveau.vagrant.config:
  args:
    state: "present"
    name: "srv001"
    config:
      box: boxomatic/debian-11
      box_path: '/path/to/a/box/file'

      # Those options will trigger the required configuration of VirtualBox, Libvirt or Docker
      cpus: 2
      memory: 2048

      # By default, this Vagrantfile with configure a private_network working with dhcp
      ip: '192.168.10.1'
      mac: '...'
      netmask: '255.255.255.0'
      auto_config: false
      intnet: false # equivalent of :virtualbox__intnet

      # forwarded_ports can be configured verry easily
      forwarded_ports:
        - host: "8080"
          guest: 80
        - host: "8043"
          guest: 443
        - guest: 22
          host: 2270
          id: ssh

      # Provisionning
      ansible:
        playbook: "your_provisionning_playbook.yml"
      shell:
        inline: 'echo "provisionning done"'

      # Example for Libvirt provider
      provider: libvirt
      libvirt_options:
        nested: true
        features:
        - acpi
        - apic
        storage:
        - - :file
          - :path: libvirt_tests_shared_disk.img
            :size: 10M
        - - :file
          - :path: libvirt_tests_shared_disk_2.img
            :size: 15M

      # Example for Docker provider
      provider: docker
      docker_options:
        create_args:
          --cpuset-cpus: 1
        # image: tknerr/baseimage-ubuntu:18.04
        ports:
        - 9999:99

      # Example for Virtualbox provider
      provider: virtualbox
      virtualbox_options:
        name: "my_vm"
        linked_clone: true
        # gui: true
        check_guest_additions: false
        # All entries having '--' as prefix will trigger a call like provider.customize ['modifyvm', :id, key, value]
        --groups: "/my-vb-group"

      # Inline configuration for providers without dedicated support
      # If you do not find an ption you need, you can pass inline Ruby code which will be evaluated against the `provider`
      # object in the Vagrantfile
      provider: my_custom_provider
      provider_options_inline:
      - my_proprty = "my_value"
      - method_call ['param_1', 'param_2']

```

### Know important issues
#### Usage in roles/tests with add_host
In integration tests using `add_host` to add your newly created vm to your inventory wouldn't work.
This works perfectly in `playbooks` but is still untested with `roles`.

#### Paralellism
Rob Parrot, implemented a lock mechanism, commenting in 2014 that Vagrant had absolutelly no care of concurrency.
This doesn't seem to be the case anymore as Vagrant throws an error if you try to `up` a vm twice at the same time.
In conclusion I removed this mechanism, letting the responsability of concurrency to Vagrant itslef.

Presently, two Vagrant commands have `parellel` parameter available: `up` and `destroy`. This parameter delegates
concurrency handling to the provider (`Libvirt` handles it while `VirtualBox` doesn't for example).
Sadly these parameters are not implemented in `python-vagrant` which doesn't seem maintained for a while.
As a result, implementing the binding to this represents quite a lot of work and I consider it out of the scope of this first version.
In consequences, I chose to allow only one vm by `Vagrant` command and let the end user implement parallelism with `Ansible`'s `async` featuer like shown below.

Also Amtega teem implemented a role handling this async use of vagrant: https://github.com/amtega/ansible_role_vagrant_provisioner

You are please to implement it if you wish: [issue 39](https://github.com/jclaveau/ansible-vagrant-modules/issues/39)

```yaml
  - name: Start the 2 vagrant instances asynchronously
    jclaveau.vagrant.up:
    args:
      name: "{{ item }}"
    loop:
      - "srv001"
      - "srv002"
    async: 90
    poll: 0
    register: async_loop

  - name: dbg async_loop
    ansible.builtin.debug:
      var: async_loop

  - name: wait for up to finish
    async_status:
      jid: "{{item.ansible_job_id}}"
      mode: status
    retries: 120
    delay: 1
    loop: "{{async_loop.results}}"
    register: async_loop_jobs
    until: async_loop_jobs.finished
```

### TODO
Feel free to give a look to [the issues](https://github.com/jclaveau/ansible-vagrant-modules/issues) if you need a feature and have time to implement it.
The priority should ideally go to the [current target milestone issues](https://github.com/jclaveau/ansible-vagrant-modules/milestone/1).
### Contributing
 + fork this repo
 + clone it in a folder matching the following pattern `.../ansible_collections/jclaveau/ansible-vagrant-modules` (required by `Ansible`)
 + Enable hooks `git config core.hooksPath .githooks`
 + Install dependencies `pip install -r requirements.txt`
 + Run the tests at first time `./tests.sh`
 + Before beginning to code, please open an issue to discuss the integration of your feature. `Ansible` has a specific philosophy and we must follow it. `Vagrant` also has its own way.
 + Make a PR
 + Your PR will merged once it's fully tested and reviewed
 + Please keep in consideration that you will not want to maintain your code a long time so it has to be at the best quality and robustness.

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

#### 2017 - 2020 Thanks, to the team of [Ansible Skeleton](https://github.com/bertvv/ansible-skeleton) for their really smart work
- [Bert Van Vreckem](https://github.com/bertvv/) (maintainer)
- [Brian Stewart](https://github.com/thecodesmith)
- [Jeroen De Meerleer](https://github.com/JeroenED)
- [Mathias Stadler](https://github.com/MathiasStadler)

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
