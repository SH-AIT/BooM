mkdir -p /home/eulercopilot/

echo "necessary tools"
yum install -y sshpass rsync docker
yum install -y vim unzip which initscripts coreutils findutils gawk e2fsprogs util-linux net-tools pciutils gcc g++ make automake autoconf libtool git dkms dpkg python3-pip kernel-headers-$(uname -r) kernel-devel-$(uname -r) &

echo "docker preload image"
mkdir -p ~/.ssh && touch ~/.ssh/known_hosts
ssh-keyscan 192.168.30.50 >> ~/.ssh/known_hosts
mkdir -p /home/eulercopilot/docker-images
sshpass -p 'DELL@Sairi123' rsync -av --progress nv@192.168.30.50:/home/nv/eulercopilot/docker-images/intelligence_boom_0.1.0-offline.tar.gz /home/eulercopilot/docker-images/intelligence_boom_0.1.0-offline.tar.gz
docker load -i /home/eulercopilot/docker-images/intelligence_boom_0.1.0-offline.tar.gz &

echo "install npu drivers"
mkdir -p /home/eulercopilot/npu-driver
sshpass -p 'DELL@Sairi123' rsync -av --progress nv@192.168.30.50:/home/nv/eulercopilot/npu-driver/ /home/eulercopilot/npu-driver/
groupadd HwHiAiUser
useradd -g HwHiAiUser -d /home/HwHiAiUser -m HwHiAiUser -s /bin/bash
( /home/eulercopilot/npu-driver/Ascend-hdk-310p-npu-driver_25.2.0_linux-aarch64.run --full --install-for-all && /home/eulercopilot/npu-driver/Ascend-hdk-310p-npu-firmware_7.7.0.6.236.run --full )  &

echo "copy other files"
sshpass -p 'DELL@Sairi123' rsync -av --progress nv@192.168.30.50:/home/nv/eulercopilot/ /home/eulercopilot/

echo "network setting"
grep -q "BOOTPROTO=dhcp" /etc/sysconfig/network-scripts/ifcfg-enp125s0f0 && \
sed -i '/BOOTPROTO=dhcp/s/dhcp/static/' /etc/sysconfig/network-scripts/ifcfg-enp125s0f0 && \
echo -e "IPADDR=192.168.30.56\nNETMASK=255.255.255.0\nGATEWAY=192.168.30.1\nDNS1=114.114.114.114\nDNS2=8.8.8.8" >> /etc/sysconfig/network-scripts/ifcfg-enp125s0f0

echo "install oedp"
yum localinstall -y /home/eulercopilot/tools/oedp-1.0.1-1.oe2503.aarch64.rpm

echo "set hostname which identical with LLM depoly all.children.masters.hosts"
hostnamectl set-hostname master1

echo "done, reboot required!"
sync
