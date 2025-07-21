#!/bin/bash
current_path=$(
    cd $(dirname $0/)
    pwd
)
ENV_FILE=/root/.bashrc
source $current_path/config.cfg
source $ENV_FILE

ray_start() {

    ps -ef | grep "python" | grep -v grep | awk '{print $2}' | xargs kill
    if [ $NODE_NUM -eq 1 ]; then
        echo "单机部署无需启动ray"
        return
    fi
    ray stop

    if [ "$1" ]; then
        # 从节点
        nohup ray start --address=$1:$RAY_PORT &
        sleep 5
        if [ $NODE_NUM -eq 2 ]; then
            NPU_NUM=16.0
        elif [ $NODE_NUM -eq 4 ]; then
            NPU_NUM=32.0
        fi

        ray_status=0
        for i in {1..10}; do
            ray status | grep "$NPU_NUM NPU"
            if [ $? -eq 0 ]; then
                echo "ray集群已全部拉起"
                ray_status=1
                break
            fi
            sleep 3
        done

        if [ $ray_status -eq 0 ]; then
            echo "ray集群超时"
            exit 1
        fi
    else
        # 主节点
        nohup ray start --head --include-dashboard=False --port=$RAY_PORT &
        sleep 5
        for i in {1..10}; do
            ray status | grep '8.0 NPU'
            if [ $? -eq 0 ]; then
                echo "主节点ray已启动"
                break
            fi
            sleep 3
        done
    fi
    echo "ray 已在后台运行"
}

ray_start "$@"
