# MindSpore-intelligence部署脚本

本部署脚本用于自动化部署 vllm+mindspore部署DeepSeek R1&V3 + openEuler Intelligence。脚本采用Shell + Python语言编写，涵盖了从镜像拉取、依赖安装、k3s部署、Ollama部署、DeepSeek 部署、Embeddings部署，数据库安装、Authhub安装、openEuler Intelligence安装的完整流程，已实现一键式部署和分布部署，旨在简化部署过程，提高部署效率和准确性。

### 1. 环境要求
1. **操作系统**：OpenEuler22.03 LTS SP4及以上要求
2. **软件依赖**：
    - `docker`：大模型镜像下载，容器管理；
    - `Python3`：用于脚本执行；
    - `oedp`：应用快速安装部署平台；
    - `k3s`:: 提供轻量级 Kubernetes 集群
    - `helm`: Kubernetes 包管理工具

### 2. 脚本执行
参考mindspore-deepseek项目下的DeepSeekV3&R1部署指南-第四章节配置config.yaml后执行

```bash
cd mindspore-intelligence/script
bash deploy.sh
# 选择0开启一键式部署
```

### 3. FAQ

1.下载的权重是CKPT格式的，脚本中默认是safetensor格式，如何修改？

```shell
# 修改config.yaml 模型权重类型
model_type: ckpt
```

