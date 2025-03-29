# Copyright 2024 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""
Utils for cann workqueue cores
"""

import os
import psutil
import subprocess

def int_to_binary_list(value: int, align_length: int = 4) -> list:
    """
    convert int value to binary list
    e.g. 13 => [1, 1, 0, 1]
    current only for 0 - 15

    Args:
        value (`int`):
            The int value to convert to binary list.
        align_length (`int`, *optional*, defaults to `4`):
            The align length for list, it will add 0 for small value

    Returns:
        The binary list with the value.
    """
    bin_list = []
    divider = value
    remainder = 0
    while True:
        remainder = divider % 2
        divider = int(divider / 2)
        bin_list.append(remainder)
        if divider == 0:
            break

    while len(bin_list) < align_length:
        bin_list.append(0)

    bin_list.reverse()
    return bin_list


def binary_list_to_int(bin_list: list) -> int:
    """
    convert binary list to int value
    e.g. [1, 1, 0, 1] => 13
    current only for 0 - 15

    Args:
        bin_list (`list`):
            The binary list represent to int value.

    Returns:
        The int value.
    """
    value = 0
    muliplier = 1
    bin_list.reverse()
    for v in bin_list:
        value = value + v * muliplier
        muliplier *= 2
    return value


def string_to_bit_list(array_string: str) -> list:
    """
    convert hex string to binary list
    e.g. "ff" => [1, 1, 1, 1, 1, 1, 1, 1]
        "deadbeef" => [1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1]

    Args:
        array_string (`str`):
            The binary list represent to int value.

    Returns:
        The binary list for the string.
    """
    bin_list = []
    for c in array_string:
        bit_list = int_to_binary_list(int(c, 16))
        bin_list += bit_list
    bin_list.reverse()
    return bin_list


class BitArray:
    """
    The bit array class to solve core mask string.

    Args:
        length(`int`, *optional*, defaults to `0`):
            The max bit length of the array.
    """

    def __init__(self, length: int = 0):
        self.bits = [0 for _ in range(length)]

    def load_from_str(self, array_string: str):
        """
        load bit array from hex string

        Args:
            array_string (`str`):
                The binary list represent to int value.

        Returns:
            NA.
        """
        self.bits = string_to_bit_list(array_string)

    def get_marked_index(self) -> list:
        """
        get the index list with value 1

        Args:
            NA.

        Returns:
            The index list.
        """
        marked_index_list = []
        for idx, item in enumerate(self.bits):
            if item == 1:
                marked_index_list.append(idx)
        return marked_index_list

    def to_bytes_array(self) -> list:
        """
        convert the bit array to byte array which is 8-bit elements

        Args:
            NA.

        Returns:
            The array values with bytes.
        """
        bytes_array = []
        slide_window_list = []
        self.bits.reverse()
        for idx, item in enumerate(self.bits):
            slide_window_list.append(item)
            if (idx + 1) % 8 == 0:
                value = binary_list_to_int(slide_window_list)
                slide_window_list.clear()
                bytes_array.append(value)
        self.bits.reverse()
        return bytes_array

    def __setitem__(self, index: int, value: int):
        """
        set the bit value with index

        Args:
            index (`int`):
                The index to set value.
            value (`int`):
                The value to set.

        Returns:
            NA.
        """
        self.bits[index] = value

    def __getitem__(self, index: int) -> int:
        """
        get the bit value with index

        Args:
            index (`int`):
                The index to get value.

        Returns:
            The value to get.
        """
        return self.bits[index]



def get_cann_workqueue_cores(device_id: int) -> list:
    """
    get cann workqueue binding cores list
    for most system, the config is set on path:
    /sys/devices/virtual/workqueue/dev0_sq_send_wq/cpumask

    Args:
        device_id (`int`):
            The device_id for the workqueue, most time is related to rank_ik.

    Returns:
        The marked core index list.
    """
    cann_workqueue_config_path = f"/sys/devices/virtual/workqueue/dev{device_id}_sq_send_wq/cpumask"
    if not os.path.exists(cann_workqueue_config_path):
        # no this config, return [] to disable cann binding
        return []

    f = open(cann_workqueue_config_path)
    cann_config = f.read()
    cann_config = cann_config.replace(",", "")
    cann_config = cann_config.replace("\n", "")
    mask_array = BitArray()
    mask_array.load_from_str(cann_config)
    return mask_array.get_marked_index()


def mask_to_str(mask: BitArray) -> str:
    """
    convert BitArray mask to string format with workqueue config

    Args:
        mask (`BitArray`):
            The BitArray mask to convert to string.

    Returns:
        The string followed with cann workqueue format to config.
    """
    mask_bytes = mask.to_bytes_array()
    mask_str = ""
    separete_num = 4
    i = 0
    for mask_value in mask_bytes:
        mask_str += '{:02x}'.format(mask_value)
        i += 1
        if i % separete_num == 0:
            mask_str += ","
    mask_str = mask_str[:-1]
    return mask_str


def execute_cmd(cmd: str, fake: bool ):
    """
    execute shell command

    Args:
        cmd (`str`):
            The command need to execute.
        fake (`bool`, *optional*, defaults to `False`):
            If fake execute is True, then print command instead to execute.

    Returns:
        NA.
    """
    if fake:
        print(cmd)
        return
    sub_process = subprocess.Popen(cmd, shell=True)
    ret = sub_process.wait()
    if ret != 0:
        raise SystemError(f"Execute cmd({cmd}) failed!")

def execute_command(cmd_list):
    try:
        with subprocess.Popen(cmd_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
            out, _ = p.communicate(timeout=1000)
        res = out.decode()
        return res
    except FileNotFoundError as e:
        raise RuntimeError(f"Failed to execute command, because {e}.")

def get_numa_map(affinity: bool, core_num_per_workqueue: int):
    numa_topo_out = execute_command(["npu-smi", "info", "-t", "topo"]).strip().split("\n")

    line_no = 0
    npu_no = 0
    numa_to_npu_map = {}
    numa_number = 0
    max_cpu = 0

    numa_node = execute_command("lscpu").strip().split("\n")
    for val in numa_node:
        if val.startswith("CPU(s):"):
            max_cpu = int(val.split(" ")[-1]) - 1
        if val.startswith("NUMA"):
            nodes = val.split(" ")
            numa_number = int(nodes[-1])
            break

    npu_max_cpu = False
    npu_max_cpu_no = 0
    for val in numa_topo_out:
        line_no += 1
        line = ''.join(val.split())
        if line.startswith("NPU") and line_no > 1:
            cpu_range = line[33:]
            npu_max_cpu_no = max(npu_max_cpu_no, int(cpu_range.split("-")[1]))
            if numa_to_npu_map.get(cpu_range, None) is None:
                numa_to_npu_map[cpu_range] = list()
            numa_to_npu_map[cpu_range].append(npu_no)
            npu_no += 1

    npu_max_cpu = True if npu_max_cpu_no==max_cpu else False
    print(len(numa_to_npu_map), npu_no, numa_number, max_cpu, npu_max_cpu_no, npu_max_cpu)
    shared_mode = False
    if npu_no > numa_number:
        shared_mode = True
        print("Shared mode")

    npu_to_core_map = {}
    for key, val in numa_to_npu_map.items():
        cpu_range = key.split("-")
        cpu_start = int(cpu_range[0])
        cpu_end = int(cpu_range[1])
        if shared_mode:
            total_core_num = cpu_end - cpu_start + 1
            shared_npu_num = len(val)
            core_num_per_npu = int(total_core_num / shared_npu_num)
        else:
            core_num_per_npu = cpu_end - cpu_start + 1 if npu_max_cpu==False else -(cpu_end - cpu_start + 1)
        core_start = cpu_start
        for npu in val:
            npu_to_core_map[npu] = core_start + core_num_per_npu - 1
            if affinity == False:
                core_start += core_num_per_npu
            else:
                core_start -= core_num_per_workqueue
                #core_start -= core_num_per_npu//2

    return npu_to_core_map

def binding_cann_workqueue(device_num: int, core_num_per_workqueue: int, separate_device_cores: bool):
    """
    binding cann workqueue cores

    Args:
        device_num (`int`):
            The total device number on the server.
        core_num_per_workqueue (`int`):
            The core number for each workqueue, the core index will alloc from end core index for each device.
        separate_device_cores (`int`):
            If separate device cores, each device workqueue binding itself cores,
            otherwise, all device workqueu binding to same cores.

    Returns:
        NA.
    """
    print(f"the cann workqueue config command list in the follow, please execute the cmd by root user!")
    total_core_num = psutil.cpu_count(logical=True)
    core_num_per_device = int(total_core_num / device_num)

    device_core_mask = BitArray(total_core_num)
    end_core_map = get_numa_map(True, core_num_per_workqueue)
    for i in range(device_num):
        cann_workqueue_config_path = f"/sys/devices/virtual/workqueue/dev{i}_sq_send_wq/cpumask"
        mask = BitArray(total_core_num)
        #start_core_num = i * core_num_per_device
        end_core_num = end_core_map[i]  #start_core_num + core_num_per_device - 1
        for j in range(core_num_per_workqueue):
            core_index = end_core_num - j
            mask[core_index] = 1
            device_core_mask[core_index] = 1

        if separate_device_cores:
            mask_str = mask_to_str(mask)
            bind_cann_core_cmd = f"echo \"{mask_str}\" > {cann_workqueue_config_path}"
            execute_cmd(bind_cann_core_cmd, False)

    if not separate_device_cores:
        device_core_mask_str = mask_to_str(device_core_mask)

        for i in range(device_num):
            cann_workqueue_config_path = f"/sys/devices/virtual/workqueue/dev{i}_sq_send_wq/cpumask"
            bind_cann_core_cmd = f"echo \"{device_core_mask_str}\" > {cann_workqueue_config_path}"
            execute_cmd(bind_cann_core_cmd)

binding_cann_workqueue(8, 4, True)
