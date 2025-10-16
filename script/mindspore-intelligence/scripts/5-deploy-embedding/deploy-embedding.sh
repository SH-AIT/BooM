#!/bin/bash
set -euo pipefail

# 颜色定义
RED='\e[31m'
GREEN='\e[32m'
YELLOW='\e[33m'
BLUE='\e[34m'
NC='\e[0m' # 重置颜色

# 配置参数
readonly MODEL_NAME="bge-m3"
readonly MODEL_FILE="bge-m3"
readonly TIMEOUT_DURATION=45
readonly MODEL_DIR="/home/eulercopilot/models"

# 初始化工作目录
readonly WORK_DIR=$(pwd)
mkdir -p "$MODEL_DIR"

create_model() {
    echo -e "${BLUE}正在创建模型容器...${NC}"
    
    # 检查容器是否已存在
    if docker ps -a | grep -q "mis-tei-bge-m3"; then
        echo -e "${YELLOW}发现已存在的容器，正在清理...${NC}"
        docker stop mis-tei-bge-m3 >/dev/null 2>&1 || true
        docker rm mis-tei-bge-m3 >/dev/null 2>&1 || true
        echo -e "${GREEN}旧容器清理完成${NC}"
    fi

    # 检查镜像是否存在
    if ! docker images | grep -q "ascendhub/mis-tei"; then
        echo -e "${YELLOW}正在拉取模型镜像...${NC}"
        docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:7.1.RC1-300I-Duo-aarch64
    fi

    # 启动Docker容器[7,8](@ref)
    echo -e "${BLUE}启动模型容器...${NC}"
    if docker run -itd \
        -u HwHiAiUser \
        -e ENABLE_BOOST=True \
        -e ASCEND_VISIBLE_DEVICES=2 \
        --name=mis-tei-bge-m3 \
        --net=host \
        -v /home/eulercopilot/models/:/home/HwHiAiUser/model \
        swr.cn-south-1.myhuaweicloud.com/ascendhub/mis-tei:7.1.RC1-300I-Duo-aarch64 \
        bge-m3 127.0.0.1 8080; then
        
        echo -e "${GREEN}✅ 模型容器启动成功${NC}"
        
        # 等待容器完全启动
        echo -e "${YELLOW}等待服务初始化（30秒）...${NC}"
        sleep 30
        
        # 检查容器状态
        if docker ps | grep -q "mis-tei-bge-m3"; then
            echo -e "${GREEN}✅ 容器运行状态正常${NC}"
            return 0
        else
            echo -e "${RED}❌ 容器启动后异常退出${NC}"
            docker logs mis-tei-bge-m3 --tail 20
            return 1
        fi
    else
        echo -e "${RED}❌ 容器启动失败${NC}"
        return 1
    fi
}


verify_deployment() {
    echo -e "${BLUE}验证部署结果...${NC}"
    local retries=30
    local wait_seconds=15
    local test_output=$(mktemp)
    local INTERVAL=5

    # 增强验证：通过API获取嵌入向量
    echo -e "${YELLOW}执行API测试（最多尝试${retries}次）...${NC}"
    for ((i=1; i<=retries; i++)); do
        local http_code=$(curl -k -o /dev/null -w "%{http_code}" -X POST http://localhost:8080/v1/embeddings \
            -H "Content-Type: application/json" \
            -d '{"input": "The food was delicious and the waiter...", "model": "bge-m3", "encoding_format": "float"}' -s -m $TIMEOUT_DURATION)

        if [[ "$http_code" == "200" ]]; then
            echo -e "${GREEN}[SUCCESS] API测试成功（HTTP状态码：200）${NC}"
            return 0
        else
            echo -e "${YELLOW}[WARNING] 第${i}次尝试失败（HTTP状态码：${http_code}）${NC}"
            sleep $INTERVAL
        fi
    done

    echo -e "${RED}[ERROR] API测试失败，已达到最大尝试次数${NC}"
    exit 1
}

### 主执行流程 ###
echo -e "${BLUE}=== 开始模型部署 ===${NC}"
{
    create_model
    verify_deployment
}
echo -e "${BLUE}=== 模型部署成功 ===${NC}"
