from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import json
from datetime import datetime

driver = webdriver.Chrome()

source_url = "https://timkiem.vnexpress.net/?search_f=title,tag_list&q=OpenAI&media_type=all&fromdate=0&todate=0&latest=&cate_code=&date_format=month&"

driver.get(source_url)

# Lấy thông tin chung
source_platform = driver.find_element(By.CSS_SELECTOR, "a.logo").get_attribute("title")
search_words = driver.find_element(By.ID, "search_q").get_attribute("value")

select = Select(driver.find_element(By.ID, "thoigian"))
time_filter = select.first_selected_option.text

scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Khởi tạo cấu trúc dữ liệu
data = {
    "source_platform": source_platform,
    "source_url": source_url,
    "scraped_at": scraped_at,
    "search_words": search_words,
    "time_filter": time_filter,
    "post_detail": []
}

print("Source platform:", source_platform)
print("Source URL:", source_url)
print("Scraped at:", scraped_at)
print("Search words:", search_words)
print("Time filter:", time_filter)
print("-" * 40)

wait = WebDriverWait(driver, 10)
articles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.item-news")))

# Lấy danh sách bài viết từ trang tìm kiếm
posts_info = []
for article in articles:
    title_els = article.find_elements(By.CSS_SELECTOR, 'h3.title-news')
    description_els = article.find_elements(By.CSS_SELECTOR, 'p.description')
    link_els = article.find_elements(By.CSS_SELECTOR, 'h3.title-news a')
    
    title = title_els[0].text if title_els else ""
    description = description_els[0].text if description_els else ""
    link = link_els[0].get_attribute("href") if link_els else ""
    
    # Bỏ qua link quảng cáo
    if link and "eclick" not in link:
        posts_info.append({
            "title": title,
            "description": description,
            "link": link
        })

# Duyệt qua từng bài viết để lấy chi tiết
for idx, post in enumerate(posts_info):
    print(f"\nĐang xử lý bài {idx + 1}/{len(posts_info)}: {post['title'][:50]}...")
    
    driver.get(post['link'])
    
    # Lấy ngày tạo
    date_elements = driver.find_elements(By.CSS_SELECTOR, "span.date")
    created_at = date_elements[0].text if date_elements else ""
    
    wait = WebDriverWait(driver, 50)
    
    # Lấy tổng số comment
    try:
        total_comment_el = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "label#total_comment")))
        total_comment = total_comment_el.text.strip() if total_comment_el else "0"
    except:
        total_comment = "0"
    
    # Click tất cả nút "Xem thêm ý kiến" để load thêm comment
    while True:
        try:
            show_more_btn = driver.find_element(By.ID, "show_more_coment")
            if show_more_btn.is_displayed():
                driver.execute_script("arguments[0].click();", show_more_btn)
                time.sleep(1)
            else:
                break
        except:
            break
    
    # Click tất cả nút "Đọc tiếp" để hiển thị full content của comment dài
    read_more_btns = driver.find_elements(By.CSS_SELECTOR, "a.icon_show_full_comment.continue-reading")
    for btn in read_more_btns:
        try:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.2)
        except:
            continue
    
    # Lấy nội dung comments
    content_comments = []
    try:
        comments = driver.find_elements(By.CSS_SELECTOR, "div.content-comment")
        
        for cmt in comments:
            try:
                content_more_els = cmt.find_elements(By.CSS_SELECTOR, "p.content_more")
                content = ""
                
                if content_more_els and content_more_els[0].is_displayed():
                    content = driver.execute_script("""
                        var el = arguments[0];
                        var clone = el.cloneNode(true);
                        var txtName = clone.querySelector('span.txt-name');
                        if (txtName) txtName.remove();
                        return clone.textContent.trim();
                    """, content_more_els[0])
                else:
                    full_content_els = cmt.find_elements(By.CSS_SELECTOR, "p.full_content")
                    if full_content_els:
                        content = driver.execute_script("""
                            var el = arguments[0];
                            var clone = el.cloneNode(true);
                            var txtName = clone.querySelector('span.txt-name');
                            if (txtName) txtName.remove();
                            return clone.textContent.trim();
                        """, full_content_els[0])
                
                if content:
                    content_comments.append(content)
            except:
                continue
    except:
        pass
    
    # Thêm thông tin bài viết vào data
    post_detail = {
        "title": post['title'],
        "description": post['description'],
        "created_at": created_at,
        "total_comment": total_comment,
        "content_comment": content_comments
    }
    
    data["post_detail"].append(post_detail)
    
    print(f"  - Created at: {created_at}")
    print(f"  - Total comments: {total_comment}")
    print(f"  - Comments scraped: {len(content_comments)}")

driver.quit()

# Lưu dữ liệu vào file JSON
output_file = "scraped_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print(f"Đã lưu dữ liệu vào file: {output_file}")
print(f"Tổng số bài viết: {len(data['post_detail'])}")
