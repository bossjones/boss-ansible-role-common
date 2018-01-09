# -*- mode: ruby -*-
# # vi: set ft=ruby :
# https://github.com/hashicorp/vagrant/issues/8058

require 'fileutils'

Vagrant.require_version ">= 1.6.0"

# Vagrant VMs
host_cache_path = File.expand_path('../.cache', __FILE__)
guest_cache_path = '/tmp/vagrant-cache'

::Dir.mkdir(host_cache_path) unless ::Dir.exist?(host_cache_path)

default = {
  :user => ENV['OS_USER'] || 'vagrant',
  :project => File.basename(Dir.getwd),
  :ansible_project_name => ENV['_ANSIBLE_PROJECT_NAME'] || 'bossjones.common'
}

VM_NODENAME = "vagrant-#{default[:user]}-#{default[:project]}"

# Defaults for config options defined in CONFIG
$num_instances = 2
$instance_name_prefix = "ubuntu"
$enable_serial_logging = false
$share_home = false
$vm_gui = false
$vm_memory = 2048
$vm_cpus = 2
$forwarded_ports = {}


$fix_perm = <<SHELL
sudo chmod 600 /home/vagrant/.ssh/id_rsa
SHELL

# SOURCE: https://github.com/bossjones/docker-swarm-vbox-lab/blob/master/Vagrantfile
$docker_script = <<SHELL
if [ -f /vagrant_bootstrap ]; then
   echo "vagrant_bootstrap EXISTS ALREADY"
   exit 0
fi
export DEBIAN_FRONTEND=noninteractive
sudo apt-get autoremove -y && \
sudo apt-get update -yqq && \
sudo apt-get install -yqq software-properties-common \
                   python-software-properties && \
sudo apt-get install -yqq build-essential \
                   libssl-dev \
                   libreadline-dev \
                   wget curl \
                   openssh-server && \
sudo apt-get install -yqq python-setuptools \
                   perl pkg-config \
                   python python-pip \
                   python-dev && \
sudo fallocate -l 4G /swapfile && \
sudo chmod 600 /swapfile && \
sudo ls -lh /swapfile && \
sudo mkswap /swapfile && \
sudo swapon /swapfile && \
sudo swapon -s && \
free -m && \
sudo easy_install --upgrade pip && \
sudo easy_install --upgrade setuptools; \
sudo pip install setuptools --upgrade && \
sudo pip install urllib3[secure] && \
sudo add-apt-repository -y ppa:git-core/ppa && \
sudo add-apt-repository -y ppa:ansible/ansible && \
sudo add-apt-repository ppa:chris-lea/python-urllib3 && \
sudo apt-get update -yqq && \
sudo apt-get install -yqq python-urllib3 && \
sudo apt-get install -yqq git lsof strace ansible && \
sudo mkdir -p /home/vagrant/ansible/{roles,group_vars,inventory}
sudo chown -R vagrant:vagrant /home/vagrant/
cat << EOF > /home/vagrant/ansible/ansible.cfg
[defaults]
# Modern servers come and go too often for host key checking to be useful
roles_path = ./roles
system_errors = False
host_key_checking = False
ask_sudo_pass = False
retry_files_enabled = False
gathering = smart
force_handlers = True
[privilege_escalation]
# Nearly everything requires sudo, so default on
become = True
[ssh_connection]
# Speeds things up, but requires disabling requiretty in /etc/sudoers
pipelining = True
EOF
cat << EOF > /home/vagrant/ansible/playbook.yml
---
- hosts: all
  become: yes
  become_method: sudo
  vars:
    ulimit_config:
      - domain: '*'
        type: soft
        item: nofile
        value: 64000
      - domain: '*'
        type: hard
        item: nofile
        value: 64000
  roles:
    - role: ulimit
    - role: sysctl-performance
EOF
cat << EOF > /home/vagrant/ansible/hosts
localhost ansible_connection=local ansible_python_interpreter=/usr/bin/python2
EOF
cd /home/vagrant/ansible/roles && \
git clone https://github.com/KAMI911/ansible-role-sysctl-performance sysctl-performance && \
git clone https://github.com/picotrading/ansible-ulimit ulimit && \
cd /home/vagrant/ansible && \
ansible-playbook -i hosts playbook.yml && \
cd /home/vagrant && \
sudo chown -R vagrant:vagrant /home/vagrant/ && \
sudo touch /vagrant_bootstrap && \
sudo chown vagrant:vagrant /vagrant_bootstrap
SHELL

# Use old vb_xxx config variables when set
def vm_gui
  $vb_gui.nil? ? $vm_gui : $vb_gui
end

def vm_memory
  $vb_memory.nil? ? $vm_memory : $vb_memory
end

def vm_cpus
  $vb_cpus.nil? ? $vm_cpus : $vb_cpus
end

# ---------------------------------------------------------------------------------------

Vagrant.configure("2") do |config|

  config.ssh.insert_key = false

  config.vm.box = "ubuntu/trusty64"

  # enable hostmanager
  config.hostmanager.enabled = true

  # configure the host's /etc/hosts
  config.hostmanager.manage_host = true

  config.vm.hostname = VM_NODENAME

  # ssh
  config.ssh.max_tries = 40
  config.ssh.timeout   = 120

#   # Enable SSH agent forwarding for git clones
#   config.ssh.forward_agent = true

  config.vm.provider :virtualbox do |vb, override|
    # Give enough horsepower to build without taking all day.
    # NOTE: uart1: serial port
    # INFO: http://wiki.openpicus.com/index.php/UART_serial_port
    vb.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
    # INFO: --uartmode<1-N> <arg>: This setting controls how VirtualBox connects a given virtual serial port (previously configured with the --uartX setting, see above) to the host on which the virtual machine is running. As described in detail in Section 3.10, “Serial ports”, for each such port, you can specify <arg> as one of the following options:
    # SOURCE: https://www.virtualbox.org/manual/ch08.html
    vb.customize ["modifyvm", :id, "--uartmode1", serialFile]
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
    vb.customize ["modifyvm", :id, "--chipset", "ich9"]
    vb.customize ["modifyvm", :id, "--memory", "2048"]
    vb.customize ["modifyvm", :id, "--cpus", "2"]

    ip = "172.17.10.101"
    config.vm.network :private_network, ip: ip
  end

  # *****************
  $forwarded_ports.each do |guest, host|
    config.vm.network "forwarded_port", guest: guest, host: host, auto_correct: true
  end

  config.vm.provider :virtualbox do |vb|
    vb.gui = vm_gui
    vb.memory = vm_memory
    vb.cpus = vm_cpus
  end

  # config.vm.network "private_network", ip: box_ip

  # # set auto_update to false, if you do NOT want to check the correct
  # # additions version when booting this machine
  # config.vbguest.auto_update = true

  # # do NOT download the iso file from a webserver
  # config.vbguest.no_remote = false

  # FIXME: Set this to a real path
  #   public_key = ENV['HOME'] + '/dev/vagrant-box/fedora/keys/vagrant.pub'

  config.vm.provision :shell, inline: $docker_script

  # shared folder setup
  config.vm.synced_folder ".", "/home/vagrant/boss-ansible-role-common"

  # copy private key so hosts can ssh using key authentication (the script below sets permissions to 600)
  config.vm.provision :file do |file|
    file.source      = './keys/vagrant_id_rsa'
    file.destination = '/home/vagrant/.ssh/id_rsa'
  end

  # fix permissions on private key file
  config.vm.provision :shell, inline: $fix_perm
  # ******************

  config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbook.yml"
      ansible.verbose = "-v"
      ansible.sudo = true
      ansible.host_key_checking = false
      ansible.limit = 'all'
      # ansible.inventory_path = "provisioning/inventory"
      ansible.inventory_path = "ubuntu-inventory"
      # ansible.sudo = true
      # ansible.extra_vars = {
      #   public_key: public_key
      # }
      # Prevent intermittent connection timeout on ssh when provisioning.
      # ansible.raw_ssh_args = ['-o ConnectTimeout=120']
      # gist: https://gist.github.com/phantomwhale/9657134
      # ansible.raw_arguments = Shellwords.shellsplit(ENV['ANSIBLE_ARGS']) if ENV  ['ANSIBLE_ARGS']
      # CLI command.
      # ANSIBLE_ARGS='--extra-vars "some_var=value"' vagrant up
  end  # config.vm.provision "ansible" do |ansible|

  ansible_inventory_dir = "ansible/hosts"

end

# ---------------------------------------------------------------------------------------
