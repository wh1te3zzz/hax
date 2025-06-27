# dingtalk_calendar.py

import requests
import json
import os
from datetime import datetime, timedelta, timezone

APP_KEY = os.environ.get("DD_APP_KEY")
APP_SECRET = os.environ.get("DD_APP_SECRET")
USER_ID = os.environ.get("DD_USER_ID")
CALENDAR_ID = "primary"

def get_access_token(app_key, app_secret):
    url = f"https://oapi.dingtalk.com/gettoken?appkey={app_key}&appsecret={app_secret}"
    try:
        response = requests.get(url)
        result = response.json()
        if result.get("errcode") == 0:
            return result["access_token"]
        else:
            print("❌ 获取 access_token 失败：", result)
            return None
    except Exception as e:
        print("⚠️ 请求失败：", str(e))
        return None


def create_calendar_event(access_token, user_id, calendar_id, event_data):
    url = f"https://api.dingtalk.com/v1.0/calendar/users/{user_id}/calendars/{calendar_id}/events"
    headers = {
        'x-acs-dingtalk-access-token': access_token,
        'Content-Type': 'application/json'
    }

    payload = json.dumps(event_data, ensure_ascii=False).encode('utf-8')

    try:
        response = requests.post(url, headers=headers, data=payload)
        result = response.json()
        if response.status_code == 200 and "id" in result:
            #print("✅ 日程创建成功")
            #print(f"📅 日程 ID：{result['id']}")
            return True, result['id']
        else:
            print("❌ 创建日程失败：", result)
            return False, None
    except Exception as e:
        print("⚠️ 请求失败：", str(e))
        return False, None


def create_dingtalk_event(summary, description, start_time, end_time, is_all_day=False):
    """
    创建钉钉日程事件
    :param summary: 日程标题
    :param description: 描述内容
    :param start_time: 开始时间（datetime 对象）
    :param end_time: 结束时间（datetime 对象）
    :param is_all_day: 是否是全天事件
    :return: 成功返回True，否则返回False
    """
    if not all([APP_KEY, APP_SECRET, USER_ID]):
        print("请确保已设置 DD_APP_KEY, DD_APP_SECRET, 和 DD_USER_ID 环境变量")
        return False

    tz = timezone(timedelta(hours=8))  # UTC+8

    # 确保时间带有时区信息
    start_time = start_time.astimezone(tz)
    end_time = end_time.astimezone(tz)

    event_data = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Shanghai"
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Shanghai"
        },
        "isAllDay": is_all_day,
        "attendees": [
            {"id": USER_ID, "isOptional": False},
        ],
        "reminders": [
            {"method": "dingtalk", "minutes": 15}
        ]
    }

    token = get_access_token(APP_KEY, APP_SECRET)
    if not token:
        return False, None

    success, event_id= create_calendar_event(token, USER_ID, CALENDAR_ID, event_data)
    return success, event_id


def delete_calendar_event(access_token, user_id, calendar_id, event_id, push_notification=True):
    """
    删除钉钉日历中的事件。    
    :param access_token: 访问令牌
    :param user_id: 用户ID
    :param calendar_id: 日历ID
    :param event_id: 事件ID
    :param push_notification: 是否推送通知，默认为True
    :return: 成功返回True，否则返回False
    """
    url = f"https://api.dingtalk.com/v1.0/calendar/users/{user_id}/calendars/{calendar_id}/events/{event_id}"
    params = {
        'pushNotification': str(push_notification).lower()
    }
    headers = {
        'x-acs-dingtalk-access-token': access_token,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.delete(url, headers=headers, params=params)
        if response.status_code == 200:  # 假设成功删除返回的状态码是204 No Content
            print("✅ 旧日程删除成功")
            return True
        else:
            print(f"❌ 旧日程删除失败：状态码 {response.status_code}, 错误信息 {response.text}")
            return False
    except Exception as e:
        print("⚠️ 请求失败：", str(e))
        return False


def delete_dingtalk_event(event_id):
    """
    根据事件ID删除钉钉日程
    :param event_id: 要删除的日程事件ID
    :return: 成功返回True，否则返回False
    """
    if not all([APP_KEY, APP_SECRET, USER_ID]):
        print("请确保已设置 DD_APP_KEY, DD_APP_SECRET, 和 DD_USER_ID 环境变量")
        return False

    token = get_access_token(APP_KEY, APP_SECRET)
    if not token:
        return False

    success = delete_calendar_event(token, USER_ID, CALENDAR_ID, event_id)
    return success
