#!/usr/bin/env python3
import yaml
import argparse
import sys
from typing import Any, Dict, List, Union

def get_nested_value(data: Dict[str, Any], keys: List[str]) -> Union[Any, None]:
    """
    递归获取嵌套字典中的值
    
    Args:
        data: 字典数据
        keys: 键路径列表
        
    Returns:
        找到的值，如果找不到则返回 None
    """
    if not keys:
        return data
        
    key = keys[0]
    if key in data:
        if len(keys) == 1:
            return data[key]
        elif isinstance(data[key], dict):
            return get_nested_value(data[key], keys[1:])
        else:
            # 如果还有剩余键但当前值不是字典，说明路径错误
            return None
    return None

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='从YAML文件中提取键值')
    parser.add_argument('-f', '--file', required=True, help='YAML文件路径')
    parser.add_argument('-k', '--key', required=True, 
                        help='点分隔的键路径（例如：all.vars.image_name）')
    parser.add_argument('-y', '--yaml', action='store_true', 
                        help='以YAML格式输出复杂结构')
    parser.add_argument('-q', '--quiet', action='store_true', 
                        help='仅输出值，不输出额外信息')
    
    args = parser.parse_args()
    
    try:
        # 读取YAML文件
        with open(args.file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        # 分割键路径
        key_path = args.key.split('.')
        
        # 获取值
        value = get_nested_value(yaml_data, key_path)
        
        if value is None:
            if not args.quiet:
                print(f"错误: 键路径 '{args.key}' 未找到", file=sys.stderr)
            sys.exit(1)
        
        # 输出结果
        if args.yaml and isinstance(value, (dict, list)):
            # 复杂结构以YAML格式输出
            print(yaml.dump(value, default_flow_style=False, sort_keys=False).strip())
        elif isinstance(value, (dict, list)):
            # 复杂结构默认以JSON格式输出
            print(yaml.dump(value, default_flow_style=False, sort_keys=False).strip())
        else:
            # 简单值直接输出
            print(value)
            
    except FileNotFoundError:
        if not args.quiet:
            print(f"错误: 文件 '{args.file}' 不存在", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        if not args.quiet:
            print(f"YAML解析错误: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if not args.quiet:
            print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
