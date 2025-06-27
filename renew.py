# -*- coding:utf-8 -*-
# -------------------------------
# @Author : github@wh1te3zzz https://github.com/wh1te3zzz/hax
# @Time : 2025-06-27 10:47:16
# hax续期提醒脚本
# -------------------------------
"""
hax 手动续期提醒

cron: 59 * * * *
const $ = new Env("hax 手动续期提醒");
"""
# renew.py

from datetime import datetime, timedelta, timezone
import notify
from notify import send
from dingtalk_calendar import create_dingtalk_event, delete_dingtalk_event

# 格式化日期时间为字符串
def format_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# 获取当前时间
def now():
    return datetime.now(timezone(timedelta(hours=8)))  # 带时区

# 创建钉钉日程提醒
def create_renew_reminder_event(next_renew_time):
    """
    创建一个续期提醒日程
    :param next_renew_time: 下次建议续期时间（datetime 对象）
    """
    tz = timezone(timedelta(hours=8))

    # 设置开始和结束时间为 current_time + 4 天 的中午12点
    current_time = now()
    start_time = current_time + timedelta(days=4)
    start_time = start_time.replace(hour=12, minute=0, second=0, microsecond=0).astimezone(tz)
    end_time = start_time + timedelta(hours=1)

    summary = "⏰ 续期提醒"
    description = f"请在此时间前续期: {format_time(next_renew_time)}"

    print(f"📅 正在创建日程：{summary}")

    # 创建钉钉日程
    success, event_id = create_dingtalk_event(summary, description, start_time, end_time)
    if success:
        print("✅ 钉钉日程已成功创建！")
        # 更新环境变量中的 event_id
        update_or_create_env_event_id(event_id)
    else:
        print("❌ 创建钉钉日程失败，请检查参数或权限。")
    return success, event_id

# 更新或创建钉钉日程环境变量
def update_or_create_env_event_id(event_id,name = "DD_EVENT_ID",remarks = "钉钉日程事件ID",status=0):

    # 获取环境变量信息
    envs_response = QLAPI.getEnvs({"searchValue": name})
    data = envs_response.get("data", [])

    if data:
        # 存在 EVENT_ID，更新为新的 event_id
        item = data[0]
        old_event_id = item.get("value")

        # 可选：删除旧日程
        try:
            if old_event_id:
                delete_result = delete_dingtalk_event(old_event_id)
        except Exception as e:
            print(f"⚠️ 删除旧日程出错: {e}")
            return None

        # 更新环境变量
        item["value"] = event_id
        try:
            update_result = QLAPI.updateEnv({"env": item})
            print(f"✅ 已更新{remarks}为: {event_id}")
        except Exception as e:
            print(f"❌ 更新环境变量失败: {e}")
            return None
    else:
        # 不存在环境变量，创建一个新的
        print(f"⚠️ 未找到 {remarks}，准备创建...")

        new_env = {
            "name": name,
            "value": event_id,
            "remarks": remarks,
            "status": status,
        }

        try:
            create_result = QLAPI.createEnv({"envs": [new_env]})
            print(f"✅ 创建成功，更新{remarks}为: {event_id}")
        except Exception as e:
            print(f"❌ 创建环境变量失败: {e}")
            return None

# 更新或创建续期时间环境变量
def update_or_create_env_variable(name, remarks="Hax上次续期时间", status=0):
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

            # 创建钉钉日程提醒
            create_renew_reminder_event(next_renew_time)

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

            # 创建钉钉日程提醒
            create_renew_reminder_event(next_renew_time)

            return create_result
        except Exception as e:
            print(f"❌ 创建环境变量失败: {e}")
            return None


if __name__ == "__main__":
    result = update_or_create_env_variable("HAX_RENEW_TIME")
