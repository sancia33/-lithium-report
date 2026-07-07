import json
import requests
from config import FEISHU_WEBHOOK_URL


def send_markdown(content):
    """发送Markdown文本消息到飞书"""
    if not FEISHU_WEBHOOK_URL or "your-webhook-id" in FEISHU_WEBHOOK_URL:
        print("[飞书] 未配置有效的 Webhook URL，跳过推送")
        print("[飞书] 请设置环境变量 FEISHU_WEBHOOK_URL")
        return False

    payload = {
        "msg_type": "interactive",
        "card": content,
    }

    try:
        resp = requests.post(
            FEISHU_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        result = resp.json()
        if result.get("code") == 0:
            print(f"[飞书] 消息推送成功")
            return True
        else:
            print(f"[飞书] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[飞书] 推送异常: {e}")
        return False


def send_card(card):
    """发送卡片消息到飞书"""
    return send_markdown(card)


def send_report(price_data, news_data, report_generator):
    """发送完整日报到飞书"""
    card = report_generator.generate_feishu_card(price_data, news_data)
    return send_card(card)
