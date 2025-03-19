#!/bin/bash

# 各个节点均执行

# 下载依赖
PKG_LIST="unzip which initscripts coreutils findutils gawk e2fsprogs util-linux net-tools pciutils gcc make automake autoconf libtool git patch kernel-devel-$(uname -r) kernel-headers-$(uname -r) dkms"

for pkg in $PKG_LIST; do
    if ! rpm -q "$pkg" > /dev/null 2>&1; then
        echo "安装 $pkg..."
        if ! yum -y install "$pkg"; then
            echo "安装 $pkg 失败"
        fi
    else
        echo "$pkg 已安装，跳过"
    fi
done

# 下载驱动
rm -rf npu-driver
mkdir -p npu-driver/hdk-install
wget -O npu-driver/driver.zip https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/Ascend%20HDK/Ascend%20HDK%2024.1.RC3/Ascend-hdk-910b-npu_24.1.rc3_linux-aarch64.zip

if [ $? -ne 0 ]; then
    echo "下载失败"
    exit 1
fi

# 解压驱动
cd npu-driver
unzip driver.zip
nested_zip=$(find . -name "*.zip" -not -path "./driver.zip" | head -n 1)
unzip -o "$nested_zip" -d "./hdk-install"

# 安装驱动
cd hdk-install
bash install.sh install all
if [ $? -ne 0 ]; then
    echo "hdk驱动&固件安装失败"
    exit 1
fi

echo "hdk驱动&固件安装成功!请重启机器生效"
