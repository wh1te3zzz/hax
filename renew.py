# -*- coding:utf-8 -*-
# -------------------------------
# @Author : github@wh1te3zzz https://github.com/wh1te3zzz/hax
# @Time : 2025-05-16 14:47:16
# hax续期提醒脚本
# -------------------------------
"""
hax 手动续期提醒

cron: 59 * * * *
const $ = new Env("hax 手动续期提醒");
"""
# renew.py

from datetime import datetime, timedelta
# 导入通知模块（notify.py）
import notify
from notify import send

# 格式化日期时间为字符串
def format_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# 获取当前时间
def now():
    return datetime.now()

# 更新或创建环境变量
def update_or_create_env_variable(name, remarks="HAX上次续期时间", status=0):
    # 获取当前时间作为本次续期时间
    current_time = now()
    formatted_current_time = format_time(current_time)

    # 获取环境变量信息
    envs_response = QLAPI.getEnvs({"searchValue": name})
    data = envs_response.get("data", [])

    if data:
        # 存在环境变量，更新 value 为当前时间
        item = data[0]
        old_time_str = item.get("value")
        print(f"🕒 上次续期时间为: {old_time_str}")

        try:
            old_time = datetime.strptime(old_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("⚠️ 环境变量中的时间格式错误，将使用当前时间重新设置")
            old_time = current_time

        # 设置新的续期时间为当前时间
        item["value"] = formatted_current_time

        # 计算请在此时间前续期：+5天，固定凌晨1点
        renew_before_time = old_time + timedelta(days=5)
        renew_before_time = renew_before_time.replace(hour=1, minute=0, second=0, microsecond=0)
        print(f"⏳ 请在此时间前续期: {format_time(renew_before_time)}")

        # 更新环境变量
        try:
            update_result = QLAPI.updateEnv({"env": item})
            print(f"✅ 已更新本次续期时间为: {formatted_current_time}")

            # 下次续期时间：当前时间 +5 天，凌晨 1 点
            next_renew_time = current_time + timedelta(days=5)
            next_renew_time = next_renew_time.replace(hour=1, minute=0, second=0, microsecond=0)
            print(f"👉 下次此时间前续期: {format_time(next_renew_time)}")

            # 发送通知
            title = "⏰ 续期时间已更新"
            content = (
                f"📅 本次更新续期时间: {formatted_current_time}\n"
                f"📆 下次建议续期时间: {format_time(next_renew_time)}"
            )
            send(title, content)

            return update_result
        except Exception as e:
            print(f"❌ 更新环境变量失败: {e}")
            return None

    else:
        # 不存在环境变量，创建一个新的
        print(f"⚠️ 未找到 {remarks}，准备创建...")

        new_env = {
            "name": name,
            "value": formatted_current_time,
            "remarks": remarks,
            "status": status,
        }

        try:
            create_result = QLAPI.createEnv({"envs": [new_env]})
            print(f"✅ 创建成功，更新本次续期时间为: {formatted_current_time}")

            # 下次续期时间：当前时间 +5 天，凌晨 1 点
            next_renew_time = current_time + timedelta(days=5)
            next_renew_time = next_renew_time.replace(hour=1, minute=0, second=0, microsecond=0)
            print(f"👉 下次此时间前续期: {format_time(next_renew_time)}")

            # 发送通知
            title = "🆕 续期时间已创建"
            content = (
                f"📅 本次更新续期时间: {formatted_current_time}\n"
                f"📆 下次建议续期时间: {format_time(next_renew_time)}"
            )
            send(title, content)

            return create_result
        except Exception as e:
            print(f"❌ 创建环境变量失败: {e}")
            return None

if __name__ == "__main__":
    result = update_or_create_env_variable("HAX_RENEW_TIME")
