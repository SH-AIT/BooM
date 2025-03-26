#!/bin/bash
current_path=$(
    cd $(dirname $0/)
    pwd
)
source $current_path/lib/config.cfg

cp_into_container() {
    docker cp $current_path/lib $CONTAINER_NAME:/workspace
}

main() {
    set -e
    chmod -R +x $current_path/lib

    systemctl stop firewalld
    systemctl stop iptables

    # 1. 启动Docker容器并复制文件
    $current_path/lib/start_docker.sh
    cp_into_container

    # 2. 执行组网检查
    if [ $NODE_NUM -ne 1 ]; then
        $current_path/lib/net_check.sh
    fi

    #进入容器执行
    # 3. 设置容器内环境变量
    docker exec -it $CONTAINER_NAME /workspace/lib/set_env.sh

    # 4. 进行绑核
    pip show psutil
    if [ $? -ne 0 ]; then
        pip install psutil
    fi
    python3 $current_path/lib/fine-grainded-bind.py
    if [ $? -ne 0 ]; then
        echo "细粒度线程绑核失败，请确保驱动版本>=24.1.0"
        exit 1
    fi

}

# 执行主函数
main "$@"
