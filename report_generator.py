from datetime import datetime


def generate_report(price_data, news_data):
    """生成Markdown格式的碳酸锂日报"""
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日")
    time_str = now.strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append(f"# 碳酸锂价格与行业信息日报")
    lines.append(f"")
    lines.append(f"**生成时间**: {time_str}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # 价格板块
    lines.append(f"## 一、碳酸锂价格概览")
    lines.append(f"")

    if price_data:
        lines.append(f"| 数据来源 | 价格 | 更新时间 |")
        lines.append(f"|---------|------|---------|")
        for source, info in price_data.items():
            price = info.get("price", info.get("raw", "N/A"))
            update_time = info.get("time", "N/A")
            if isinstance(price, list):
                price = "; ".join(price)
            lines.append(f"| {source} | {price} | {update_time} |")
    else:
        lines.append(f"暂无价格数据。")
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"")

    # 新闻板块
    lines.append(f"## 二、行业信息速览")
    lines.append(f"")

    if news_data:
        for i, news in enumerate(news_data, 1):
            title = news.get("title", "未知标题")
            url = news.get("url", "")
            source = news.get("source", "未知来源")
            if url:
                lines.append(f"{i}. [{title}]({url}) _({source})_")
            else:
                lines.append(f"{i}. {title} _({source})_")
    else:
        lines.append(f"暂无行业新闻。")
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"")

    # 市场简评
    lines.append(f"## 三、市场简评")
    lines.append(f"")

    price_note = ""
    if price_data:
        for source, info in price_data.items():
            p = info.get("price", "")
            if p and p != "N/A" and p != "获取失败":
                try:
                    val = float(p.replace(",", ""))
                    if val > 100000:
                        price_note = f"当前碳酸锂报价约 **{val/10000:.2f}万元/吨**，"
                    elif val > 0:
                        price_note = f"当前碳酸锂报价约 **{val:.2f}元/吨**，"
                except ValueError:
                    price_note = f"当前碳酸锂报价: {p}，"

    lines.append(
        f"{price_note}以上数据仅供参考，实际成交价格以各平台实时报价为准。"
        f"建议关注下游需求变化及锂矿供应端动态。"
    )
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"*报告自动生成于 {time_str}*")

    return "\n".join(lines)


def generate_feishu_card(price_data, news_data):
    """生成飞书消息卡片（JSON格式）"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    price_lines = []
    if price_data:
        for source, info in price_data.items():
            p = info.get("price", info.get("raw", "N/A"))
            if isinstance(p, list):
                p = "; ".join(p)
            price_lines.append(f"**{source}**: {p}")

    news_lines = []
    if news_data:
        for news in news_data[:5]:
            title = news.get("title", "")
            url = news.get("url", "")
            if url:
                news_lines.append(f"[{title}]({url})")
            else:
                news_lines.append(title)

    price_text = "\n".join(price_lines) if price_lines else "暂无数据"
    news_text = "\n".join(news_lines) if news_lines else "暂无数据"

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"碳酸锂日报 {date_str}"},
            "template": "blue",
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**📊 价格概览**\n{price_text}"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**📰 行业资讯**\n{news_text}"}},
            {"tag": "hr"},
            {
                "tag": "note",
                "element": {"tag": "plain_text", "content": f"报告自动生成于 {now.strftime('%Y-%m-%d %H:%M')}"},
            },
        ],
    }

    return card
