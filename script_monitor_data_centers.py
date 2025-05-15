# -*- coding:utf-8 -*-
# -------------------------------
# @Author : github@wh1te3zzz https://github.com/wh1te3zzz/hax
# @Time : 2025-05-15 13:57:56
# hax监控脚本，监控数据中心变化和当前可创建的区域
# -------------------------------
"""
hax 可开通区域

cron: 59 * * * *
const $ = new Env("hax 可开通区域");
"""
# script_monitor_data_centers.py

import re
import requests
from bs4 import BeautifulSoup

from cache_utils import save_current_data  # 可选：记录最新数据（不需要对比）
from wxpusher_notifier import wx_pusher_notify

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

URL_HAX_CREATE_VPS = "https://hax.co.id/create-vps"
URL_WOIDEN_CREATE_VPS = "https://woiden.id/create-vps"


class DataCenterMonitor:
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

    def parse_vps_centers(self, html_text, vir=False):
        """
        解析VPS中心信息。
        
        :param html_text: 页面HTML内容
        :param vir: 是否解析虚拟机选项
        :return: 解析后的中心信息字符串
        """
        soup = BeautifulSoup(html_text, "html.parser")
        options = soup.find_all("option", value=re.compile(r"^[A-Z]{2,}-"))
        centers = [opt.text for opt in options]

        if vir:
            processed = [(c.split(" (")[1].rstrip(")"), c.split(" (")[0]) for c in centers if " (" in c]
            result_dict = {}
            for key, val in processed:
                result_dict.setdefault(key, []).append(val)
            return "".join([f"★{k}★ " + ", ".join(v) + "\n" for k, v in result_dict.items()])

        return "\n".join(centers)

    def get_data_center(self, url, vir=False):
        """
        获取数据中心信息。
        
        :param url: 目标URL
        :param vir: 是否解析虚拟机选项
        :return: 解析后的数据中心信息
        """
        html = self.fetch_page(url)
        if not html:
            return ""
        return self.parse_vps_centers(html, vir)

    def main(self):
        vir_str = self.get_data_center(URL_HAX_CREATE_VPS, vir=True)
        woiden_str = self.get_data_center(URL_WOIDEN_CREATE_VPS)

        data_center = (
            "[🚩Available Centers / 可开通区域]\n"
            f'---------- <a href="{URL_HAX_CREATE_VPS}">Hax</a> ----------\n'
            f"{vir_str}"
            f'---------- <a href="{URL_WOIDEN_CREATE_VPS}">Woiden</a> ----------\n'
            f"{woiden_str}\n"
        )

        if vir_str.strip() or woiden_str.strip():
            print("检测到可开通区域信息，正在推送...")
            wx_pusher_notify(data_center)
        else:
            print("无可用开通区域，跳过推送。")


if __name__ == "__main__":
    monitor = DataCenterMonitor()
    monitor.main()
