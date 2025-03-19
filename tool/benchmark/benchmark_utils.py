import asyncio
import csv
import json
import logging
import os
import stat
import time
from typing import Union

import aiohttp
import numpy as np
import requests
from tqdm import tqdm
from transformers import (AutoTokenizer, PreTrainedTokenizer,
                          PreTrainedTokenizerFast)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
IS_DEBUG = int(os.environ.get("BENCKMARK_DEBUG", 0))
EPOCH_NUM = 10
# The size of the data block returned in each iteration is not greater than 8192. Therefore, chunk_size is 8192.
CHUNK_SIZE = 8192
TIMEOUT = 3 * 3600

if IS_DEBUG:
    import matplotlib.lines as mlines
    import matplotlib.pyplot as plt


def get_tokenizer(
        transformer_tokenizer_path: str,
) -> Union[PreTrainedTokenizer, PreTrainedTokenizerFast]:
    """Gets a tokenizer for the given model name via Huggingface."""
    tokenizer = AutoTokenizer.from_pretrained(transformer_tokenizer_path, trust_remote_code=True)

    return tokenizer


def generate_hello_str(tokenizer, length, hello_token="Hello"):
    text = hello_token * (length - 1)
    completion_token_ids = tokenizer([text]).input_ids
    while len(completion_token_ids[0]) < length:
        text += hello_token
        completion_token_ids = tokenizer([text]).input_ids

    return text


def generate_str(tokenizer, length):
    vocab_size = tokenizer.vocab_size
    ids = np.random.randint(vocab_size / 4, vocab_size / 3, length)
    text = tokenizer.decode(ids)

    completion_token_ids = tokenizer([text]).input_ids
    if IS_DEBUG:
        logger.info("len(completion_token_ids[0]) %d, length %d ", len(completion_token_ids[0]), length)

    epoch = EPOCH_NUM
    while len(completion_token_ids[0]) != length and epoch > 0:
        while len(completion_token_ids[0]) > length:
            diff = len(completion_token_ids[0]) - length
            now_length = ids.shape[0] - diff
            ids = ids[:now_length]
            text = tokenizer.decode(ids)
            completion_token_ids = tokenizer([text]).input_ids
            if IS_DEBUG:
                logger.info("len(completion_token_ids[0]) %d, %d ", len(completion_token_ids[0]), length)

        while len(completion_token_ids[0]) < length:
            diff = length - len(completion_token_ids[0])
            diff_ids = np.random.randint(vocab_size / 4, vocab_size / 3, diff)
            ids = np.append(ids, diff_ids)
            text = tokenizer.decode(ids)
            completion_token_ids = tokenizer([text]).input_ids
            if IS_DEBUG:
                logger.info("len(completion_token_ids[0]) %d, %d ", len(completion_token_ids[0]), length)

        epoch -= 1

    if len(completion_token_ids[0]) != length:
        text = generate_hello_str(tokenizer, length)

    if IS_DEBUG:
        logger.info(text)
    return text


def get_api_url(backend, host, port, url):
    if url is not None and len(url) > 0:
        return url

    if backend == "mindspore":
        api_url = f"http://{host}:{port}/models/llama2/generate"
    elif backend == "base":
        api_url = f"http://{host}:{port}/v1/generate"
    elif backend == "tgi":
        api_url = f"https://{host}:{port}/generate_stream"
    elif backend == "openai":
        api_url = f"http://{host}:{port}/v1/completions"
    elif backend == "trt":
        api_url = f"http://{host}:{port}/v2/models/ensemble/generate_stream"
    else:
        api_url = f"http://{host}:{port}/generate"
    return api_url


def get_request_data(
        backend: str,
        prompt: str,
        prompt_len: int,
        output_len: int,
        best_of: int,
        use_beam_search: bool,
        app_code: str = None,
        model: str = None,
        served_model_name: str = None,
        use_spec_decode: bool = False
):
    confirm_error_output = False

    if app_code is not None and len(app_code) > 0:
        headers = {"User-Agent": "Benchmark Client",
                   'Content-Type': 'application/json',
                   'X-Apig-AppCode': app_code}
    else:
        headers = {"User-Agent": "Benchmark Client"}

    if backend == "vllm":
        pload = {
            "prompt": prompt,
            "temperature": 0.0,
            "top_p": 0.8,
            "top_k": 5,
            "max_tokens": output_len,
            "ignore_eos": True,
            "stream": True,
        }
        if use_spec_decode:
            pload["skip_special_tokens"] = False
        confirm_error_output = True
    elif backend == "openai":
        if served_model_name is None:
            served_name = model
        else:
            served_name = served_model_name
        pload = {
            "prompt": prompt,
            "temperature": 0,
            "top_p": 0.8,
            "top_k": 5,
            "max_tokens": output_len,
            "ignore_eos": True,
            "model": served_name,
            "stream": True,
        }
        if use_spec_decode:
            pload["skip_special_tokens"] = False
        confirm_error_output = True
    elif backend == "mindspore":
        params = {
            "max_new_tokens": output_len,
            "do_sample": False,
            "ignore_eos": True,
            "return_full_text": False
        }
        pload = {
            "inputs": prompt,
            "parameters": params,
            "stream": True
        }
    elif backend == "base":
        pload = {
            "prompt": prompt,
            "max_tokens": (prompt_len + output_len),
            "model_name": "llama2",
            "do_sample": False,
            "stream": True,
            "debug": 2
        }
    elif backend == "tgi":
        params = {
            "best_of": best_of,
            "max_new_tokens": output_len,
            "do_sample": False,
            "ignore_eos_token": True,
            "decoder_input_details": False
        }
        pload = {
            "inputs": prompt,
            "parameters": params,
        }
        confirm_error_output = True
    elif backend == "trt":
        headers = {"Content-Type": "text/event-stream; charset=utf-8"}
        params = {
            "max_tokens": output_len,
            "min_length": output_len,
            "bad_words": "",
            "stop_words": "",
            "ignore_eos": True,
            "stream": True
        }
        pload = {
            "text_input": prompt,
            "parameters": params,
        }
        confirm_error_output = True
    else:
        raise ValueError(f"Unknown backend: {backend}")

    return headers, pload, confirm_error_output


async def do_request(api_url, headers, pload, confirm_error_output, output_len, num_scheduler_steps,
                     use_spec_decode=False):
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    first_token = True
    async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as session:
        while True:
            last_chunk = None
            prefill_start_time = time.perf_counter()
            time_record = [prefill_start_time]
            chunk_record = []
            async with session.post(api_url, headers=headers, json=pload) as response:
                async for chunk, _ in response.content.iter_chunks():
                    if len(chunk.strip()) > 0:
                        last_chunk = chunk
                        return_token_num = 1 if first_token else min(num_scheduler_steps, output_len)
                        time_record.extend([time.perf_counter()] * return_token_num)
                        first_token = False
                        output_len -= return_token_num
                    # for maximum block depth
                    if len(chunk.strip()) > 0 and use_spec_decode:
                        chunk_record.append(last_chunk)

            if confirm_error_output:
                if last_chunk.startswith(b'data:'):
                    output = last_chunk[5:].strip().decode("utf-8")
                else:
                    output = last_chunk.strip().strip().decode("utf-8").rstrip("\0")

                if IS_DEBUG:
                    logger.info(output)
                if output == '[DONE]':
                    break
                try:
                    output = json.loads(output)
                except Exception:
                    logger.error("Exception")
                    break

                # Re-send the request if it failed.
                if "error" not in output:
                    break
                else:
                    logger.error("request failed, %s, retry", output)
                    await asyncio.sleep(0.1)
            else:
                break
        return time_record, chunk_record


def check_multi_step(args, api_url, tokenizer, prompt_len, output_len):
    prompt = generate_str(tokenizer, prompt_len)
    headers, pload, confirm_error_output = get_request_data(args.backend,
                                                            prompt,
                                                            prompt_len,
                                                            output_len,
                                                            args.best_of,
                                                            args.use_beam_search,
                                                            args.app_code,
                                                            args.tokenizer,
                                                            args.served_model_name)
    return_num = 0
    response = requests.post(api_url, headers=headers, json=pload, stream=True, timeout=TIMEOUT)
    response.raise_for_status()
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        return_num += 1

    # openai流式最后返回[done],其余接口没有
    end_chunk_num = 1 if args.backend == 'openai' else 0
    # 首token + 是否有返回[done] + chunk_num
    theory_return_num = 1 + end_chunk_num + (output_len - 1) // args.num_scheduler_steps
    # (output_len - 1) % num_scheduler_steps 非整除情况下最后返回包含剩余token的chunk
    theory_return_num += 1 if (output_len - 1) % args.num_scheduler_steps else 0
    if theory_return_num == return_num:
        return True
    return False


def statistics_and_print_performance_data(args, prompt_tokens, output_tokens, parallel_num,
                                          request_latency_record, all_latency_record):
    benchmark_start_time = np.min([time_record[0] for _, _, time_record, _ in request_latency_record])
    benchmark_end_time = np.max([time_record[-1] for _, _, time_record, _ in request_latency_record])
    benchmark_time = benchmark_end_time - benchmark_start_time
    logger.info("所有请求耗时: %.4f s", benchmark_time)

    benchmark_requests = args.epochs * parallel_num / benchmark_time
    logger.info("请求吞吐: %.4f requests/s", benchmark_requests)

    total_output_tokens = np.sum([
        output_len
        for _, output_len, _, _ in request_latency_record
    ])
    total_output_token_throughput = total_output_tokens / benchmark_time
    logger.info("输出tokens总吞吐: %.4f tokens/s", total_output_token_throughput)

    prefill_latency_list = [
        time_record[1] - time_record[0]
        for _, _, time_record, _ in request_latency_record
    ]

    p90_prefill_latency = np.percentile(prefill_latency_list, 90) * 1000
    logger.info("首tokens时延TP90: %.4f ms", p90_prefill_latency)

    p99_prefill_latency = np.percentile(prefill_latency_list, 99) * 1000
    logger.info("首tokens时延TP99: %.4f ms", p99_prefill_latency)

    max_prefill_latency = np.max(prefill_latency_list) * 1000
    logger.info("最大首tokens时延: %.4f ms", max_prefill_latency)

    avg_prefill_latency = np.mean(prefill_latency_list) * 1000
    logger.info("平均首tokens时延: %.4f ms", avg_prefill_latency)

    prefill_ranges = [
        (time_record[0], time_record[1])
        for _, _, time_record, _ in request_latency_record
    ]

    def in_ranges(ranges, start, end):
        for time_range in ranges:
            if start <= time_range[1] and end >= time_range[0]:
                return True
        return False

    decode_latency_list = [
        end - start
        for _, _, time_record, _ in request_latency_record
        for start, end in zip(time_record[1:-1], time_record[2:])
        if not in_ranges(prefill_ranges, start, end)
    ]

    # 去掉开始的0（multi-step场景）
    start_index = 0
    for latency_index, latency in enumerate(decode_latency_list):
        if latency > 0:
            start_index = latency_index
            break
    decode_latency_list = decode_latency_list[start_index:]

    p90_decode_latency = np.percentile(decode_latency_list, 90) * 1000
    logger.info("增量时延TP90: %.4f ms", p90_decode_latency)

    p99_decode_latency = np.percentile(decode_latency_list, 99) * 1000
    logger.info("增量时延TP99: %.4f ms", p99_decode_latency)

    max_decode_latency = np.max(decode_latency_list) * 1000
    logger.info("最大增量时延: %.1f ms", max_decode_latency)

    avg_decode_latency = np.mean(decode_latency_list) * 1000
    logger.info("平均增量时延: %.1f ms", avg_decode_latency)

    if IS_DEBUG:
        plot_time_record(benchmark_start_time, benchmark_time, request_latency_record,
                         f"{parallel_num}_{prompt_tokens}_{output_tokens}.jpg")

    avg_prompt_token = np.mean([prompt_len for prompt_len, _, _, _ in request_latency_record])
    avg_output_token = np.mean([output_len for _, output_len, _, _ in request_latency_record])

    if getattr(args, "height", None) is None:
        latency_record = (avg_prompt_token, avg_output_token, parallel_num,
                        total_output_token_throughput,
                        p90_prefill_latency, p99_prefill_latency, max_prefill_latency, avg_prefill_latency,
                        p90_decode_latency, p99_decode_latency, max_decode_latency, avg_decode_latency)
    else:
        image_shape = str(args.height) + ',' + str(args.width)
        latency_record = (avg_prompt_token, avg_output_token, parallel_num, image_shape,
                        total_output_token_throughput,
                        p90_prefill_latency, p99_prefill_latency, max_prefill_latency, avg_prefill_latency,
                        p90_decode_latency, p99_decode_latency, max_decode_latency, avg_decode_latency)

    # If the benchmark backend supports speculative inference, request_latency_record is replaced with output_step,
    # which is an int value. Otherwise, the original chunk_list is retained as a list.
    is_spec_support_backend = isinstance(request_latency_record[0][-1], int)
    if getattr(args, "use_spec_decode", False) and getattr(args, "num_speculative_tokens", -1) >= 0 \
            and is_spec_support_backend:
        accept_rate_list = [(output_len - 1) / ((output_step - 1) * (args.num_speculative_tokens + 1)) for
                            _, output_len, _, output_step in request_latency_record]

        p90_accept_rate = np.percentile(accept_rate_list, 90)
        logger.info("投机接受率TP90: %.4f", p90_accept_rate)

        p99_accept_rate = np.percentile(accept_rate_list, 99)
        logger.info("投机接受率TP99: %.4f", p99_accept_rate)

        max_accept_rate = np.max(accept_rate_list)
        logger.info("投机最大接受率: %.2f", max_accept_rate)

        min_accept_rate = np.min(accept_rate_list)
        logger.info("投机最小接受率: %.2f", min_accept_rate)

        avg_accept_rate = np.mean(accept_rate_list)
        logger.info("投机平均接受率: %.2f", avg_accept_rate)

        accept_rate_record = (p90_accept_rate, p99_accept_rate, max_accept_rate, min_accept_rate, avg_accept_rate)

        latency_record = latency_record + accept_rate_record

    time.sleep(10)

    all_latency_record.append(latency_record)


def plot_time_record(benchmark_start_time, benchmark_time, request_latency_record, name="parallel.jpg"):
    def newline(ax, p1, p2, color='skyblue'):
        line = mlines.Line2D([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=20, markersize=100, marker=".",
                             markerfacecolor=color)
        ax.add_line(line)

    fig_size_x = 256
    fig_size_y = 128
    fig, ax = plt.subplots(1, 1, figsize=(fig_size_x, fig_size_y), facecolor='#f7f7f7', dpi=80)
    time_records = [time_record for _, _, time_record in request_latency_record]
    time_records = (time_records - benchmark_start_time) * 1000
    for idx, time_record in enumerate(tqdm(time_records, desc="plot_time_record")):
        idx = idx * 1
        newline(ax, [time_record[0], idx], [time_record[1], idx], color='red')
        for start, end in zip(time_record[1:-1], time_record[2:]):
            newline(ax, [start, idx], [end, idx])

    ax.set_facecolor('#f7f7f7')
    ax.set(xlim=(0, (benchmark_time * 1000) + 10), ylim=(-1, len(time_records) * 1), ylabel='request')
    font_size = round(fig_size_x / 3)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.xlabel('time', fontsize=fig_size_x)
    plt.ylabel('request', fontsize=fig_size_x)
    logger.info(f"save fig ...")
    plt.savefig(name)


def save_to_csv(benchmark_head, records, csv_path):
    logger.info(benchmark_head)
    sprtr_idx = csv_path.rfind('/')
    if sprtr_idx > 0:
        csv_dir = csv_path[0:sprtr_idx]
        if len(csv_dir) > 1:
            os.makedirs(csv_dir, exist_ok=True)

    # 设置文件打开的标志
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    # 设置文件权限，仅授予文件所有者读写权限
    mode = stat.S_IWUSR | stat.S_IRUSR
    # 使用 os.open 打开文件描述符
    fd = os.open(csv_path, flags, mode)
    with os.fdopen(fd, 'w', encoding='utf-8-sig', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(benchmark_head)
        for items in records:
            to_csv = []
            for item in items:
                if isinstance(item, float):
                    item = round(item, 4)
                to_csv.append(item)
            logger.info(to_csv)
            writer.writerow(to_csv)
