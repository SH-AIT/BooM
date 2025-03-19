# benchmark性能测试脚本

本测试脚本旨在对在线推理服务进行性能评估。

### 测试参数

可以通过以下命令查看benchmark测试参数

```shell
# python benchmark_parallel.py -h
None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.
usage: benchmark_parallel.py [-h] [--backend {vllm,mindspore,base,tgi,openai,trt,embedding,openai-chat}] [--host HOST]
                             [--port PORT] [--url URL] [--app-code APP_CODE] --tokenizer TOKENIZER [--best-of BEST_OF]
                             [--use-beam-search] [--request-rate REQUEST_RATE] [--epochs EPOCHS]
                             [--parallel-num PARALLEL_NUM [PARALLEL_NUM ...]]
                             [--output-tokens OUTPUT_TOKENS [OUTPUT_TOKENS ...]]
                             [--prompt-tokens PROMPT_TOKENS [PROMPT_TOKENS ...]] [--benchmark-csv BENCHMARK_CSV]
                             [--seed SEED] [--served-model-name SERVED_MODEL_NAME]
                             [--num-scheduler-steps NUM_SCHEDULER_STEPS] [--enable-prefix-caching ENABLE_PREFIX_CACHING]
                             [--prefix-caching-num PREFIX_CACHING_NUM] [--use-spec-decode]
                             [--num-speculative-tokens NUM_SPECULATIVE_TOKENS] [--dataset-type {random,sharegpt,human-eval}]
                             [--dataset-path DATASET_PATH] [--use-real-dataset-output-tokens]
                             [--use-pd-separate USE_PD_SEPARATE]

Benchmark the serving prefill performance.

options:
  -h, --help            show this help message and exit
  --backend {vllm,mindspore,base,tgi,openai,trt,embedding,openai-chat}
  --host HOST
  --port PORT
  --url URL
  --app-code APP_CODE
  --tokenizer TOKENIZER
                        Name or path of the tokenizer.
  --best-of BEST_OF     Generates `best_of` sequences per prompt and returns the best one.
  --use-beam-search
  --request-rate REQUEST_RATE
                        Number of requests per second. If this is inf, then all the requests are sent at time 0. Otherwise,
                        we use Poisson process to synthesize the request arrival times.
  --epochs EPOCHS       Number of epochs.
  --parallel-num PARALLEL_NUM [PARALLEL_NUM ...]
                        Number of parallel request number.
  --output-tokens OUTPUT_TOKENS [OUTPUT_TOKENS ...]
                        Max tokens to process.
  --prompt-tokens PROMPT_TOKENS [PROMPT_TOKENS ...]
                        Max tokens to process.
  --benchmark-csv BENCHMARK_CSV
                        Path to the csv.
  --seed SEED
  --served-model-name SERVED_MODEL_NAME
  --num-scheduler-steps NUM_SCHEDULER_STEPS
  --enable-prefix-caching ENABLE_PREFIX_CACHING
  --prefix-caching-num PREFIX_CACHING_NUM
  --use-spec-decode
  --num-speculative-tokens NUM_SPECULATIVE_TOKENS
                        the step if spec decode, default -1 for disable accept rate statistic.
  --dataset-type {random,sharegpt,human-eval}
  --dataset-path DATASET_PATH
  --use-real-dataset-output-tokens
  --use-pd-separate USE_PD_SEPARATE

```

### 多batch测试

可以参考以下命令进行192-batch多并发测试

```bash
python benchmark_parallel.py --backend openai --host [主服务IP] --port [推理接口] --tokenizer [权重路径] --num-scheduler-steps=8 --epochs 1 --parallel-num 192 --prompt-tokens 256 --output-tokens 256
```

最终输出如下：

```shell
2025-03-19 08:25:32,725 - benchmark_utils - INFO - 所有请求耗时: 13.5293 s
2025-03-19 08:25:32,726 - benchmark_utils - INFO - 请求吞吐: 14.1914 requests/s
2025-03-19 08:25:32,726 - benchmark_utils - INFO - 输出tokens总吞吐: 3633.0039 tokens/s
2025-03-19 08:25:32,728 - benchmark_utils - INFO - 首tokens时延TP90: 7958.1101 ms
2025-03-19 08:25:32,729 - benchmark_utils - INFO - 首tokens时延TP99: 7964.8968 ms
2025-03-19 08:25:32,729 - benchmark_utils - INFO - 最大首tokens时延: 7966.0322 ms
2025-03-19 08:25:32,729 - benchmark_utils - INFO - 平均首tokens时延: 5049.2075 ms
2025-03-19 08:25:32,740 - benchmark_utils - INFO - 增量时延TP90: 159.5743 ms
2025-03-19 08:25:32,744 - benchmark_utils - INFO - 增量时延TP99: 175.7760 ms
2025-03-19 08:25:32,746 - benchmark_utils - INFO - 最大增量时延: 207.5 ms
2025-03-19 08:25:32,749 - benchmark_utils - INFO - 平均增量时延: 20.8 ms
2025-03-19 08:25:42,751 - benchmark_utils - INFO - ['输入长度', '输出长度', '并发数', '输出tokens总吞吐', '首tokens时延TP90（ms）', '首tokens时延TP99（ms）', '最大首tokens时延（ms）', '平均首tokens时延（ms）', '增量时延TP90（ms）', '增量时延TP99（ms）', '最大增量时延（ms）', '平均增量时延（ms）']
2025-03-19 08:25:42,753 - benchmark_utils - INFO - [256.0, 256.0, 192, 3633.0039, 7958.1101, 7964.8968, 7966.0322, 5049.2075, 159.5743, 175.776, 207.5029, 20.7627]
2025-03-19 08:25:42,753 - __main__ - INFO - Benchmark parallel finished
```

