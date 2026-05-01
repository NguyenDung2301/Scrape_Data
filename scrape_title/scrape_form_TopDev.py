from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time
import json
import os

driver = webdriver.Chrome()

#source_url = "https://topdev.vn/blog/category/cong-nghe/"  # 100

source_url = "https://topdev.vn/blog/category/lap-trinh/"  # 100

driver.get(source_url)
time.sleep(3)  # Chờ trang load xong

source_name = "TopDev-Việc làm IT hàng đầu Việt Nam"

# Mục tiêu ~100 bài; dừng khi đạt ngưỡng đủ gần (không cần đúng 100)
ENOUGH = 100
max_scroll_rounds = 150

data = []
seen_links = set()


def collect_articles():
    articles = driver.find_elements(By.CSS_SELECTOR, "div.td-animation-stack")
    for article in articles:
        if len(data) >= ENOUGH:
            break
        try:
            link_els = article.find_elements(By.CSS_SELECTOR, "h3.td-module-title a")
            link = link_els[0].get_attribute("href") if link_els else ""

            if not link:
                continue
            if "eclick" in link:
                continue
            if link in seen_links:
                continue

            title_els = article.find_elements(By.CSS_SELECTOR, "h3.td-module-title")
            title = title_els[0].text if title_els else ""

            if not title:
                continue

            seen_links.add(link)
            data.append({"title": title, "source_name": source_name})
        except StaleElementReferenceException:
            continue


prev_len = None
stuck = 0
for i in range(max_scroll_rounds):
    collect_articles()
    n = len(data)
    if n >= ENOUGH:
        print(f"Đã cào khoảng đủ mục tiêu (~100 bài, hiện {n}) sau {i + 1} lần cuộn.")
        break
    if prev_len is not None and n == prev_len:
        stuck += 1
        if stuck >= 3:
            print(f"Hết bài mới sau {i + 1} lần cuộn (hiện có {n} bài).")
            break
    else:
        stuck = 0
    prev_len = n
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
else:
    if len(data) < ENOUGH:
        print(f"Đã hết {max_scroll_rounds} lần cuộn, thu được {len(data)} bài (chưa tới ~100).")

print(f"Đã thu thập {len(data)} tiêu đề.")

driver.quit()

os.makedirs("raw_data", exist_ok=True)
output_file = os.path.join("raw_data", "titles_TopDev2.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nĐã lưu dữ liệu vào file: {output_file}")
print(f"Tổng số tiêu đề: {len(data)}")
