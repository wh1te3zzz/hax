# -*- coding:utf-8 -*-
# -------------------------------
# @Author : github@wh1te3zzz https://github.com/wh1te3zzz/hax
# @Time : 2025-05-15 13:57:56
# hax监控脚本，监控数据中心变化和当前可创建的区域
# -------------------------------
"""
hax 已开通数据

cron: 59 * * * *
const $ = new Env("hax 已开通数据");
"""
# monitor_hax_stats.py
import os
import requests
from bs4 import BeautifulSoup
import notify

# 配置项
URL_HAX_SERVER_INFO = "https://hax.co.id/data-center"
ENV_NAME = "HAX_STATS"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_page(url):
    """请求页面内容"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"请求失败: {e}")
        return ""


def parse_server_info(html_text):
    """解析服务器信息"""
    soup = BeautifulSoup(html_text, "html.parser")
    zone_list = [x.text for x in soup.find_all("h5", class_="card-title mb-4")]
    sum_list = [x.text for x in soup.find_all("h1", class_="card-text")]

    result = {}
    for zone_info, count_info in zip(zone_list, sum_list):
        parts = zone_info.split("-", 1)
        region = parts[0].lstrip("./")
        suffix = f"{parts[1]}({count_info.rstrip(' VPS')}♝)" if len(parts) > 1 else count_info
        result.setdefault(region, []).append(suffix)

    return "\n".join([f">>{region}-" + ", ".join(values) for region, values in result.items()])


def get_current_data():
    """获取当前服务器信息"""
    html = fetch_page(URL_HAX_SERVER_INFO)
    return parse_server_info(html) if html else None


def get_cached_data():
    """从青龙环境中获取缓存的数据"""
    envs_response = QLAPI.getEnvs({"searchValue": ENV_NAME})
    data = envs_response.get("data", [])
    return data[0]["value"] if data else None


def update_or_create_env(value):
    """更新或创建环境变量"""
    envs = QLAPI.getEnvs({"searchValue": ENV_NAME}).get("data", [])
    new_env = {
        "name": ENV_NAME,
        "value": value,
        "remarks": "Hax 已开通数据缓存"
    }

    if envs:
        item = envs[0]
        item["value"] = value
        QLAPI.updateEnv({"env": item}) and print("✅ 环境变量已更新")
    else:
        QLAPI.createEnv({"envs": [new_env]}) and print("✅ 环境变量已创建")


def main():
    current_data = get_current_data()
    if not current_data:
        print("❌ 获取数据为空，跳过本次操作。")
        return

    last_data = get_cached_data()

    if last_data is None:
        print("🆕 环境变量不存在，准备创建并推送通知...")
        update_or_create_env(current_data)
        notify.send("[🛰 Hax Stats] 数据已缓存！", current_data)
    elif current_data != last_data:
        print("🔄 检测到数据变化，准备更新并推送通知...")
        update_or_create_env(current_data)
        notify.send("[🛰 Hax Stats] 数据已更新！", current_data)
    else:
        print("🔵 数据未发生变化，不更新环境变量。")


if __name__ == "__main__":
    main()
