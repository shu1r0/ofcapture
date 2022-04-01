# vm name 
$name = "ofcapture-dev"

# ------------------------------------------------------------
# Description
# ------------------------------------------------------------
$description = <<'EOS'
VM for testing ofcapture

user: vagrant
password: vagrant
EOS


# ------------------------------------------------------------
# install basic package
# ------------------------------------------------------------
$install_package = <<'SCRIPT'
# install package
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install build-essential
sudo apt-get -y install python3-pip
sudo apt-get -y install sshpass
sudo apt-get -y install python3.8-dev python3.8

# python upgrade
# update-alternatives causes a bug
# sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 20
# sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 10
# sudo alternatives --auto python3

python3.8 -m pip install -U pip
sudo apt-get -y remove python-pexpect python3-pexpect

sudo apt-get -y install libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev
sudo apt-get -y install git
sudo apt-get -y install curl
sudo apt-get -y install wireshark-dev

#NOTE: Should is used venv???
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade pexpect
sudo pip3 install --upgrade lxml
sudo pip3 install grpcio-tools
sudo pip3 install mininet
sudo pip3 install aiohttp
sudo pip3 install python-socketio
sudo pip3 install python-openflow
sudo pip3 install flask
sudo pip3 install macaddress

sudo apt install -y --reinstall python3.8
SCRIPT

# ------------------------------------------------------------
# install Vue 3
# 
# References:
#    - https://linuxize.com/post/how-to-install-node-js-on-ubuntu-20-04/
# ------------------------------------------------------------
$install_vue = <<'SCRIPT'
sudo curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt install -y nodejs

sudo chown -R vagrant /usr/lib/node_modules/
sudo npm install -g n
sudo npm install -g @vue/cli

sudo n install 10.16.0
SCRIPT


# ------------------------------------------------------------
# install mininet
# ------------------------------------------------------------
$install_mininet = <<'SCRIPT'
cd module
git clone git://github.com/mininet/mininet
cd mininet
# git tag  # list available versions
git checkout -b mininet-2.3.0 2.3.0  # or whatever version you wish to install
cd ..
# mininet/util/install.sh -n3fw
mininet/util/install.sh -a

sudo apt-get -y install openvswitch-switch
sudo service openvswitch-switch start
SCRIPT

# ------------------------------------------------------------
# install ryu 
# Libraries dependent on ryu are added here as required
# ------------------------------------------------------------
$install_ryu = <<'SCRIPT'
sudo apt install -y python3-ryu
SCRIPT


# ------------------------------------------------------------
# # vagrant configure version 2
# ------------------------------------------------------------
VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    # vm name
    config.vm.hostname = $name + '.localhost'
    # ubuntu image
    config.vm.box = 'bento/ubuntu-18.04'
    # config.vm.box = 'bento/ubuntu-16.04'

    # network
    config.vm.network 'private_network', ip: '10.0.0.100'
    # port for web server
    config.vm.network 'forwarded_port', guest: 8080, host: 8080
    # port for websocket
    config.vm.network 'forwarded_port', guest: 8889, host: 8889

    # share directory
    config.vm.synced_folder './', '/home/vagrant/ofcapture'

    # install package
    config.vm.provision 'shell', inline: $install_package
    config.vm.provision 'shell', inline: $install_mininet
    config.vm.provision 'shell', inline: $install_ryu
    config.vm.provision 'shell', inline: $install_vue
    # config.vm.provision 'shell', inline: $install_onos


    # ssh config
    # config.ssh.username = 'vagrant'
    # config.ssh.password = 'vagrant'
    # config.ssh.insert_key = false

    # config.vbguest.auto_update = false

    # config virtual box
    config.vm.provider "virtualbox" do |vb|
        vb.name = $name
        vb.gui = true

        vb.cpus = 2
        vb.memory = "2048"
    
        vb.customize [
            "modifyvm", :id,
            "--vram", "16",
            "--clipboard", "bidirectional",
            "--ioapic", "off",
            "--pae", "off",
            "--accelerate3d", "off",
            "--description", $description,
        ]
    end
end