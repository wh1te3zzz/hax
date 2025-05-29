# -*- coding:utf-8 -*-
# -------------------------------
# @Author : github@wh1te3zzz https://github.com/wh1te3zzz/hax
# @Time : 2025-05-29 09:53:56
# hax监控脚本，监控数据中心变化和当前可创建的区域
# -------------------------------
"""
hax 可开通区域

cron: 59 * * * *
const $ = new Env("hax 可开通区域");
"""
# monitor_available_centers.py

import re
import requests
from bs4 import BeautifulSoup
from notify import send

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

URL_HAX_CREATE_VPS = "https://hax.co.id/create-vps"
URL_WOIDEN_CREATE_VPS = "https://woiden.id/create-vps"

ENV_NAME = "HAX_AVAILABLE"  # 青龙环境变量名称


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

    # =================== 环境变量操作模块 START =================== #

    def get_cached_data(self):
        """从青龙环境中获取缓存的数据"""
        envs_response = QLAPI.getEnvs({"searchValue": ENV_NAME})
        data = envs_response.get("data", [])
        return data[0]["value"] if data else None

    def update_or_create_env(self, value):
        """更新或创建环境变量"""
        envs = QLAPI.getEnvs({"searchValue": ENV_NAME}).get("data", [])
        new_env = {
            "name": ENV_NAME,
            "value": value,
            "remarks": "数据中心信息缓存"
        }

        if envs:
            item = envs[0]
            item["value"] = value
            QLAPI.updateEnv({"env": item}) and print("✅ 环境变量已更新")
        else:
            QLAPI.createEnv({"envs": [new_env]}) and print("✅ 环境变量已创建")

    # =================== 环境变量操作模块 END =================== #

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

        last_data = self.get_cached_data()

        if data_center.strip() == "":
            print("❌ 当前无可用开通区域。")
            return

        if last_data != data_center:
            print("🔄 检测到数据变化，正在更新缓存并推送通知...")
            self.update_or_create_env(data_center)
            send("🌐【数据中心信息更新】", data_center)
        else:
            print("🔵 数据未发生变化，无需更新。")


if __name__ == "__main__":
    monitor = DataCenterMonitor()
    monitor.main()
