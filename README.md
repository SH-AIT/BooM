# openEuler开源全栈AI推理解决方案（Intelligence BooM）

**如果您的使用场景符合以下形态，您也可以直接下载以下 3 种镜像来开启使用之旅！** 

**①** **CPU+NPU（800I A2）** 

•**硬件规格：** 支持单机、双机、四机、大集群

•**镜像地址：** hub.oepkgs.net/oedeploy/openeuler/aarch64/intelligence_boom:0.1.0-aarch64-800I-A2-openeuler24.03-lts-sp2 hub.oepkgs.net/oedeploy/openeuler/x86_64/intelligence_boom:0.1.0-x86_64-800I-A2-openeuler24.03-lts-sp2



**②CPU+NPU（300I Duo）** 

•**硬件规格：** 支持单机、双机

•**镜像地址：** hub.oepkgs.net/oedeploy/openeuler/aarch64/intelligence_boom:0.1.0-aarch64-300I-Duo-openeuler24.03-lts-sp2 hub.oepkgs.net/oedeploy/openeuler/x86_64/intelligence_boom:0.1.0-x86_64-300I-Duo-openeuler24.03-lts-sp2



**③** **CPU+GPU（NVIDIA A100）** 

•**硬件规格：** 支持单机单卡、单机多卡

•**镜像地址：**  hub.oepkgs.net/oedeploy/openeuler/aarch64/intelligence_boom:0.1.0-aarch64-A100-openeuler24.03-lts-sp2 hub.oepkgs.net/oedeploy/openeuler/aarch64/intelligence_boom:0.1.0-aarch64-syshax-openeuler24.03-lts-sp2-



**我们的愿景：** 基于 openEuler 构建开源的 AI 基础软件事实标准，推动企业智能应用生态的繁荣。

**当大模型遇见产业落地，我们为何需要全栈方案？** 

DeepSeek创新降低大模型落地门槛，AI进入“杰文斯悖论”时刻，需求大幅增加、多模态交互突破硬件限制、低算力需求重构部署逻辑，标志着AI从“技术验证期”迈入“规模落地期”。然而，产业实践中最核心的矛盾逐渐显现：

**产业痛点​** 

**适配难​：** 不同行业（如金融、制造、医疗）的业务场景对推理延迟、算力成本、多模态支持的要求差异极大，单一模型或工具链难以覆盖多样化需求；

**成本高​：** 从模型训练到部署，需跨框架（PyTorch/TensorFlow/MindSpore）、跨硬件（CPU/GPU/NPU）、跨存储（关系型数据库/向量数据库）协同，硬件资源利用率低，运维复杂度指数级上升；

**​生态割裂​：** 硬件厂商（如华为、英伟达）、框架厂商（Meta、Google）的工具链互不兼容，“拼凑式”部署导致开发周期长、迭代效率低。
​技术挑战

**推理效率瓶颈​：** 大模型参数规模突破万亿级，传统推理引擎对动态计算图、稀疏激活、混合精度支持不足，算力浪费严重；

**资源协同低效​：** CPU/GPU/NPU异构算力调度依赖人工经验，内存/显存碎片化导致资源闲置； 


为了解决以上问题，我们通过开源社区协同，加速开源推理方案Intelligence BooM成熟。

## 技术架构

![](/Users/项目/llm方案/xin/llm_solution/doc/deepseek/asserts/IntelligenceBoom.png)



#### **智能应用平台：让您的业务快速“接轨”AI​** 

**组件构成 ：**  openHermes（智能体引擎，利用平台公共能力，Agent应用货架化，提供行业典型应用案例、多模态交互中间件，轻量框架，业务流编排、提示词工程等能力）、deeplnsight（业务洞察平台，提供多模态识别、Deep Research能力）

【deepInsight开源地址】https://gitee.com/openeuler/deepInsight  

**核心价值** 

**低代码开发：**  openHermes提供自然语言驱动的任务编排能力，业务人员可通过对话式交互生成AI应用原型； 

**效果追踪​：**  deeplnsight实时监控模型推理效果（如准确率、延迟、成本），结合业务指标（如转化率、故障率）给出优化建议，实现“数据-模型-业务”闭环。



#### **推理服务：让模型“高效跑起来”** 

**组件构成​：**  vLLM（高性能大模型推理框架）、SGLang（多模态推理加速库）

【vLLM开源地址】https://vllm.hyper.ai/docs

**核心价值​** 

**动态扩缩容：**  vLLM支持模型按需加载，结合K8s自动扩缩容策略，降低70%以上空闲算力成本；

**大模型优化​：** vLLM通过PagedAttention、连续批处理等技术，将万亿参数模型的推理延迟降低50%，吞吐量提升3倍； 



#### **加速层：让推理“快人一步”​​** 

**组件构成​：**  sysHAX、expert-kit、ktransformers

【sysHAX开源地址】https://gitee.com/openeuler/sysHAX

【expert-kit开源地址】https://gitee.com/openeuler/expert-kit

**核心价值​** 

**异构算力协同分布式推理加速引擎：**  整合CPU、NPU、GPU等不同架构硬件的计算特性，通过动态任务分配实现"专用硬件处理专用任务"的优化，将分散的异构算力虚拟为统一资源池，实现细粒度分配与弹性伸缩；



#### **框架层：让模型“兼容并蓄”** 

**组件构成​：**  MindSpore（全场景框架）、PyTorch（Meta通用框架）、TensorFlow（Google工业框架）

【MindSpore开源地址】https://gitee.com/mindspore

**核心价值​** 

**多框架兼容：** 通过统一API接口，支持用户直接调用任意框架训练的模型，无需重写代码；

**动态图优化​：**  针对大模型的动态控制流（如条件判断、循环），提供图优化能力，推理稳定性提升30%；
​**社区生态复用​：**  完整继承PyTorch/TensorFlow的生态工具（如Hugging Face模型库），降低模型迁移成本。



#### **数据工程、向量检索、数据融合分析：从原始数据到推理燃料的转化​** 

**组件构成​：**  DataJuicer、Oasis、九天计算引擎、PG Vector、Milvus、GuassVector、Lotus、融合分析引擎

**核心价值​** 

**多模态数据高效处理与管理：**  多模态数据的统一接入、清洗、存储与索引，解决推理场景中数据类型复杂、规模庞大的管理难题，为上层智能应用提供标准化数据底座。

**高效检索与实时响应支撑：** 实现海量高维数据的快速匹配与实时查询，满足推理场景中对数据时效性和准确性的严苛要求，缩短数据到推理结果的链路延迟，为智能问答、智能运维等实时性应用提供底层性能保障。



#### **任务管理平台：让资源“聪明调度”​​** 

**组件构成​：** openFuyao（任务编排引擎）、K8S（容器编排）、RAY（分布式计算）、oeDeploy（一键部署工具）

【openFuyao开源地址】https://gitcode.com/openFuyao

【RAY开源地址】https://gitee.com/src-openeuler/ray

【oeDeploy开源地址】https://gitee.com/openeuler/oeDeploy

**核心价值​** 

**端边云协同：**  根据任务类型（如实时推理/离线批处理）和硬件能力（如边缘侧NPU/云端GPU），自动分配执行节点；

**全生命周期管理​：** 从模型上传、版本迭代、依赖安装到服务启停，提供“一站式”运维界面；
​**故障自愈​：**  实时监控任务状态，自动重启异常进程、切换备用节点，保障服务高可用性。



#### **编译器：让代码“更懂硬件”​​** 

**组件构成​：** 异构融合编译器（Bisheng）

**核心价值** 

**跨硬件优化：** 针对CPU（x86/ARM）、GPU（CUDA）、NPU（昇腾/CANN）的指令集差异，自动转换计算逻辑，算力利用率大幅提升%；

**混合精度支持​：** 动态调整FP32/FP16/INT8精度，在精度损失可控的前提下，推理速度大幅提升；
​**内存优化​：** 通过算子融合、内存复用等技术，减少30%显存/内存占用，降低硬件成本。



#### **操作系统：让全栈“稳如磐石”** 

**组件构成​：**  openEuler（开源欧拉操作系统）

【openEuler开源地址】https://gitee.com/openeuler

**核心价值** 

**异构资源管理：**  原生支持CPU/GPU/NPU的统一调度，提供硬件状态监控、故障隔离等能力；

**安全增强​：**  集成国密算法、权限隔离、漏洞扫描模块，满足金融、政务等行业的合规要求。



#### **硬件使能与硬件层：让算力“物尽其用”** 

**组件构成​：** CANN（昇腾AI使能套件）、CUDA（英伟达计算平台）、CPU（x86/ARM）、NPU（昇腾）、GPU（英伟达/国产GPU）

**核心价值** 

**硬件潜能释放：** CANN针对昇腾NPU的达芬奇架构优化矩阵运算、向量计算，算力利用率大幅提升；CUDA提供成熟的GPU并行计算框架，支撑通用AI任务；

**异构算力融合​：** 通过统一编程接口（如OpenCL），实现CPU/NPU/GPU的协同计算，避免单一硬件性能瓶颈；
​

#### **互联技术：让硬件“高速对话”​​** 

**组件构成​：** UB（通用总线）、CXL（计算与内存扩展）、NvLink（英伟达高速互联）、SUE

**核心价值** 

**低延迟通信：** CXL/NvLink提供内存级互联带宽（>1TB/s），减少跨设备数据拷贝开销

**灵活扩展：** 支持从单机（多GPU）到集群（跨服务器）的无缝扩展，适配不同规模企业的部署需求。




## 全栈解决方案部署教程

目前方案已支持**DeepSeek**/**Qwen**/**Llama**/**GLM**/**TeleChat**等50+主流模型，以下我们选取DeepSeek V3&R1 模型和 openEuler Intelligence 应用的部署来

### DeepSeek V3&R1部署

参考[部署指南](https://gitee.com/openeuler/llm_solution/blob/master/doc/deepseek/DeepSeek-V3&R1%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97.md)，使用一键式部署脚本，20min完成推理服务拉起。



### 一键式部署DeepSeek 模型和openEuler Intelligence智能应用

参考[一键式部署openEuler Intelligence ](https://gitee.com/openeuler/llm_solution/tree/master/script/mindspore-intelligence)，搭建本地知识库并协同DeepSeek大模型完成智能调优、智能运维等应用；


## 性能

### 精度

本方案使用8bit权重量化、SmoothQuant
8bit量化和混合量化等技术，最终以CEval精度损失2分的代价，实现了DeepSeek-R1w8a8的大模型部署。

| 模型                   | CEval精度 |
| ---------------------- | --------- |
| Claude-3.5-Sonnet-1022 | 76.7      |
| GPT-4o 0513            | 76        |
| DeepSeek V3            | 86.5      |
| GPT-4o 0513            | 76        |
| OpenAI o1-mini         | 68.9      |
| DeepSeek R1            | 91.8      |
| Deepseek R1 w8a8       | 89.52     |
| Deepseek R1 W4A16      | 88.78     |
| Deepseek V3 0324 W4A16 | 87.82     |



### 吞吐

测试环境：

1.  两台Atlas 800I A2（8\*64G）。
2.  Ascend HDK Driver 24.1.0版本，Firmware 7.5.0.3.22版本。
3.  openEuler 22.03 LTS版本（内核 5.10）。

| 并发数 | 吞吐(Token/s) |
| ------ | ------------- |
| 1      | 22.4          |
| 192    | 2600          |



## 参与贡献

欢迎通过issue方式提出您宝贵的建议，共建开箱即优、性能领先的全栈开源国产化推理解决方案

# llm_solution
