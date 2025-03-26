#!/bin/bash

# 各个节点的容器内均执行
current_path=$(
    cd $(dirname $0/)
    pwd
)
source $current_path/config.cfg

ENV_ARG='
# openeuler_deepseek_env_config
export ASCEND_CUSTOM_PATH=$ASCEND_HOME_PATH/../
export MS_ENABLE_LCCL=off
export HCCL_OP_EXPANSION_MODE=AIV
export vLLM_MODEL_BACKEND=MindFormers
export vLLM_MODEL_MEMORY_USE_GB=53
export MS_DEV_RUNTIME_CONF="parallel_dispatch_kernel:True"
export MS_ALLOC_CONF="enable_vmm:True"
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export ASCEND_TOTAL_MEMORY_GB=64
export HCCL_CONNECT_TIMEOUT=7200
export MS_COMPILER_CACHE_ENABLE=1
export CPU_AFFINITY=0
'

NET_ENV="
export GLOO_SOCKET_IFNAME=$RAY_DEVICE
export TP_SOCKET_IFNAME=$RAY_DEVICE
export HCCL_SOCKET_IFNAME=$RAY_DEVICE
"

if [ $NODE_NUM -eq 1 ]; then
    YAML_FILE='/usr/local/Python-3.11/lib/python3.11/site-packages/research/deepseek3/deepseek_r1_671b/predict_deepseek_r1_671b_w8a8.yaml'
    cat $YAML_FILE | grep gptq-pergroup
    if [ $? -ne 0 ]; then
        sed -e 's/model_parallel:.*/model_parallel: 8/' -i $YAML_FILE
        sed -e "s/quant_method:.*/quant_method: 'gptq-pergroup'/" -i $YAML_FILE
        sed -e 's/weight_dtype/#weight_dtype/' -i $YAML_FILE
        sed -e 's/activation_dtype/#activation_dtype/' -i $YAML_FILE
    fi
elif [ $NODE_NUM -eq 2 ]; then
    YAML_FILE='/usr/local/Python-3.11/lib/python3.11/site-packages/research/deepseek3/deepseek_r1_671b/predict_deepseek_r1_671b_w8a8.yaml'
elif [ $NODE_NUM -eq 4 ]; then
    YAML_FILE='/usr/local/Python-3.11/lib/python3.11/site-packages/research/deepseek3/deepseek_r1_671b/predict_deepseek_r1_671b.yaml'
fi

# 修改权重类型
sed -e 's/^load_ckpt_format.*/load_ckpt_format: "'$MODEL_TYPE'"/' -i $YAML_FILE
sed -e 's/^auto_trans_ckpt.*/auto_trans_ckpt: False/' -i $YAML_FILE

YAML_ENV="export MINDFORMERS_MODEL_CONFIG=$YAML_FILE"

ENV_FILE=/root/.bashrc

if grep -q "openeuler_deepseek_env_config" /root/.bashrc; then
    echo "存在已配置的环境变量，详见容器内/root/.bashrc"
    exit 0
fi

echo "$ENV_ARG" >> $ENV_FILE
echo "$YAML_ENV" >> $ENV_FILE
if [ $NODE_NUM -ne 1 ]; then
    echo "$NET_ENV" >> $ENV_FILE
fi
source $ENV_FILE
