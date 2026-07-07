from datetime import datetime


def _get_price_info(info):
    """提取价格信息文本"""
    parts = []
    p = info.get("price", "N/A")
    if p and p != "N/A":
        parts.append(f"最新价: {p}元/吨")
    for k, label in [("open", "开盘"), ("high", "最高"), ("low", "最低"), ("pre_close", "前收")]:
        v = info.get(k)
        if v:
            parts.append(f"{label}: {v}")
    change = info.get("change", "")
    change_pct = info.get("change_pct", "")
    if change and change_pct:
        parts.append(f"涨跌: {change} ({change_pct})")
    date = info.get("date", "")
    if date:
        parts.append(f"日期: {date}")
    return " | ".join(parts)


def generate_report(price_data, news_data):
    """生成Markdown格式的碳酸锂日报"""
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M")

    lines = [
        "# 碳酸锂价格与行业信息日报",
        "",
        f"**生成时间**: {time_str}",
        "",
        "---",
        "",
        "## 一、碳酸锂价格概览",
        "",
    ]

    if price_data:
        for source, info in price_data.items():
            price_text = _get_price_info(info)
            lines.append(f"### {source}")
            lines.append(f"")
            lines.append(f"{price_text}")
            lines.append(f"")
    else:
        lines.append("暂无价格数据。")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 二、行业信息速览")
    lines.append("")

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
        lines.append("暂无行业新闻。")
    lines.append("")

    lines.append("---")
    lines.append("")

    price_note = ""
    if price_data:
        for info in price_data.values():
            p = info.get("price", "")
            if p:
                try:
                    val = float(p.replace(",", ""))
                    price_note = f"当前碳酸锂主力合约报价约 **{val/10000:.2f}万元/吨**。"
                    break
                except ValueError:
                    price_note = f"当前碳酸锂报价: {p}。"
                    break

    lines.append("## 三、市场简评")
    lines.append("")
    lines.append(
        f"{price_note}以上数据仅供参考，实际成交价格以各平台实时报价为准。"
        f"建议关注下游需求变化及锂矿供应端动态。"
    )
    lines.append("")
    lines.append("---")
    lines.append(f"*报告自动生成于 {time_str}*")

    return "\n".join(lines)


def generate_feishu_card(price_data, news_data):
    """生成飞书消息卡片"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    price_lines = []
    if price_data:
        for source, info in price_data.items():
            price_text = _get_price_info(info)
            price_lines.append(f"**{source}**\n{price_text}")

    news_lines = []
    if news_data:
        for news in news_data[:5]:
            title = news.get("title", "")
            url = news.get("url", "")
            if url and title:
                news_lines.append(f"[{title}]({url})")
            elif title:
                news_lines.append(title)

    price_text = "\n\n".join(price_lines) if price_lines else "暂无数据"
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
