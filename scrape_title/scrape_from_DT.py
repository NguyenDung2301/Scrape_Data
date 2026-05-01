from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import os

driver = webdriver.Chrome()

# Gán link tìm kiếm
# source_url = "https://dantri.com.vn/cong-nghe/ai-internet.htm" #120
# num_pages = 6  # Số trang muốn cào


# source_url = "https://dantri.com.vn/cong-nghe/gia-dung-thong-minh.htm" #40
# num_pages = 2  # Số trang muốn cào


source_url = "https://dantri.com.vn/cong-nghe/an-ninh-mang.htm" #40
num_pages = 2  # Số trang muốn cào

driver.get(source_url)

# Lấy tên nền tảng nguồn tin
source_name = driver.find_element(By.CSS_SELECTOR, "a[aria-label]").get_attribute("aria-label")

# Khởi tạo danh sách dữ liệu
data = []

# Duyệt qua từng trang
seen_links = set()  # Tránh trùng bài khi cùng bài xuất hiện nhiều trang
for page in range(1, num_pages + 1):
    print(f"{'='*40}\n")
    print(f"Đang cào trang {page}")
    
    page_url = source_url if page == 1 \
        else source_url.replace(".htm", f"/trang-{page}.htm")
    
    driver.get(page_url)
    
    time.sleep(2)
    
    articles = driver.find_elements(By.CSS_SELECTOR, "div.article-content")

    added_this_page = 0  # Số bài đã thêm
    not_found_link = 0  # Số bài không tìm thấy link

    for article in articles:
        # Lấy link — nếu không có link thì bỏ qua hoàn toàn
        link_els = article.find_elements(By.CSS_SELECTOR, 'a[data-prop="sapo"]')
        link = link_els[0].get_attribute("href") if link_els else ""

        if not link:  # Không có link → bỏ qua, không lấy tiêu đề
            not_found_link += 1
            continue
        if "eclick" in link:  # Link quảng cáo → bỏ qua
            continue
        if link in seen_links:  # Đã xử lý → bỏ qua
            continue

        # Lấy tiêu đề
        title_els = article.find_elements(By.CSS_SELECTOR, 'h3.article-title')
        title = title_els[0].text if title_els else ""

        if not title:  # Không có tiêu đề → bỏ qua
            continue

        seen_links.add(link)
        data.append({
            "title": title,
            "source_name": source_name
        })
        added_this_page += 1

    print(f"  Tìm thấy {len(articles)} phần tử, thêm {added_this_page} bài (bỏ qua {not_found_link} bài không tìm thấy link)")

print(f"\nTổng cộng {len(data)} tiêu đề từ {num_pages} trang")

driver.quit()

# Lưu dữ liệu vào file JSON trong folder raw_data
os.makedirs("raw_data", exist_ok=True)
output_file = os.path.join("raw_data", "titles_DT3.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nĐã lưu dữ liệu vào file: {output_file}")
print(f"Tổng số tiêu đề: {len(data)}")
