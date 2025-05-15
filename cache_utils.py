# cache_utils.py

import os
import json

CACHE_FILE = "last_data_cache.json"  # 缓存文件名


def load_last_data(key: str):
    """
    加载上次存储的值。
    
    :param key: 数据的键名
    :return: 对应键名的值或 None（如果不存在）
    """
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(key)
    except Exception as e:
        print(f"读取缓存失败: {e}")
        return None


def save_current_data(key: str, value: str):
    """
    保存当前值到缓存文件中。
    
    :param key: 数据的键名
    :param value: 要保存的数据值
    """
    data = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[key] = value
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"写入缓存失败: {e}")
