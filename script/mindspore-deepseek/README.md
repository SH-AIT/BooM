# MindSpore-DeepSeek部署脚本

本部署脚本用于自动化部署 vllm+mindspore部署DeepSeek R1&V3。脚本采用Python语言编写，涵盖了从镜像拉取、依赖安装、容器部署、服务拉起的完整流程，旨在简化部署过程，提高部署效率和准确性。

### 1. 环境要求
1. **操作系统**：OpenEuler22.03 LTS SP4及以上要求
2. **软件依赖**：
    - `docker`：镜像下载，容器管理；
    - `Python3`：用于脚本执行；
    - `oedp`：应用快速安装部署平台；

### 2. 脚本执行
参考该项目下的DeepSeekV3&R1部署指南-第四章节配置config.yaml后执行以下命令

```bash
oedp run install
```

### 3. FAQ

1.下载的权重是CKPT格式的，脚本中默认是safetensor格式，如何修改？

```shell
# 修改config.yaml 模型权重类型
model_type: ckpt
```

