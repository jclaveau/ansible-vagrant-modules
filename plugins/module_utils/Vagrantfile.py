
# This file is auto generated by a Github hook from the content of the Vagrantfile file of the same folder.
# Caution: All the changes you directly do here will be lost
# Please enable hooks for proper development by running `git config core.hooksPath .githooks`

VAGRANTFILE_CONTENT = """


# One Vagrantfile to rule them all!
#
# This is a generic Vagrantfile that can be used without modification in
# a variety of situations. Hosts and their properties are specified in
# `vagrant-hosts.yml`. Provisioning is done by an Ansible playbook,
# `ansible/site.yml`.
#
# See https://github.com/jclaveau/ansible-vagrant-modules for details
#
# Copyright 2021 Jean Claveau (https://github.com/jclaveau/ansible-vagrant-modules)
# Copyright 2017 - 2020 Bert Van Vreckem (https://github.com/bertvv/ansible-skeleton/commits?author=bertvv)
# Copyright 2018 Jonas Verhofsté (https://github.com/bertvv/ansible-skeleton/commits?author=JonasVerhofste)
# Copyright 2018 Mathias Stadler (https://github.com/bertvv/ansible-skeleton/commits?author=MathiasStadler)
# Copyright 2017 Jeroen De Meerleer  (https://github.com/bertvv/ansible-skeleton/commits?author=JeroenED)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

require 'rbconfig'
require 'yaml'

# set default LC_ALL for all BOXES
ENV["LC_ALL"] = "en_US.UTF-8"

# Set your default base box here
DEFAULT_BASE_BOX = 'bento/centos-7.6'

# When set to `true`, Ansible will be forced to be run locally on the VM
# instead of from the host machine (provided Ansible is installed).
FORCE_LOCAL_RUN = false

#
# No changes needed below this point
#

VAGRANTFILE_API_VERSION = '2'

# set custom vagrant-hosts file
vagrant_hosts = ENV['VAGRANT_HOSTS'] ? ENV['VAGRANT_HOSTS'] : 'vagrant-hosts.yml'
hosts = YAML.load_file(File.join(Dir.pwd, vagrant_hosts))

vagrant_groups = ENV['VAGRANT_GROUPS'] ? ENV['VAGRANT_GROUPS'] : 'vagrant-groups.yml'
if File.file?(vagrant_groups)
  groups = YAML.load_file(File.join(Dir.pwd, vagrant_groups))
else
  groups = []
end

# {{{ Helper functions

def run_locally?
  windows_host? || FORCE_LOCAL_RUN
end

def windows_host?
  Vagrant::Util::Platform.windows?
end

class VagrantPlugins::ProviderVirtualBox::Action::Network
  def dhcp_server_matches_config?(dhcp_server,config)
    true
  end
end

# Set options for the network interface configuration. All values are
# optional, and can include:
# - ip (default = DHCP)
# - netmask (default value = 255.255.255.0
# - mac
# - auto_config (if false, Vagrant will not configure this network interface
# - intnet (if true, an internal network adapter will be created instead of a
#   host-only adapter)
def network_options(host)
  options = {}

  if host.key?('ip')
    options[:ip] = host['ip']
    options[:netmask] = host['netmask'] ||= '255.255.255.0'
  else
    options[:type] = 'dhcp'
  end

  options[:mac] = host['mac'].gsub(/[-:]/, '') if host.key?('mac')
  options[:auto_config] = host['auto_config'] if host.key?('auto_config')
  options[:virtualbox__intnet] = true if host.key?('intnet') && host['intnet']
  options
end

def custom_synced_folders(vm, host)
  return unless host.key?('synced_folders')
  folders = host['synced_folders']

  folders.each do |folder|
    vm.synced_folder folder['src'], folder['dest'], folder['options']
  end
end

# Adds forwarded ports to your Vagrant machine
#
# example:
#  forwarded_ports:
#    - guest: 88
#      host: 8080
#    - guest: 22
#      host: 2270
#      id: ssh
def forwarded_ports(vm, host)
  if host.has_key?('forwarded_ports')

    host['forwarded_ports'].each do |port_config|
      port_options = {}
      port_config.each do |key, value|
        eval("port_options[:"+key+"] = value")
      end

      vm.network(:forwarded_port, **port_options)
    end
  end
end

def provision_ansible(node, host, groups)
  return unless host.key?('ansible')
  # https://www.vagrantup.com/docs/provisioning/ansible_intro
  # https://www.vagrantup.com/docs/provisioning/ansible
  ansible_mode = run_locally? ? 'ansible_local' : 'ansible'
  node.vm.provision ansible_mode do |ansible|
    ansible.compatibility_mode = '2.0'
    host['ansible'].each do |key, value|
      # ansible[key] = host['ansible'][key]  produces a bug due to the config implementation i guess
      eval("ansible."+key+" = host['ansible'][key]")
    end
    ansible.limit = 'all' if ! ansible.has? 'limit'
    ansible.limit = true if ! ansible.has? 'become'
    if ! groups.nil?
      ansible.groups = groups
    end
  end
end

def provision_shell(node, host)
  return unless host.key?('shell')
  node.vm.provision "shell" do |shell|
    # https://www.vagrantup.com/docs/provisioning/shell
    host['shell'].each do |key, value|
      # shell[key] = host['shell'][key] produces a bug due to the config implementation i guess
      eval("shell."+key+" = host['shell'][key]")
    end
  end

  # Could be useful https://stackoverflow.com/questions/15461898/passing-variable-to-a-shell-script-provisioner-in-vagrant
  # config.vm.provision "shell" do |s|
  #   s.binary = true # Replace Windows line endings with Unix line endings.
  #   s.inline = %Q(/usr/bin/env      #     TRACE=#{ENV['TRACE']}         #     VERBOSE=#{ENV['VERBOSE']}     #     FORCE=#{ENV['FORCE']}         #     bash my_script.sh)
  # end
end

def virtualbox_guest_additions(node, host)
  return unless host.key?('vbguest')

  if Vagrant.has_plugin?("vagrant-vbguest") then
    # https://github.com/dotless-de/vagrant-vbguest
    # https://subscription.packtpub.com/book/virtualization_and_cloud/9781786464910/1/ch01lvl1sec12/enabling-virtualbox-guest-additions-in-vagrant
    host['vbguest'].each do |key, value|
      # shell[key] = host['shell'][key] produces a bug due to the config implementation i guess
      eval("node.vbguest."+key+" = host['vbguest'][key]")
    end

    node.vbguest = false if ! ansible.has? 'auto_update' # Disables vbguest auto_update by default as it slows down tests
  end
end

def configure_provider_virtualbox(node, host)
  # https://docs.oracle.com/en/virtualization/virtualbox/6.0/user/vboxmanage-modifyvm.html
  node.vm.provider :virtualbox do |provider|
    provider.memory = host['memory'] if host.key? 'memory'
    provider.cpus = host['cpus'] if host.key? 'cpus'

    if host.key? 'virtualbox_options' then
      host['virtualbox_options'].each do |key, value|
        if key.match(/^--/) then
          provider.customize ['modifyvm', :id, key, value]
        else
          eval("provider."+key+" = value")
        end
      end
    end

      # TODO factorize
      if host.key? 'provider_options_inline' then
      host['provider_options_inline'].each do |line|
        eval("provider."+line)
      end
    end
  end
end

def configure_provider_libvirt(node, host)
  # https://github.com/vagrant-libvirt/vagrant-libvirt#provider-options

  # TODO check that it is required
  # Alternative solution https://stackoverflow.com/a/57708188/2714285 ?
  # if Vagrant.has_plugin?("vagrant-libvirt") then
  #   puts "The vagrant-libvirt plugin is required. Please install it with:"
  #   puts "$ vagrant plugin install vagrant-libvirt"
  #   return
  # end

  node.vm.provider :libvirt do |provider|
    provider.memory = host['memory'] if host.key? 'memory' # default 512
    provider.cpus = host['cpus'] if host.key? 'cpus' # default 1

    if host.key? 'libvirt_options' then
      host['libvirt_options'].each do |key, value|

        is_method_call = false
        if value.is_a?(Array) then
          # p value
          # exit

          value.each do |array_item|
            if array_item.is_a?(Array) and (array_item.length() == 1 or array_item.length() == 2) and
              array_item[0].is_a?(Symbol) and
              (array_item.length() == 1 or (array_item[1].is_a?(Array) or array_item[1].is_a?(Hash))) then
              is_method_call = true
            end
          end
        end

        if is_method_call then
          value.each do |array_item|
            provider.send(key, *array_item)
          end
        else
          # use send? https://stackoverflow.com/questions/3167966/ruby-using-object-send-for-assigning-variables
          eval("provider."+key+" = value")
        end
      end

      # TODO factorize
      if host.key? 'provider_options_inline' then
        host['provider_options_inline'].each do |line|
          eval("provider."+line)
        end
      end
    end
  end
end

def configure_provider_docker(node, host)
  # https://docs.docker.com/config/containers/resource_constraints/
  # https://stackoverflow.com/questions/47919339/vagrant-with-docker-provider-specifying-cpu-and-memory
  # https://www.vagrantup.com/docs/providers/docker/configuration
  node.vm.provider :docker do |provider|

    # provider.image = "foo/bar" # dup of box? https://www.vagrantup.com/docs/providers/docker/basics
    # https://www.vagrantup.com/docs/providers/docker/boxes

    provider.build_dir = "."
    provider.vagrant_vagrantfile = ".../path_to_vagrantfile_for_host_vm"
    provider.force_host_vm = false
    provider.has_ssh = true
    provider.remains_running = true

    provider.create_args = ['--cpuset-cpus=2']
    provider.create_args = ['--memory=6g']
  end
end


Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  hosts.each do |host|
    config.vm.define host['name'] do |node|
      node.vm.box = host['box'] ||= DEFAULT_BASE_BOX
      node.vm.box_url = host['box_url'] if host.key? 'box_url'
      node.vm.hostname = host['name']

      node.vm.network :private_network, **network_options(host)

      custom_synced_folders(node.vm, host)

      forwarded_ports(node.vm, host)

      virtualbox_guest_additions(node, host)

      # if not host.key? 'provider' || host['provider'] == 'virtualbox' then
      if host['provider'] == 'virtualbox' then
        configure_provider_virtualbox(node, host)
      elsif host['provider'] == 'libvirt' then
        configure_provider_libvirt(node, host)
      elsif host['provider'] == 'docker' then
        configure_provider_docker(node, host)
      end

      # Shell provisioning
      provision_shell(node, host)

      # Ansible provisioning
      provision_ansible(node, host, groups)
    end
  end
end

# -*- mode: ruby -*-
# vi: ft=ruby :


"""
