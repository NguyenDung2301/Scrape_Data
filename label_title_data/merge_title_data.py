import json
import os
import glob
import random

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "C:\\Users\\Admin\\MyProject\\ScrapeData\\label_title_data")
TITLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "C:\\Users\\Admin\\MyProject\\ScrapeData\\label_title_data")
OUTPUT_FILE = os.path.join(TITLE_DATA_DIR, "label_merged_titles.json")

def merge_json_files():
    """Đọc tất cả file JSON trong folder raw_data và trộn thành 1 file duy nhất."""
    
    # Tạo folder title_data nếu chưa tồn tại
    os.makedirs(TITLE_DATA_DIR, exist_ok=True)
    
    all_data = []
    json_files = sorted(glob.glob(os.path.join(RAW_DATA_DIR, "*.json")))
    
    if not json_files:
        print("Không tìm thấy file JSON nào trong folder raw_data!")
        return
    
    print(f"Tìm thấy {len(json_files)} file JSON trong raw_data:")
    
    for file_path in json_files:
        file_name = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, list):
                all_data.extend(data)
                print(f"  ✔ {file_name}: {len(data)} bản ghi")
            else:
                print(f"  ⚠ {file_name}: Không phải dạng mảng, bỏ qua")
        except json.JSONDecodeError as e:
            print(f"  ✘ {file_name}: Lỗi đọc JSON - {e}")
        except Exception as e:
            print(f"  ✘ {file_name}: Lỗi - {e}")
    
    # Xáo trộn ngẫu nhiên
    random.shuffle(all_data)
    
    # Lưu file merged
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"Tổng số bản ghi: {len(all_data)}")
    print(f"File đã lưu tại: {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_json_files()
