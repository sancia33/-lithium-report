import os


FEISHU_WEBHOOK_URL = os.getenv(
    "FEISHU_WEBHOOK_URL",
    "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-id",
)

REPORT_TITLE = os.getenv("REPORT_TITLE", "碳酸锂价格与行业信息日报")

# 价格采集来源配置
PRICE_SOURCES = {
    "生意社": "https://www.100ppi.com/monitor/",
    "上海有色网": "https://www.smm.cn/lithium.html",
}

# 行业新闻搜索关键词
NEWS_KEYWORDS = [
    "碳酸锂 价格",
    "锂矿 行业",
    "锂电池 市场",
    "碳酸锂 期货",
    "lithium carbonate price",
]

# 新闻检索来源
NEWS_SOURCES = {
    "生意社": "https://www.100ppi.com/news/",
    "东方财富": "https://www.eastmoney.com/",
}
