import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin # Để xử lý trường hợp link tương đối

def scrape_article_links(page_url):
    """
    Cào tất cả các link bài viết từ một trang tin tức cha.
    Trang này cụ thể là solarbk.vn/tin-tuc
    """
    all_links = []
    try:
        # 1. Tải nội dung HTML của trang cha
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(page_url, headers=headers, timeout=10)
        response.raise_for_status() # Báo lỗi nếu request thất bại

        # 2. Phân tích HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. Tìm tất cả các thẻ chứa link bài viết
        #    Qua kiểm tra, các link bài viết trên trang này nằm trong thẻ <a>
        #    bên trong một thẻ <h3> có class là "entry-title"
        #    Đây là "Selector" CSS: 'h3.entry-title a'
        link_elements = soup.select('h3.entry-title a')

        if not link_elements:
            print("Không tìm thấy link nào với selector 'h3.entry-title a'.")
            return []

        # 4. Lặp qua các thẻ và lấy đường link (href)
        for link_tag in link_elements:
            href = link_tag.get('href')
            if href:
                # Chuyển link tương đối (vd: /tin-tuc/bai-viet) thành link tuyệt đối
                full_url = urljoin(page_url, href)
                all_links.append(full_url)
        
        # 5. Xóa các link trùng lặp (nếu có) nhưng vẫn giữ nguyên thứ tự
        ordered_unique_links = list(dict.fromkeys(all_links))
        return ordered_unique_links

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải trang {page_url}: {e}")
        return []

# --- Chạy chương trình ---
parent_url = "https://solarbk.vn/tin-tuc"
article_urls = scrape_article_links(parent_url)

if article_urls:
    print(f"Đã tìm thấy {len(article_urls)} link bài viết (theo thứ tự mới nhất):")
    for i, url in enumerate(article_urls):
        print(f"{i+1}. {url}")
else:
    print("Không tìm thấy link bài viết nào.")