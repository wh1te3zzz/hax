# wxpusher_notifier.py

import requests
import logging
import re

# ======================
# 配置区域（请根据你的WXPUSHER信息修改）
# ======================

# WXPUSHER接口地址，无需修改
WXPUSHER_API_URL = "http://wxpusher.zjiecode.com/api/send/message"
# 📢 替换为你的appToken
APP_TOKEN = "AT_XXXXXXXXXXXXX"
# 🔐 通知用户UID，支持多个用户
UIDS = ["UID_XXXXXXXXXXXXXX"]
# ☑️ 通知内容格式，1:文本, 2:HTML, 3:Markdown
CONTENT_TYPE = 1

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_summary(msg: str) -> str:
    """
    提取消息中第一个 [xxx] 标签的内容作为 summary。
    如果未找到 [xxx]，则回退到截取前11个字符（如果不足11个字符则全部截取）。
    """
    #logging.info(f"原始消息: {msg}")  # 记录原始消息
    
    if not msg or not msg.strip():
        return ""

    # 使用非贪婪正则提取第一个 [xxx] 中的内容
    match = re.search(r"$(.*?)$", msg)
    if match:
        content = match.group(1).strip()
        #logging.info(f"匹配到的标签内容: {content}")  # 记录匹配到的标签内容
        if content:
            return content

    # 否则截取前11个字符
    truncated_summary = msg[:11]
    #logging.info(f"未找到标签，使用前11个字符作为摘要: {truncated_summary}")  # 记录使用的摘要
    return truncated_summary


def wx_pusher_notify(msg: str):
    """
    发送微信推送通知。
    
    :param msg: 要发送的消息内容
    :return: 是否成功发送
    """
    summary = extract_summary(msg)

    payload = {
        "appToken": APP_TOKEN,
        "content": msg,
        "summary": summary if summary else "无摘要信息",  # 确保 summary 不为空
        "contentType": CONTENT_TYPE,
        "uids": UIDS
    }
    
    #logging.info(f"准备发送的消息内容: {payload}")  # 记录准备发送的消息内容

    try:
        response = requests.post(WXPUSHER_API_URL, json=payload, timeout=10)
        logging.info(f"推送成功: {response.text}")  # 记录推送成功的响应
        return True
    except Exception as e:
        logging.error(f"推送失败: {e}", exc_info=True)  # 记录推送失败的信息
        return False
