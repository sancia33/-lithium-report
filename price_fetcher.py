import json
import requests
from datetime import datetime, timedelta


def fetch_sina_lc():
    """从新浪财经获取碳酸锂期货LC0的K线数据"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://finance.sina.com.cn",
        }
        url = (
            "https://stock.finance.sina.com.cn/futures/api/json_v2.php/"
            "InnerFuturesNewService.getDailyKLine?symbol=LC0"
        )
        resp = requests.get(url, headers=headers, timeout=15)
        data = json.loads(resp.text)

        if not data or len(data) < 2:
            return {"提示": {"price": "数据不足"}}

        today = data[-1]
        yesterday = data[-2]

        close = today["c"]
        open_p = today["o"]
        high = today["h"]
        low = today["l"]
        pre_close = yesterday["c"]
        change = round(float(close) - float(pre_close), 2)
        change_pct = round(change / float(pre_close) * 100, 2)

        return {
            "广期所(碳酸锂期货LC)": {
                "price": f"{float(close):,.0f}",
                "open": f"{float(open_p):,.0f}",
                "high": f"{float(high):,.0f}",
                "low": f"{float(low):,.0f}",
                "pre_close": f"{float(pre_close):,.0f}",
                "change": f"{change:+.0f}",
                "change_pct": f"{change_pct:+.2f}%",
                "unit": "元/吨",
                "date": today["d"],
                "volume": today.get("v", ""),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        }
    except Exception as e:
        return {"新浪财经": {"error": str(e)}}


def get_all_prices():
    """获取价格数据"""
    return fetch_sina_lc()
