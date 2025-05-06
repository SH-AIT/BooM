#!/bin/bash
current_path=$(
    cd $(dirname $0/)
    pwd
)
ENV_FILE=/root/.bashrc
source $current_path/config.cfg
source $ENV_FILE
# 仅主节点运行

#检测推理服务是否拉起
llm_status=0
for i in {1..7200}; do
    netstat -ntlp | grep $LLM_PORT
    if [ $? -eq 0 ]; then
        echo "推理服务已拉起，端口$LLM_PORT已打开"
        llm_status=1
        break
    fi
    sleep 1
done

if [ $llm_status -eq 0 ]; then
    echo "推理服务拉起超时，请手动确认"
    exit 1
fi