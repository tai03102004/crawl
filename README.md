# Web Crawler

## Cài đặt

```bash
# Môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Thư viện
pip install scrapy scrapy-splash

# Chạy Splash
docker pull scrapinghub/splash
docker run -p 8050:8050 scrapinghub/splash

# Chạy crawler
# Crawl 10 bài
scrapy crawl smart -s CLOSESPIDER_ITEMCOUNT=10
```
