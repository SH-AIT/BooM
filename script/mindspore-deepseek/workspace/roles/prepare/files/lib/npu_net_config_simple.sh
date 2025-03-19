#!/bin/bash
# 简易辅助脚本，仅配置npu的ip
# sh npu_set_config_simple.sh 1

net_config() {
    if [ "$1" ]; then
        for i in {0..7}; do
            hccn_tool -i $i -ip -s address 10.10.0.$1$i netmask 255.255.0.0
        done
    else
        echo "请输入节点id,从1开始,会使用节点id设置对应的ip地址"
        echo "npu会设置ip为10.10.0.{节点}{npu卡id},例如:"
        echo "sh npu_set_config_simple.sh 1"
        echo "该样例中节点id为1, 卡id为0-7"
        echo "设置ip为10.10.0.10 ~ 10.10.0.17"
        exit 1
    fi
    # 检查IP信息
    for i in {0..7}; do
        hccn_tool -i $i -ip -g
    done
    echo "npu卡ip配置完成"
}

net_config "$@"
