import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def fetch_100ppi_news():
    """从生意社获取碳酸锂相关新闻"""
    try:
        url = "https://www.100ppi.com/news/"
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

        news_list = []
        for link in soup.select("a[href*='news'], a[href*='detail'], .news-title a, .list-item a"):
            title = link.get_text(strip=True)
            href = link.get("href", "")
            if "碳酸锂" in title or "锂" in title:
                if href and not href.startswith("http"):
                    href = "https://www.100ppi.com" + href
                news_list.append({
                    "title": title,
                    "url": href,
                    "source": "生意社",
                })

        return news_list[:10]
    except Exception as e:
        return [{"title": f"生意社获取失败: {e}", "url": "", "source": "生意社"}]


def fetch_eastmoney_news():
    """从东方财富获取碳酸锂相关新闻"""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.eastmoney.com/",
        }

        news_list = []
        search_url = "https://search-api-web.eastmoney.com/search/jsonp"
        params = {
            "param": '{"uid":"","keyword":"碳酸锂","type":["cmsArticleWebOld"],"page":1,"size":10}',
        }

        resp = requests.get(search_url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            try:
                data = resp.json()
                articles = data.get("data", []) if isinstance(data, dict) else []
                for art in articles[:10]:
                    news_list.append({
                        "title": art.get("title", "").replace("<em>", "").replace("</em>", ""),
                        "url": art.get("url", ""),
                        "source": "东方财富",
                    })
            except Exception:
                pass

        return news_list
    except Exception as e:
        return [{"title": f"东方财富获取失败: {e}", "url": "", "source": "东方财富"}]


def fetch_google_news():
    """从Google News获取锂行业新闻（备选）"""
    try:
        url = "https://news.google.com/rss/search?q=lithium+carbonate+price&hl=en-US&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "xml")

        news_list = []
        for item in soup.select("item")[:10]:
            title = item.find("title")
            link = item.find("link")
            if title and link:
                news_list.append({
                    "title": title.text.strip(),
                    "url": link.text.strip(),
                    "source": "Google News",
                })

        return news_list
    except Exception as e:
        return [{"title": f"Google News获取失败: {e}", "url": "", "source": "Google News"}]


def get_all_news():
    """聚合所有新闻"""
    all_news = []
    for fetcher in [fetch_100ppi_news, fetch_eastmoney_news, fetch_google_news]:
        try:
            all_news.extend(fetcher())
        except Exception:
            pass

    seen = set()
    unique = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            unique.append(n)

    return unique[:20]
