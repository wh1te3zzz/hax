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
# script_monitor_hax_stats.py

import requests
from bs4 import BeautifulSoup

from cache_utils import load_last_data, save_current_data
from wxpusher_notifier import wx_pusher_notify

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

URL_HAX_SERVER_INFO = "https://hax.co.id/data-center"
CACHE_KEY = "hax_server_info"


class HaxStatsMonitor:
    @staticmethod
    def fetch_page(url):
        """
        请求页面内容。
        
        :param url: 目标URL
        :return: 页面内容或空字符串（请求失败时）
        """
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            res.raise_for_status()
            return res.text
        except Exception as e:
            print(f"请求失败: {e}")
            return ""

    def parse_server_info(self, html_text):
        """
        解析服务器开通数据。
        
        :param html_text: 页面HTML内容
        :return: 解析后的内容字符串
        """
        soup = BeautifulSoup(html_text, "html.parser")
        zone_list = [x.text for x in soup("h5", class_="card-title mb-4")]
        sum_list = [x.text for x in soup("h1", class_="card-text")]

        result = {}
        for zone_info, count_info in zip(zone_list, sum_list):
            parts = zone_info.split("-", 1)
            region = parts[0].lstrip("./")
            suffix = f"{parts[1]}({count_info.rstrip(' VPS')}♝)" if len(parts) > 1 else count_info
            result.setdefault(region, []).append(suffix)

        lines = [f">>{region}-" + ", ".join(values) + "\n" for region, values in result.items()]
        return "".join(lines)

    def get_server_info(self):
        """
        获取服务器开通数据。
        
        :return: 解析后的服务器开通数据
        """
        html = self.fetch_page(URL_HAX_SERVER_INFO)
        if not html:
            return ""
        return self.parse_server_info(html)

    def main(self):
        current_data = self.get_server_info()
        if not current_data:
            print("获取数据为空，跳过本次检查。")
            return

        last_data = load_last_data(CACHE_KEY)
        if current_data != last_data:
            print("检测到数据变化，准备推送通知...")
            wx_pusher_notify(f"[🛰Hax Stats / Hax 已开通数据]\n{current_data}")
            save_current_data(CACHE_KEY, current_data)
        else:
            print("数据未发生变化，不推送通知。")


if __name__ == "__main__":
    monitor = HaxStatsMonitor()
    monitor.main()
