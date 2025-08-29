# DeepSeek-V3&R1-300IDuo-部署指南

## 1. 硬件要求及组网
本文以DeepSeek-R1为主进行介绍，DeepSeek-V3与R1的模型结构和参数量一致，部署方式与R1相同。

部署DeepSeek-R1量化模型（A8W8）至少需要3台Atlas 300I Duo 四卡八芯（8\*48G）服务器。

部署DeepSeek-R1量化模型（A8W4）至少需要2台Atlas 300I Duo 四卡八芯（8\*48G）服务器。

组网结构推荐使用npu直连模式，即两台服务器的**所有npu卡通过交换机连接，网络端口UP**



## 2. 模型权重获取

| 序号 | 检查项                   | 详细说明                                                     |
| ---- | ------------------------ | ------------------------------------------------------------ |
| 2.A  | 模型权重存储空间         |  下载A8W4/A8W8权重时，需确保机器内/挂载盘中有大于400G/700G的存储空间。  |
| 2.B  | CPU侧内存                | 需确保CPU侧内存能够放下对应权重。<br>例：A8W8权重需要大约500G左右的内存，可通过free -h指令查看空闲cpu内存。<br>计算方式：free_mem >= (权重大小 / 机器数) * 1.3 （该计算方式待验证，但需要确保内存足够） |
| 2.C  | 根据权重大小选择推理卡数 | A8W8至少需要3台300I Duo 四卡八芯机器。                               |
| 2.D  | 权重正确性检查           | 请确保权重的正确性，对比权重/tokenizer等文件与源文件的MD5或SHA256值。 |

### 2.1 量化模型权重下载

 A8W4：modelers.cn   [MindSpore-Lab/DeepSeek-R1-W8A4 \| 魔乐社区](https://modelers.cn/models/MindSpore-Lab/R1-A8W4) 

 A8W8：modelers.cn   [MindSpore-Lab/DeepSeek-R1-A8W8 \| 魔乐社区](https://modelers.cn/models/MindSpore-Lab/DeepSeek-R1-W8A8)



#### 2.1.1 权重放置【重要】

所有机器均需要放置权重，且放置在相同路径下。该路径后续需作为配置项，填写进一键部署脚本的配置文件中(见4.1章节)。

例如: 主节点模型权重放置在/home/ds/deepseek-r1下，从节点也需放置在/home/ds/deepseek-r1

##### 注意事项：
* 由于300IDuo不支持bfloat16的数据格式，将 `/home/ds/deepseek-r1/config.json` 中torch dtype设置成float16： `"torch_dtype": "float16",`


## 3. 驱动&固件准备

### 3.1 推荐版本

| 部件                | 社区版      |
| ------------------- | ----------- |
| Ascend HDK Driver   | 24.1.rc3    |
| Ascend HDK Firmware | 7.5.0.1.129 |

#### 3.1.1 hdk下载方式

**社区版本下载链接**：https://www.hiascend.com/hardware/firmware-drivers/community?product=4&model=32&cann=8.0.0.alpha002&driver=1.0.RC2

该版本要求内核版本为5.10，安装前校验内核版本

```shell
# 可以使用如下命令获取环境上的驱动&固件版本信息
npu-smi info -t board -i 1 | egrep -i "software|firmware"
```

![image-20250318153035798](./asserts/image1.png)

注意：在安装驱动和固件时，需要提前安装kernel-devel和kernel-headers包，且确保版本和服务器内核的版本保持一致

```shell
# 安装kernel-devel & kernel-headers
yum install -y kernel-devel-$(uname -r) kernel-headers-$(uname -r)
```



#### 3.1.2 驱动&固件安装

环境上没有昇腾驱动&固件，首次安装可采用以下方式：

```shell
# 方式1：
# 驱动安装
./Ascend-hdk-<chip_type>-npu-driver_<version>_linux-<arch>.run --full --install-for-all
# 固件安装
./Ascend-hdk-<chip_type>-npu-firmware_<version>.run --full

# 方式2：需先下载部署插件包，该脚本在插件包内。参考4.1章节
sh mindspore-deepseek/workspace/roles/prepare/files/lib/ascend_prepare.sh
# 安装后需要重启
```

环境已有昇腾驱动&固件可跳过该步骤


## 4. 部署步骤


### 拉取镜像

```shell
# aarch64
docker pull hub.oepkgs.net/oedeploy/openeuler/aarch64/intelligence_boom:0.1.0-aarch64-300I-Duo-mindspore2.7-openeuler24.03-lts-sp2

# x86_64
docker pull hub.oepkgs.net/oedeploy/openeuler/x86_64/intelligence_boom:0.1.0-x86_64-300I-Duo-mindspore2.7-openeuler24.03-lts-sp2
```

### 启动镜像
 
假设您的NPU设备安装在/dev/davinci[0-7]上，并且您的NPU驱动程序安装在/usr/local/Ascend上：

```shell
docker run -it -u root --name=deepseek-r1-671b --net=host --ipc=host --privileged=true \
    --device=/dev/davinci0 \
    --device=/dev/davinci1 \
    --device=/dev/davinci2 \
    --device=/dev/davinci3 \
    --device=/dev/davinci4 \
    --device=/dev/davinci5 \
    --device=/dev/davinci6 \
    --device=/dev/davinci7 \
    --device=/dev/davinci_manager \
    --device=/dev/devmm_svm \
    --device=/dev/hisi_hdc \
    -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
    -v /usr/local/Ascend/add-ons/:/usr/local/Ascend/add-ons/ \
    -v /usr/local/sbin/:/usr/local/sbin/ \
    -v /var/log/npu/slog/:/var/log/npu/slog \
    -v /var/log/npu/profiling/:/var/log/npu/profiling \
    -v /var/log/npu/dump/:/var/log/npu/dump \
    -v /var/log/npu/:/usr/slog \
    -v /etc/hccn.conf:/etc/hccn.conf \
    hub.oepkgs.net/oedeploy/openeuler/aarch64/intelligence_boom:0.1.0-aarch64-300I-Duo-mindspore2.7-openeuler24.03-lts-sp2 \
    /bin/bash
```
### 服务化部署
镜像内已预置了部署脚本:

```
1. 在主节点上运行`source env_main.sh`, 从节点上`source env_sub.sh`设置环境变量。(修改ray启动的ip地址为实际的ip地址）

2. 运行`bash run_vllm.sh`一键启动deepseek服务。(将脚本中启动参数的权重地址修改为实际地址）
```

**脚本内容与启动参赛说明见附录**

## 5. 服务化测试

### 5.1 使用Benchmark测试【容器内】

使用ascend-vllm性能测试工具

```shell
python benchmark_parallel.py --backend openai --host [主节点IP] --port [服务端口] --tokenizer [模型路径] --epochs 1 --parallel-num 192 --prompt-tokens 256 --output-tokens 256
```

注意: --tokenizer指定的模型路径，要和启动推理服务时的model_path一模一样

也可使用vllm开源的性能测试工具

<https://github.com/vllm-project/vllm/tree/main/benchmarks>

### 5.2 使用curl请求测试

 Deepseek-R1请求样例（**请按照配置的LLM_PORT变量调整请求端口**）

```cpp
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/home/ds/deepseek-r1",
    "prompt": "Mindspore is",
    "max_tokens": 120,
    "temperature": 0
  }'
```
#### 注意：

**目前还不支持设置seed，可能会导致服务崩溃**

## 6. FAQ

### 6.1 安装ascend驱动时显示Decompression fail

缺少tar命令，需安装tar包


### 6.2 运行部署时显示空间不足

> ![](./asserts/image10.png)

请确保各个节点根目录有足够空间


## 附录

### vllm-mindspore部分启动参数说明：

| **启动参数**                                        | **功能说明**                    |
| --------------------------------------------------- | ------------------------------- |
| /home/ckpt/qwen2.5-14B/                             | 权重地址                    |
| trust_remote_code                         | 允许执行模型的自定义代码                    |
| tensor_parallel_size                      | tp并行数量设置        |
| max-num-seqs                         | 最大同时处理的输入batch数量                    |
| block-size | kvcache每个block的大小                        |
| gpu-memory-utilization                    | 模型占用的gpu内存大小                        |
| max-num-batched-tokens           | 最大能同时处理的token数量            |
| max-model-len                        | 单个输入最大的token数量                     |

