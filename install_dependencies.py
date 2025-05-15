# -*- coding:utf-8 -*-
# -------------------------------
# @Author : github@wh1te3zzz https://github.com/wh1te3zzz/hax
# @Time : 2025-05-15 13:57:56
# hax监控脚本依赖，一次性脚本
# -------------------------------
"""
hax 监控依赖

cron: 1 1 1 1 1
const $ = new Env("hax 监控依赖");
"""
# install_dependencies.py

import sys
import subprocess
import os
import importlib.util


def check_module_installed(module_name):
    """检查模块是否已安装"""
    return importlib.util.find_spec(module_name) is not None


def install_package(package_name):
    """
    使用 pip 安装指定包
    
    :return: 是否安装成功 (bool)
    """
    try:
        print(f"📦 正在安装 {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 安装完成。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装 {package_name} 失败: {e}")
        return False


def read_requirements_file(filename="requirements.txt"):
    """
    读取 requirements.txt 文件中的依赖列表
    
    :return: 包名列表
    """
    if not os.path.exists(filename):
        print(f"⚠️ 错误：找不到 {filename} 文件")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    packages = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):  # 忽略空行和注释
            packages.append(line)

    return packages


def main():
    print("📄 正在读取 requirements.txt 中的依赖...")
    required_packages = read_requirements_file()

    # 分析哪些包未安装
    missing_packages = []
    for package in required_packages:
        # 去除版本号等信息，只取包名
        base_name = package.split("==")[0].split(">=")[0].split("<=")[0].strip()
        if not check_module_installed(base_name):
            missing_packages.append((package, base_name))

    if not missing_packages:
        print("🎉 所有必需的依赖已经安装，无需操作。")
        return

    print("\n🔍 检测到以下依赖尚未安装或需要更新：")
    for package, _ in missing_packages:
        print(f"- {package}")

    failed_packages = []

    print("\n🚀 开始自动安装缺失的依赖...\n")
    for package, base_name in missing_packages:
        success = install_package(package)
        if not success:
            failed_packages.append((package, base_name))

    # 输出最终结果
    if not failed_packages:
        print("\n✅ 所有依赖安装成功！")
    else:
        print("\n⚠️ 以下依赖安装失败，请手动安装：")
        for package, _ in failed_packages:
            print(f"- {package}")


if __name__ == "__main__":
    main()
