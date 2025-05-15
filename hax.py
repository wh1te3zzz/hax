# -*- coding:utf-8 -*-
# -------------------------------
# @Author : github@wh1te3zzz https://github.com/wh1te3zzz/hax
# @Time : 2025-05-15 13:57:56
# hax监控脚本，监控数据中心变化和当前可创建的区域，不启用通知版本
# -------------------------------
"""
hax 监控

cron: 59 * * * *
const $ = new Env("hax 监控");
"""
import re
import logging

import requests
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 常量定义
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
}

URL_HAX_SERVER_INFO = "https://hax.co.id/data-center"
URL_HAX_CREATE_VPS = "https://hax.co.id/create-vps"
URL_WOIDEN_CREATE_VPS = "https://woiden.id/create-vps"


class Hax:
    @staticmethod
    def fetch_page(url: str) -> str:
        """获取网页内容"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"请求失败: {url}，错误: {e}")
            return ""

    def parse_server_info(self, html_text: str) -> dict:
        """解析服务器信息（区域与数量）"""
        soup = BeautifulSoup(html_text, "html.parser")
        zone_list = [x.text for x in soup("h5", class_="card-title mb-4")]
        sum_list = [x.text for x in soup("h1", class_="card-text")]

        result = {}
        for zone_info, count_info in zip(zone_list, sum_list):
            parts = zone_info.split("-", 1)
            region = parts[0].lstrip("./")
            suffix = f"{parts[1]}({count_info.rstrip(' VPS')}♝)" if len(parts) > 1 else count_info

            result.setdefault(region, []).append(suffix)

        return result

    def get_server_info(self) -> str:
        """获取并格式化服务器统计信息"""
        html_text = self.fetch_page(URL_HAX_SERVER_INFO)
        if not html_text:
            return ""

        info_dict = self.parse_server_info(html_text)
        lines = [f">>{region}-" + ", ".join(values) + "\n" for region, values in info_dict.items()]
        return "".join(lines)

    def parse_vps_centers(self, html_text: str, vir: bool = False) -> str:
        """解析 VPS 区域选项"""
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

    def get_data_center(self, url: str, vir: bool = False) -> str:
        """获取数据中心信息"""
        html_text = self.fetch_page(url)
        if not html_text:
            return ""
        return self.parse_vps_centers(html_text, vir)

    def main(self) -> str:
        hax_str = self.get_server_info()
        hax_stat = f"[🛰Hax Stats / Hax 开通数据]\n{hax_str}\n"

        vir_str = self.get_data_center(URL_HAX_CREATE_VPS, vir=True)
        woiden_str = self.get_data_center(URL_WOIDEN_CREATE_VPS)

        data_center = (
            f"[🚩Available Centers / 可开通区域]\n"
            f'---------- <a href="{URL_HAX_CREATE_VPS}">Hax</a> ----------\n'
            f"{vir_str}"
            f'---------- <a href="{URL_WOIDEN_CREATE_VPS}">Woiden</a> ----------\n'
            f"{woiden_str}\n"
        )

        return hax_stat + data_center


if __name__ == "__main__":
    hax = Hax()
    try:
        result = hax.main()
        logging.info(result)
    except Exception as e:
        logging.error(f"执行主程序出错: {e}")
