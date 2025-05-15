# dingtalk_notifier.py

import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import logging

# ======================
# 配置区域（请根据你的钉钉机器人信息修改）
# ======================

# 📢 替换为你的钉钉机器人 Webhook 地址
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=你的access_token"

# 🔐 加签密钥（如果开启了“加签”功能，请填写；否则可留空或设为 None）
DINGTALK_SECRET = "SEC你的加签密钥"

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DingTalkBot:
    def __init__(self, webhook_url: str = DINGTALK_WEBHOOK, secret: str = DINGTALK_SECRET):
        """
        初始化钉钉机器人。
        
        :param webhook_url: 钉钉机器人的 Webhook 地址
        :param secret: 加签密钥（如果启用了加签验证）
        """
        self.webhook_url = webhook_url
        self.secret = secret

    def _get_sign(self) -> dict:
        """
        如果设置了 secret，则生成钉钉要求的 timestamp 和 sign。
        
        :return: 包含 timestamp 和 sign 的字典参数
        """
        if not self.secret:
            return {}

        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        return {
            'timestamp': timestamp,
            'sign': sign
        }

    def send_markdown(self, title: str, text: str):
        """
        发送 Markdown 格式的消息到钉钉群。

        :param title: 消息标题（显示在通知栏）
        :param text: Markdown 内容正文
        :return: 是否发送成功
        """
        params = self._get_sign()
        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            }
        }

        try:
            response = requests.post(self.webhook_url, params=params, json=data, headers=headers, timeout=10)
            logging.info(f"钉钉推送成功: {response.text}")
            return True
        except Exception as e:
            logging.error(f"钉钉推送失败: {e}")
            return False
