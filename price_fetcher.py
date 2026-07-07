import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup


def fetch_100ppi_price():
    """从生意社获取碳酸锂价格"""
    try:
        url = "https://www.100ppi.com/monitor/"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        price_data = {}
        for item in soup.select(".list-item, .item, tr"):
            text = item.get_text(strip=True)
            if "碳酸锂" in text:
                numbers = re.findall(r"[\d,]+\.?\d*", text)
                price_data["生意社"] = {
                    "raw": text[:100],
                    "price": numbers[0] if numbers else "N/A",
                    "unit": "元/吨",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                break

        if not price_data:
            price_data["生意社"] = {"raw": "未找到碳酸锂价格数据", "price": "N/A", "unit": "", "time": datetime.now().strftime("%Y-%m-%d %H:%M")}

        return price_data
    except Exception as e:
        return {"生意社": {"error": str(e), "price": "获取失败", "time": datetime.now().strftime("%Y-%m-%d %H:%M")}}


def fetch_alternative_prices():
    """从多个备用源获取价格"""
    results = {}
    sources = {
        "SMM上海有色网": "https://www.smm.cn/lithium.html",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    for name, url in sources.items():
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text()
            if "碳酸锂" in text:
                lines = [l.strip() for l in text.split("\n") if "碳酸锂" in l]
                results[name] = {
                    "raw": lines[:3] if lines else "N/A",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            else:
                results[name] = {"raw": "未找到相关数据", "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
        except Exception as e:
            results[name] = {"error": str(e), "time": datetime.now().strftime("%Y-%m-%d %H:%M")}

    return results


def get_all_prices():
    """聚合所有价格数据"""
    result = {}
    result.update(fetch_100ppi_price())
    result.update(fetch_alternative_prices())
    return result
