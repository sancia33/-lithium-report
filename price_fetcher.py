import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def fetch_100ppi_monitor():
    """从生意社监测页面获取碳酸锂价格"""
    try:
        resp = requests.get("https://www.100ppi.com/monitor/", headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # 尝试多种选择器匹配价格行
        for row in soup.select("tr, .list-item, .item, .price-item, [class*=price]"):
            text = row.get_text(strip=True)
            if "碳酸锂" in text:
                numbers = re.findall(r"[\d,]+\.?\d*", text)
                if numbers:
                    return {
                        "生意社(监测)": {
                            "price": numbers[0],
                            "unit": "元/吨",
                            "raw": text[:120],
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    }

        # 全页搜碳酸锂
        page_text = soup.get_text()
        for line in page_text.split("\n"):
            if "碳酸锂" in line and re.search(r"[\d,]+\.?\d*", line):
                nums = re.findall(r"[\d,]+\.?\d*", line)
                return {
                    "生意社(监测)": {
                        "price": nums[0],
                        "unit": "元/吨",
                        "raw": line.strip()[:120],
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                }

        return {}
    except Exception as e:
        return {"生意社(监测)": {"error": str(e)}}


def fetch_100ppi_commodity():
    """从生意社商品报价页获取"""
    try:
        resp = requests.get("https://www.100ppi.com/price/", headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.select("a[href]"):
            if "碳酸锂" in a.get_text(strip=True):
                href = a.get("href", "")
                if href.startswith("/"):
                    href = "https://www.100ppi.com" + href
                # 进详情页
                detail = requests.get(href, headers=HEADERS, timeout=15)
                detail.encoding = "utf-8"
                dsoup = BeautifulSoup(detail.text, "html.parser")
                text = dsoup.get_text()
                nums = re.findall(r"[\d,]+\.?\d*", text)
                if nums:
                    return {
                        "生意社(商品页)": {
                            "price": nums[0],
                            "unit": "元/吨",
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    }
                break
        return {}
    except Exception as e:
        return {"生意社(商品页)": {"error": str(e)}}


def fetch_gfex_futures():
    """从广州期货交易所获取碳酸锂期货价格"""
    try:
        url = "https://www.gfex.com.cn/gfex/gtll/futuresQuotation.shtml"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        for row in soup.select("tr"):
            cells = row.find_all("td")
            text = " ".join(c.get_text(strip=True) for c in cells)
            if "碳酸锂" in text or "LC" in text:
                nums = re.findall(r"[\d,]+\.?\d*", text)
                if nums:
                    return {
                        "广期所(碳酸锂期货)": {
                            "price": nums[0],
                            "raw": text[:200],
                            "unit": "元/吨",
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    }
        return {}
    except Exception as e:
        return {"广期所": {"error": str(e)}}


def fetch_eastmoney_futures():
    """从东方财富获取碳酸锂期货行情"""
    try:
        # 东方财富期货API - 碳酸锂期货合约LC
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            "fltt": "2",
            "fields": "f2,f3,f4,f12,f14",
            "secids": "1.10280729",  # 碳酸锂主力合约
            "_": int(datetime.now().timestamp() * 1000),
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get("data") and data["data"].get("diff"):
            item = data["data"]["diff"][0]
            price = item.get("f2", "N/A")
            return {
                "东方财富(碳酸锂期货)": {
                    "price": price,
                    "unit": "元/吨",
                    "raw": f"最新价: {price}",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            }
        return {}
    except Exception as e:
        return {"东方财富": {"error": str(e)}}


def fetch_eastmoney_spot():
    """从东方财富现货市场获取碳酸锂价格"""
    try:
        # 东方财富商品现货API
        url = "https://searchadapter.eastmoney.com/api/suggestion/get"
        params = {"input": "碳酸锂", "type": 14, "token": "D43BF722C8E33BDC906FB84D85E326E8"}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get("Data"):
            for item in data["Data"]:
                if "碳酸锂" in item.get("name", "") or "碳酸锂" in item.get("code", ""):
                    price = item.get("price", item.get("lastPrice", "N/A"))
                    return {
                        "东方财富(现货)": {
                            "price": price,
                            "unit": "元/吨",
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    }
        return {}
    except Exception as e:
        return {"东方财富(现货)": {"error": str(e)}}


def fetch_smm():
    """从上海有色网获取碳酸锂价格"""
    try:
        # SMM API
        url = "https://www.smm.cn/api/live/metals/list"
        params = {"category": "lithium", "locale": "zh_cn"}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for item in data if isinstance(data, list) else data.get("data", []):
                name = item.get("name", "")
                if "碳酸锂" in name:
                    price = item.get("price", item.get("latestPrice", "N/A"))
                    change = item.get("change", "")
                    return {
                        "SMM上海有色网": {
                            "price": price,
                            "change": change,
                            "unit": "元/吨",
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    }
        return {}
    except Exception as e:
        return {"SMM": {"error": str(e)}}


def get_all_prices():
    """聚合所有价格数据"""
    fetchers = [
        fetch_100ppi_monitor,
        fetch_100ppi_commodity,
        fetch_gfex_futures,
        fetch_eastmoney_futures,
        fetch_eastmoney_spot,
        fetch_smm,
    ]

    result = {}
    for fetcher in fetchers:
        try:
            data = fetcher()
            if data:
                result.update(data)
        except Exception:
            pass

    return result
