#!/usr/bin/env python3
"""碳酸锂价格与行业信息日报 - 主入口"""

import os
import sys
from datetime import datetime

from price_fetcher import get_all_prices
from news_fetcher import get_all_news
import report_generator
from feishu_notifier import send_card


def run():
    print("=" * 50)
    print(f"碳酸锂日报生成器 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 获取价格
    print("\n[1/3] 正在获取碳酸锂价格...")
    price_data = get_all_prices()
    for source, info in price_data.items():
        p = info.get("price", info.get("raw", "N/A"))
        if isinstance(p, list):
            p = "; ".join(p)
        detail = info.get("detail", info.get("error", ""))
        if detail:
            print(f"  {source}: {p} ({detail})")
        else:
            print(f"  {source}: {p}")

    # 2. 获取新闻
    print("\n[2/3] 正在检索行业信息...")
    news_data = get_all_news()
    for news in news_data[:5]:
        print(f"  - {news.get('title', '')[:60]}")

    # 3. 生成报告
    print("\n[3/3] 正在生成报告并推送...")
    report = report_generator.generate_report(price_data, news_data)

    # 保存报告到本地
    date_str = datetime.now().strftime("%Y%m%d")
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"lithium-report-{date_str}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  报告已保存: {report_path}")

    # 4. 推送到飞书
    print("\n  正在推送到飞书...")
    card = report_generator.generate_feishu_card(price_data, news_data)
    success = send_card(card)

    if success:
        print("\n✅ 日报任务完成!")
    else:
        print("\n⚠️ 日报已生成本地文件，但飞书推送未成功（请检查 FEISHU_WEBHOOK_URL 配置）")
        print(f"   报告位置: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(run())
