mkdir /home/eulercopilot/

echo "necessary tools"
yum install -y vim unzip rsync which initscripts coreutils findutils gawk e2fsprogs util-linux net-tools pciutils gcc g++ make automake autoconf libtool git dkms dpkg python3-pip kernel-headers-$(uname -r) kernel-devel-$(uname -r) docker
wget https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/aarch64/Packages/oedp-1.0.1-1.oe2503.aarch64.rpm
yum localinstall -y oedp-1.0.1-1.oe2503.aarch64.rpm
sleep 1

echo "prepare for copy"
ssh-keyscan 192.168.30.50 >> ~/.ssh/known_hosts

echo "copy files"
sshpass -p 'DELL@Sairi123' rsync -av --progress nv@192.168.30.50:/home/nv//home/nv/eulercopilot/ /home/eulercopilot/

echo "docker preload image"
docker load -i /home/eulercopilot/docker-images/intelligence_boom_0.1.0-offline.tar

echo "install npu drivers"
groupadd HwHiAiUser
useradd -g HwHiAiUser -d /home/HwHiAiUser -m HwHiAiUser -s /bin/bash
/home/eulercopilot/npu-driver/Ascend-hdk-310p-npu-driver_25.2.0_linux-aarch64.run --full --install-for-all
/home/eulercopilot/npu-driver/Ascend-hdk-310p-npu-firmware_7.7.0.6.236.run --full

echo "network setting"
grep -q "BOOTPROTO=dhcp" /etc/sysconfig/network-scripts/ifcfg-enp125s0f0 && \
sed -i '/BOOTPROTO=dhcp/s/dhcp/static/' /etc/sysconfig/network-scripts/ifcfg-enp125s0f0 && \
echo -e "IPADDR=192.168.30.56\nNETMASK=255.255.255.0\nGATEWAY=192.168.30.1\nDNS1=114.114.114.114\nDNS2=8.8.8.8" >> /etc/sysconfig/network-scripts/ifcfg-enp125s0f0

echo "done, reboot required!"
sync
