# Scrapy settings for bilingualcrawl project

BOT_NAME = 'bilingualcrawl'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

# User Agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # Tắt để crawl dễ hơn

# Concurrent requests
CONCURRENT_REQUESTS = 8

# Download delay
DOWNLOAD_DELAY = 1

# Splash settings
SPLASH_URL = "http://localhost:8050"
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Spider middlewares
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# Downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Export settings
FEEDS = {
    'articles.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 4,
    },
    'articles.csv': {
        'format': 'csv',
        'encoding': 'utf8',
    }
}

# Log level
LOG_LEVEL = 'INFO'