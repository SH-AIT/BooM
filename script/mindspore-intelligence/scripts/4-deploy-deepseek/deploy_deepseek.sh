#!/bin/bash
set -euo pipefail

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 重置颜色

# 全局变量
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly MINDSPORE_QWEN_DIR="${SCRIPT_DIR}/../../../mindspore-qwen2.5"
readonly CONFIG_FILE="${MINDSPORE_QWEN_DIR}/config.yaml"
readonly YAML_EXTRACTOR="${SCRIPT_DIR}/yaml_extractor.py"
readonly TIMEOUT_DURATION=45

# 从配置文件中获取参数
function get_config_value() {
    local key="$1"
    if [ ! -f "$YAML_EXTRACTOR" ]; then
        echo -e "${RED}错误: YAML解析脚本不存在: $YAML_EXTRACTOR${NC}"
        return 1
    fi
    python3 "$YAML_EXTRACTOR" -f "$CONFIG_FILE" -k "$key"
}

# 检查命令是否存在
function check_command() {
    local cmd=$1
    if ! command -v "$cmd" &> /dev/null; then
        echo -e "${RED}命令未安装: $cmd${NC}"
        return 1
    fi
    echo -e "${GREEN}命令已安装: $cmd${NC}"
    return 0
}

# 检查目录是否存在
function check_directory() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        echo -e "${RED}目录不存在: $dir${NC}"
        return 1
    fi
    echo -e "${GREEN}目录存在: $dir${NC}"
    return 0
}

# 检查文件是否存在
function check_file() {
    local file=$1
    if [ ! -f "$file" ]; then
        echo -e "${RED}文件不存在: $file${NC}"
        return 1
    fi
    echo -e "${GREEN}文件存在: $file${NC}"
    return 0
}

# 安装qwen
function install_qwen() {
    local install_dir=$1
    echo -e "${YELLOW}执行: oedp run install -p $install_dir${NC}"
    
    if oedp run install -p "$install_dir"; then
        echo -e "${GREEN}qwen安装成功${NC}"
        return 0
    else
        echo -e "${RED}qwen安装失败${NC}"
        return 1
    fi
}

# 验证部署结果
function verify_deployment() {
    echo -e "${BLUE}步骤4/4：验证部署结果...${NC}"
    
    # 从配置文件获取参数
    local IP=$(get_config_value "all.children.masters.hosts.master1.ansible_host")
    local PORT=$(get_config_value "all.vars.llm_port")
    local MODEL_NAME=$(get_config_value "all.vars.model_path")
    
    # 验证参数获取
    if [ -z "$IP" ] || [ -z "$PORT" ] || [ -z "$MODEL_NAME" ]; then
        echo -e "${RED}从配置文件获取参数失败${NC}"
        echo -e "${YELLOW}请检查以下配置项:"
        echo "1. all.children.masters.hosts.master1.ansible_host"
        echo "2. all.vars.llm_port"
        echo "3. all.vars.model_path"
        return 1
    fi
    
    echo -e "${GREEN}获取配置参数成功:"
    echo "IP: $IP"
    echo "PORT: $PORT"
    echo "MODEL_NAME: $MODEL_NAME${NC}"
    
    # 检查jq命令
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}注意：jq未安装，响应解析可能受限${NC}"
    fi

    local retries=3
    local interval=5
    local attempt=1

    echo -e "${YELLOW}执行API测试（超时时间${TIMEOUT_DURATION}秒）...${NC}"

    while [ $attempt -le $retries ]; do
        echo -e "${BLUE}尝试 $attempt: 发送测试请求...${NC}"

        response=$(timeout ${TIMEOUT_DURATION} curl -s http://$IP:$PORT/v1/chat/completions \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer sk-123456" \
            -d '{
                "model": "'"${MODEL_NAME}"'",
                "messages": [
                    {"role": "system", "content": "你是一个AI助手"},
                    {"role": "user", "content": "你好，请说一首中文古诗"}
                ],
                "stream": false
            }' 2>&1)

        if [[ $? -eq 0 ]] && [[ -n "$response" ]]; then
            echo -e "${GREEN}测试响应成功，收到有效输出："
            if command -v jq &> /dev/null && jq -e .choices[0].message.content <<< "$response" &> /dev/null; then
                jq .choices[0].message.content <<< "$response"
            else
                echo "$response"
            fi
            return 0
        else
            echo -e "${YELLOW}请求未得到有效响应，重试中...${NC}"
            ((attempt++))
            sleep $interval
        fi
    done

    echo -e "${RED}验证失败：经过 ${retries} 次重试仍未收到有效响应${NC}"
    return 1
}

# 主函数
function main() {
    echo -e "${BLUE}=== 开始安装流程 ===${NC}"

    echo $SCRIPT_DIR
    echo $MINDSPORE_QWEN_DIR
    
    # 步骤0：检查必要文件
    echo -e "${BLUE}步骤0/4：检查必要文件...${NC}"
    check_file "$YAML_EXTRACTOR" || exit 1
    check_file "$CONFIG_FILE" || exit 1
    
    # 步骤1：检查oedp工具
    echo -e "${BLUE}步骤1/4：检查oedp工具...${NC}"
    check_command "oedp" || {
        echo -e "${YELLOW}可能原因："
        echo "1. 未安装oedp工具"
        echo "2. PATH环境变量未包含oedp路径"
        echo -e "3. 工具安装不完整${NC}"
        exit 1
    }
    
    # 步骤2：检查mindspore-qwen2.5目录
    echo -e "${BLUE}步骤2/4：检查mindspore-qwen2.5目录...${NC}"
    check_directory "$MINDSPORE_QWEN_DIR" || {
        echo -e "${YELLOW}可能原因："
        echo "1. 项目未正确克隆"
        echo "2. 当前工作目录错误"
        echo -e "3. 目录路径配置错误${NC}"
        exit 1
    }
    
    # 步骤3：安装qwen
    echo -e "${BLUE}步骤3/4：安装qwen...${NC}"
    install_qwen "$MINDSPORE_QWEN_DIR" || {
        echo -e "${YELLOW}可能原因："
        echo "1. 安装脚本执行失败"
        echo "2. 依赖项缺失"
        echo -e "3. 权限不足${NC}"
        exit 1
    }
    
    # 步骤4：验证部署结果
    verify_deployment || {
        echo -e "${YELLOW}可能原因："
        echo "1. 服务未启动"
        echo "2. 配置参数错误"
        echo "3. 模型未正确加载"
        echo "4. 网络连接问题"
        echo -e "5. API请求格式错误${NC}"
        exit 1
    }
    
    echo -e "${GREEN}=== 所有步骤已完成 ===${NC}"
    
    # 使用说明
    local IP=$(get_config_value "all.children.masters.hosts.master1.ansible_host")
    local PORT=$(get_config_value "all.vars.llm_port")
    local MODEL_NAME=$(get_config_value "all.vars.model_path")
    
    echo -e "${YELLOW}使用说明：${NC}"
    echo -e "${BLUE}API访问示例：${NC}"
    cat <<EOF
curl http://$IP:$PORT/v1/chat/completions \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer sk-123456" \\
-d '{
    "model": "$MODEL_NAME",
    "messages": [
        {"role": "system", "content": "你是一个AI助手"},
        {"role": "user", "content": "你好"}
    ],
    "stream": false,
    "n": 1,
    "max_tokens": 2048
}'
EOF
}

# 执行主函数
main "$@"