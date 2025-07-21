#!/bin/bash
current_path=$(
    cd $(dirname $0/)
    pwd
)
ENV_FILE=/root/.bashrc
source $current_path/config.cfg
source $ENV_FILE

master_ip="$1"

if [ "$2" ]; then
    #从节点
    headless="--headless"
    RANK_START=2
else
    #主节点
    headless=""
    RANK_START=0
fi

if [ $NODE_NUM -eq 2 ]; then
    PARALLEL=16
elif [ $NODE_NUM -eq 4 ]; then
    PARALLEL=32
fi

#拉起服务
rm -rf ds.log
if [ $NODE_NUM -ne 1 ]; then
    nohup vllm-mindspore serve --model="$MODEL_PATH" --port=$LLM_PORT --trust_remote_code --max-num-seqs=512 --max_model_len=32768 --max-num-batched-tokens=4096 --block-size=128 --gpu-memory-utilization=0.93 --tensor-parallel-size 4 --data-parallel-size 4 --data-parallel-size-local 2 $headless --data-parallel-start-rank $RANK_START --data-parallel-address $master_ip --data-parallel-rpc-port $DP_PORT --enable-expert-parallel &> ds.log &
else
    nohup python3 -m vllm_mindspore.entrypoints vllm.entrypoints.openai.api_server --model "$MODEL_PATH" --port=$LLM_PORT --trust_remote_code --tensor_parallel_size=8 --max-num-seqs=192 --max_model_len=32768 --max-num-batched-tokens=16384 --block-size=32 --gpu-memory-utilization=0.93 &> ds.log &
fi