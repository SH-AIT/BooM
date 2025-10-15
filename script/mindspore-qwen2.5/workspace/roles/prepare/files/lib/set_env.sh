#!/bin/bash

# 各个节点的容器内均执行
current_path=$(
    cd $(dirname $0/)
    pwd
)
source $current_path/config.cfg

ENV_ARG='
# openeuler_qwen_env_config
export ASCEND_CUSTOM_PATH=$ASCEND_HOME_PATH/../
export MS_ENABLE_LCCL=off
export HCCL_OP_EXPANSION_MODE="AI_CPU"
export vLLM_MODEL_MEMORY_USE_GB=53
export MS_DEV_RUNTIME_CONF="parallel_dispatch_kernel:True"
export MS_ALLOC_CONF="enable_vmm:True"
export ASCEND_RT_VISIBLE_DEVICES=0,1,2
export ASCEND_TOTAL_MEMORY_GB=64
export HCCL_CONNECT_TIMEOUT=7200
export CPU_AFFINITY=0
export EXPERIMENTAL_KERNEL_LAUNCH_GROUP="thread_num:4,kernel_group_num:16"
export MS_INTERNAL_ENABLE_NZ_OPS="QuantBatchMatmul,MlaPreprocess,GroupedMatmulV4"
export PYTHONPATH=/workspace/mindformers:$PYTHONPATH
export MS_DISABLE_INTERNAL_KERNELS_LIST="AddRmsNorm,Add,MatMul,Cast"
'

ENV_FILE=/root/.bashrc
echo "$ENV_ARG" >> $ENV_FILE

source $ENV_FILE
