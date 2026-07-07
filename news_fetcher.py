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


def fetch_smm_news():
    """从SMM获取锂行业新闻"""
    try:
        url = "https://www.smm.cn/news/lithium"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        news = []
        for a in soup.select("a[href*='news'], a[title]"):
            title = a.get("title") or a.get_text(strip=True)
            href = a.get("href", "")
            if not title:
                continue
            if any(kw in title for kw in ["碳酸锂", "锂", "锂矿", "锂电池", "lithium"]):
                if href and not href.startswith("http"):
                    href = "https://www.smm.cn" + href
                news.append({"title": title, "url": href, "source": "SMM"})
        return news[:5]
    except Exception:
        return []


def fetch_eastmoney_news():
    """从东方财富API获取碳酸锂新闻"""
    try:
        url = "https://search-api-web.eastmoney.com/search/jsonp"
        params = {
            "param": '{"uid":"","keyword":"碳酸锂 价格","type":["cmsArticleWebOld"],"page":1,"size":10}',
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        news = []
        if resp.status_code == 200:
            try:
                data = resp.json()
                articles = data if isinstance(data, list) else data.get("data", []) if isinstance(data, dict) else []
                for art in articles[:10]:
                    title = art.get("title", "").replace("<em>", "").replace("</em>", "")
                    news_url = art.get("url", art.get("articleUrl", ""))
                    if title:
                        news.append({
                            "title": title,
                            "url": news_url,
                            "source": "东方财富",
                        })
            except Exception:
                pass
        return news
    except Exception:
        return []


def fetch_eastmoney_article_list():
    """从东方财富锂电板块获取新闻"""
    try:
        url = "https://finance.eastmoney.com/a/czqyw.html"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        news = []
        for a in soup.select("a[href*='article'], a[href*='news']"):
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if not title or len(title) < 5:
                continue
            if any(kw in title for kw in ["碳酸锂", "锂", "锂电", "锂电池", "锂矿", "新能源"]):
                news.append({"title": title, "url": href, "source": "东方财富"})
        return news[:5]
    except Exception:
        return []


def get_all_news():
    """聚合所有新闻"""
    all_news = []
    for fetcher in [fetch_eastmoney_news, fetch_smm_news, fetch_eastmoney_article_list]:
        try:
            all_news.extend(fetcher() or [])
        except Exception:
            pass

    seen = set()
    unique = []
    for n in all_news:
        key = n["title"][:30]
        if key not in seen:
            seen.add(key)
            unique.append(n)
    return unique[:15]
