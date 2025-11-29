import scrapy
from scrapy_splash import SplashRequest
from datetime import datetime
from urllib.parse import urlparse
import re
from collections import Counter

class SmartSpider(scrapy.Spider):
    name = 'smart'
    
    start_urls = [
        'https://vnexpress.net/thoi-su',
        # Thêm bất kỳ URL nào
    ]
    
    max_pages = 5
    
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint='render.html',
                args={'wait': 2},
                meta={'category_url': url, 'page': 1}
            )
    
    def parse(self, response):
        """TỰ ĐỘNG phát hiện links bài viết"""
        category_url = response.meta['category_url']
        current_page = response.meta['page']
        
        # 1. TÌM TẤT CẢ LINKS trên trang
        all_links = response.css('a::attr(href)').getall()
        
        # 2. LỌC links có khả năng là bài viết
        article_links = self.detect_article_links(all_links, response.url)
        
        self.logger.info(
            f'🔍 Trang {current_page}: '
            f'Phát hiện {len(article_links)} bài viết từ {len(all_links)} links'
        )
        
        # 3. Crawl từng bài
        for link in article_links[:50]:  # Giới hạn 50 bài/trang
            full_url = response.urljoin(link)
            yield SplashRequest(
                url=full_url,
                callback=self.parse_article,
                endpoint='render.html',
                args={'wait': 1},
            )
        
        # 4. Tự động tìm trang tiếp theo
        if current_page < self.max_pages:
            next_page = self.detect_next_page(response, category_url, current_page)
            if next_page:
                self.logger.info(f'➡️  Tìm thấy trang {current_page + 1}: {next_page}')
                yield SplashRequest(
                    url=next_page,
                    callback=self.parse,
                    endpoint='render.html',
                    args={'wait': 2},
                    meta={'category_url': category_url, 'page': current_page + 1},
                    dont_filter=True
                )
    
    def detect_article_links(self, links, base_url):
        """
        TỰ ĐỘNG phát hiện links là bài viết
        Dựa trên pattern phổ biến
        """
        article_candidates = []
        
        for link in links:
            if not link or link.startswith('#'):
                continue
            
            link_lower = link.lower()
            
            # Loại bỏ các link rõ ràng KHÔNG phải bài viết
            skip_patterns = [
                'javascript:', 'mailto:', 'tel:',
                '.jpg', '.png', '.gif', '.pdf', '.zip',
                '/tag/', '/tags/', '/category/', '/categories/',
                '/page/', '/search', '/login', '/register',
                '/cart', '/checkout', '/account',
                'facebook.com', 'twitter.com', 'youtube.com',
                '/video/', '/album/', '/gallery/',
            ]
            
            if any(pattern in link_lower for pattern in skip_patterns):
                continue
            
            # Chỉ lấy link có dạng bài viết
            is_article = False
            
            # Pattern 1: Có năm trong URL (2020, 2021...)
            if re.search(r'/20\d{2}/', link):
                is_article = True
            
            # Pattern 2: Có ID số dài (thường là ID bài viết)
            if re.search(r'-\d{6,}', link):
                is_article = True
            
            # Pattern 3: URL dài với nhiều từ (slug bài viết)
            if link.count('-') >= 4:
                is_article = True
            
            # Pattern 4: Có đuôi .html, .htm
            if link.endswith(('.html', '.htm')):
                is_article = True
            
            # Pattern 5: Path có ít nhất 2 cấp (không phải trang chủ)
            path_depth = link.strip('/').count('/')
            if path_depth >= 2:
                is_article = True
            
            if is_article:
                article_candidates.append(link)
        
        return list(dict.fromkeys(article_candidates))
    
    def detect_next_page(self, response, base_url, current_page):
        """
        TỰ ĐỘNG phát hiện link trang tiếp theo
        """
        # Cách 1: Tìm nút "Next", "Trang sau", "»"
        next_links = response.css(
            'a.next::attr(href), '
            'a.next-page::attr(href), '
            'a[rel="next"]::attr(href), '
            'a:contains("Next")::attr(href), '
            'a:contains("Trang sau")::attr(href), '
            'a:contains("»")::attr(href)'
        ).get()
        
        if next_links:
            return response.urljoin(next_links)
        
        # Cách 2: Tìm pattern pagination phổ biến
        all_links = response.css('a::attr(href)').getall()
        
        for link in all_links:
            # Pattern: /page/2, /p/2, -p2, ?page=2
            patterns = [
                rf'/page/{current_page + 1}',
                rf'/p/{current_page + 1}',
                rf'-p{current_page + 1}',
                rf'\?page={current_page + 1}',
                rf'/trang-{current_page + 1}',
            ]
            
            for pattern in patterns:
                if re.search(pattern, link, re.I):
                    return response.urljoin(link)
        
        # Cách 3: Tự tạo URL (thử nhiều pattern)
        guess_urls = [
            f'{base_url}/page/{current_page + 1}',
            f'{base_url}-p{current_page + 1}',
            f'{base_url}?page={current_page + 1}',
            f'{base_url}/trang-{current_page + 1}.htm',
        ]
        
        # Trả về URL đầu tiên (có thể test trước)
        return guess_urls[0]
    
    def parse_article(self, response):
        """
        TỰ ĐỘNG trích xuất nội dung bài viết
        KHÔNG CẦN biết cấu trúc HTML
        """
        
        # 1. TÌM TIÊU ĐỀ - thường là thẻ h1 lớn nhất
        title = (
            response.css('h1::text').get() or
            response.css('meta[property="og:title"]::attr(content)').get() or
            response.css('title::text').get()
        )
        
        # 2. TÌM MÔ TẢ
        description = (
            response.css('meta[name="description"]::attr(content)').get() or
            response.css('meta[property="og:description"]::attr(content)').get()
        )
        
        # 3. TÌM NỘI DUNG - Lấy TẤT CẢ đoạn văn (p tag)
        all_paragraphs = response.css('p::text').getall()
        
        # Lọc bỏ các đoạn quá ngắn (< 50 ký tự)
        content_paragraphs = [
            p.strip() for p in all_paragraphs 
            if len(p.strip()) > 50
        ]
        
        content = ' '.join(content_paragraphs)
        
        # 4. TÌM NGÀY ĐĂNG - thử nhiều cách
        date = (
            response.css('time::attr(datetime)').get() or
            response.css('time::text').get() or
            response.css('meta[property="article:published_time"]::attr(content)').get() or
            self.extract_date_from_text(response.text)
        )
        
        # 5. TÌM TÁC GIẢ
        author = (
            response.css('meta[name="author"]::attr(content)').get() or
            self.extract_author(response)
        )
        
        # KIỂM TRA: Chỉ lưu nếu có đủ nội dung
        if not title or not content or len(content) < 200:
            self.logger.warning(f'⚠️  Bỏ qua (thiếu nội dung): {response.url}')
            return
        
        article = {
            'url': response.url,
            'domain': urlparse(response.url).netloc,
            'title': title.strip() if title else None,
            'description': description.strip() if description else None,
            'content': content.strip(),
            'author': author,
            'publish_date': date,
            'word_count': len(content.split()),
            'paragraph_count': len(content_paragraphs),
            'crawled_at': datetime.now().isoformat(),
        }
        
        self.logger.info(
            f'✅ {article["title"][:50]}... '
            f'({article["word_count"]} từ, {article["paragraph_count"]} đoạn)'
        )
        
        yield article
    
    def extract_date_from_text(self, html):
        """Tự động tìm ngày tháng trong HTML"""
        # Pattern: 28/11/2024, 2024-11-28, Nov 28, 2024...
        patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}\s+\w+\s+\d{4}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(0)
        
        return None
    
    def extract_author(self, response):
        """Tự động tìm tên tác giả"""
        # Tìm trong các pattern phổ biến
        author_keywords = ['author', 'tác giả', 'by', 'writer']
        
        for keyword in author_keywords:
            # Tìm trong class/id
            author = response.css(
                f'*[class*="{keyword}"]::text, '
                f'*[id*="{keyword}"]::text'
            ).get()
            if author and len(author.strip()) > 2:
                return author.strip()
        
        return None