import re
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def fetch_sina_futures():
    """从新浪财经获取碳酸锂期货主力合约价格（最稳定的源）"""
    try:
        url = "https://hq.sinajs.cn/list=gfex_lc0"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = "gbk"
        text = resp.text

        # 返回格式: var hq_str_gfex_lc0="名称,开盘,最高,最低,最新,涨跌,..."
        match = re.search(r'"(.*?)"', text)
        if match:
            fields = match.group(1).split(",")
            if len(fields) >= 10:
                name = fields[0]
                price = fields[3]  # 最新价
                change = fields[4]  # 涨跌
                change_pct = fields[5]  # 涨跌幅
                open_price = fields[1]
                high = fields[2]
                low = fields[3]
                return {
                    "广期所(碳酸锂期货主力)": {
                        "price": price,
                        "change": change,
                        "change_pct": change_pct,
                        "unit": "元/吨",
                        "raw": f"开盘{open_price} 最高{high} 最低{low}",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                }
        return {}
    except Exception as e:
        return {"新浪财经(期货)": {"error": str(e)}}


def fetch_sina_spot():
    """从新浪财经获取碳酸锂现货价格"""
    try:
        symbol_candidates = ["gfex_lc0", "gfex_lc2409", "gfex_lc2501"]
        for sym in symbol_candidates:
            try:
                url = f"https://hq.sinajs.cn/list={sym}"
                resp = requests.get(url, headers=HEADERS, timeout=10)
                resp.encoding = "gbk"
                text = resp.text
                match = re.search(r'"(.*?)"', text)
                if match:
                    fields = match.group(1).split(",")
                    if len(fields) >= 8 and fields[0]:
                        price = fields[3] if fields[3] else fields[1]
                        if price and price != "0.00":
                            return {
                                "新浪财经(碳酸锂)": {
                                    "price": price,
                                    "unit": "元/吨",
                                    "raw": f"合约:{fields[0]}",
                                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                }
                            }
            except Exception:
                continue
        return {}
    except Exception as e:
        return {"新浪财经": {"error": str(e)}}


def fetch_100ppi_with_session():
    """从生意社监测页获取价格（带session/cookies）"""
    try:
        sess = requests.Session()
        sess.headers.update(HEADERS)
        # 先访问首页获取cookie
        sess.get("https://www.100ppi.com", timeout=10)
        resp = sess.get("https://www.100ppi.com/monitor/", timeout=15)
        resp.encoding = "utf-8"

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")

        # 找所有包含"碳酸锂"的文本行
        for elem in soup.find_all(["td", "th", "span", "div", "li", "a"]):
            text = elem.get_text(strip=True)
            if "碳酸锂" in text:
                parent = elem.parent
                parent_text = parent.get_text(strip=True) if parent else text
                nums = re.findall(r"[\d,]+\.?\d*", parent_text)
                if nums:
                    return {
                        "生意社": {
                            "price": nums[0],
                            "unit": "元/吨",
                            "raw": parent_text[:150],
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    }

        # fallback: 全页搜索
        page_text = soup.get_text()
        for line in page_text.split("\n"):
            if "碳酸锂" in line:
                nums = re.findall(r"[\d,]+\.?\d*", line)
                if nums:
                    return {
                        "生意社": {
                            "price": nums[0],
                            "unit": "元/吨",
                            "raw": line.strip()[:150],
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    }
        return {}
    except Exception as e:
        return {"生意社": {"error": str(e)}}


def fetch_google_search():
    """通过Google搜索获取碳酸锂价格"""
    try:
        url = "https://www.google.com/search"
        params = {"q": "碳酸锂价格 2026", "hl": "zh-CN"}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        snippets = []
        for div in soup.select("div[class*='BNeawe']"):
            text = div.get_text(strip=True)
            if "碳酸锂" in text and re.search(r"[\d,]+\.?\d*", text):
                snippets.append(text)

        for s in snippets[:3]:
            nums = re.findall(r"[\d,]+\.?\d*", s)
            if nums:
                return {
                    "Google搜索": {
                        "price": nums[0],
                        "unit": "元/吨",
                        "raw": s[:120],
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                }
        return {}
    except Exception as e:
        return {"Google": {"error": str(e)}}


def get_all_prices():
    """聚合所有价格数据"""
    fetchers = [
        ("新浪期货", fetch_sina_futures),
        ("新浪现货", fetch_sina_spot),
        ("生意社", fetch_100ppi_with_session),
        ("Google", fetch_google_search),
    ]

    result = {}
    errors = []
    for name, fetcher in fetchers:
        try:
            data = fetcher()
            if data and any(
                v.get("price") or v.get("error") for v in data.values()
            ):
                result.update(data)
        except Exception as e:
            errors.append(f"{name}: {e}")

    if not result:
        result["提示"] = {
            "price": "暂未获取到价格数据",
            "detail": "; ".join(errors) if errors else "所有数据源均无返回",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    return result
