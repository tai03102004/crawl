import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_html(url):
    headers = {
        "User-Agent": 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"❌ Lỗi tải URL {url}: {e}")
        return None


def scrape_article_links(page_url):
    html = fetch_html(page_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Hỗ trợ nhiều selector để phòng cấu trúc thay đổi
    selectors = [
        "h3.entry-title a",
        "div.entry-title a",
        "article h2 a",
    ]

    link_elements = []
    for selector in selectors:
        link_elements = soup.select(selector)
        if link_elements:
            break

    if not link_elements:
        print("⚠️ Không tìm thấy link bài viết.")
        return []

    links = []
    for tag in link_elements:
        href = tag.get("href")
        if not href:
            continue
        if href.startswith("javascript") or href.startswith("#"):
            continue

        full_url = urljoin(page_url, href).rstrip("/")
        links.append(full_url)

    # Loại duplicate nhưng giữ thứ tự
    return list(dict.fromkeys(links))


# --- Chạy ---
parent_url = "https://vnexpress.net/"
article_urls = scrape_article_links(parent_url)

print("Found:", len(article_urls))
for i, u in enumerate(article_urls, 1):
    print(f"{i}. {u}")
