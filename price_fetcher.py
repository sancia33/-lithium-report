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


def fetch_eastmoney_quote():
    """从东方财富API获取碳酸锂期货行情（最可靠的源）"""
    try:
        # 先搜索找到碳酸锂的secid
        search_url = "https://searchadapter.eastmoney.com/api/suggestion/get"
        params = {
            "input": "碳酸锂",
            "type": 14,
            "token": "D43BF722C8E33BDC906FB84D85E326E8",
        }
        resp = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        secids = []
        for item in data.get("Data", []):
            code = item.get("code", item.get("Code", ""))
            if "LC" in code.upper() or "碳酸锂" in item.get("name", item.get("Name", "")):
                secid = item.get("secid", item.get("SecID", ""))
                if secid:
                    secids.append(secid)

        # 如果没有搜索到，用已知的secid尝试
        known_ids = [
            "102.10280729",  # 碳酸锂主力 GFEX
            "0.10280729",
            "1.10280729",
        ]
        secids.extend(id for id in known_ids if id not in secids)

        # 用secid获取行情
        for secid in secids:
            try:
                quote_url = "https://push2.eastmoney.com/api/qt/stock.np/get"
                qparams = {
                    "secid": secid,
                    "fields": "f2,f3,f4,f12,f14,f15,f16,f17,f18,f19",
                }
                qresp = requests.get(quote_url, params=qparams, headers=HEADERS, timeout=10)
                qdata = qresp.json()
                qd = qdata.get("data", {})
                if qd and qd.get("f2"):
                    price = qd["f2"]
                    high = qd.get("f15", "")
                    low = qd.get("f16", "")
                    open_p = qd.get("f17", "")
                    pre_close = qd.get("f18", "")
                    change = qd.get("f4", "")
                    change_pct = qd.get("f3", "")
                    name = qd.get("f14", "碳酸锂")
                    return {
                        f"东方财富({name})": {
                            "price": price,
                            "change": change,
                            "change_pct": f"{change_pct}%" if change_pct else "",
                            "open": open_p,
                            "high": high,
                            "low": low,
                            "pre_close": pre_close,
                            "unit": "元/吨",
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    }
            except Exception:
                continue

        return {}
    except Exception as e:
        return {"东方财富": {"error": str(e)}}


def fetch_eastmoney_spot():
    """从东方财富获取碳酸锂现货价格"""
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            "fltt": "2",
            "fields": "f2,f3,f4,f12,f14",
            "secids": "102.10280729,102.LC0",
            "_": int(datetime.now().timestamp() * 1000),
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        items = data.get("data", {}).get("diff", []) if data.get("data") else []
        for item in items if isinstance(items, list) else []:
            price = item.get("f2")
            if price:
                name = item.get("f14", "碳酸锂期货")
                return {
                    f"东方财富({name})": {
                        "price": price,
                        "unit": "元/吨",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                }
        return {}
    except Exception as e:
        return {"东方财富现货": {"error": str(e)}}


def fetch_sina_futures():
    """从新浪财经获取碳酸锂期货价格"""
    try:
        headers = {**HEADERS, "Referer": "https://finance.sina.com.cn"}

        # 尝试不同的合约代码
        symbols = [
            "gfex_lc0", "gfex_lc2412", "gfex_lc2501",
            "GFEX_LC0", "gfex_LC0",
            "gzex_lc0", "gzex_lc2412",
        ]

        for sym in symbols:
            try:
                url = f"https://hq.sinajs.cn/list={sym}"
                resp = requests.get(url, headers=headers, timeout=10)
                resp.encoding = "gbk"
                text = resp.text.strip()

                if "not exist" in text.lower() or "404" in text:
                    continue

                match = re.search(r'"(.*?)"', text)
                if match:
                    fields = match.group(1).split(",")
                    if len(fields) >= 8 and fields[0] and fields[3]:
                        price = fields[3]
                        if price and price != "0.00":
                            change = fields[4] if len(fields) > 4 else ""
                            change_pct = fields[5] if len(fields) > 5 else ""
                            return {
                                "新浪财经(期货)": {
                                    "price": price,
                                    "change": change,
                                    "change_pct": change_pct,
                                    "unit": "元/吨",
                                    "raw": f"合约:{fields[0]} 开盘:{fields[1]} 最高:{fields[2]} 最低:{fields[3]}",
                                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                }
                            }
            except Exception:
                continue

        return {}
    except Exception as e:
        return {"新浪财经": {"error": str(e)}}


def fetch_100ppi():
    """从生意社获取碳酸锂价格"""
    try:
        sess = requests.Session()
        sess.headers.update(HEADERS)
        sess.get("https://www.100ppi.com", timeout=10)

        resp = sess.get("https://www.100ppi.com/monitor/", timeout=15)
        resp.encoding = "utf-8"

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()

        for line in text.split("\n"):
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


def get_all_prices():
    """聚合所有价格数据"""
    fetchers = [
        ("东方财富期货", fetch_eastmoney_quote),
        ("东方财富现货", fetch_eastmoney_spot),
        ("新浪财经", fetch_sina_futures),
        ("生意社", fetch_100ppi),
    ]

    result = {}
    errors = []
    for name, fetcher in fetchers:
        try:
            data = fetcher()
            if data:
                # 跳过只有error的返回
                has_real_data = any(
                    v.get("price") and v["price"] not in ("", "0", "0.00", "N/A")
                    for v in data.values()
                )
                if has_real_data:
                    result.update(data)
                    break
        except Exception as e:
            errors.append(f"{name}: {e}")

    if not result:
        result["提示"] = {
            "price": "今日暂未获取到价格数据",
            "detail": "; ".join(errors) if errors else "所有数据源均无返回，可能非交易日",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    return result
