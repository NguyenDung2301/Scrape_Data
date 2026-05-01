# 🤖 Vietnamese IT Title Classifier

Pipeline thu thập và phân loại tiêu đề bài báo công nghệ tiếng Việt, sử dụng **PhoBERT** fine-tuned để phân biệt nội dung thuần IT/CNTT với nội dung công nghệ tổng quát.

---

## 📋 Tổng quan

Dự án xây dựng một pipeline đầu-cuối gồm 3 giai đoạn:

1. **Thu thập dữ liệu** — Cào tiêu đề bài báo từ 4 nguồn báo công nghệ tiếng Việt bằng Selenium.
2. **Gán nhãn & Tiền xử lý** — Gộp, xáo trộn, chia nhỏ dữ liệu; gán nhãn thủ công (hoặc bán tự động).
3. **Huấn luyện & Suy diễn** — Fine-tune PhoBERT với Underthesea để phân loại nhị phân (IT / Non-IT).

### Nhãn phân loại

| Label | Ý nghĩa | Ví dụ |
|-------|---------|-------|
| `1` — **IT** | Nội dung trực tiếp liên quan đến CNTT, AI, Lập trình | *"Google ra mắt mô hình AI Gemini 2.0 với khả năng lập trình tự động"* |
| `0` — **Non-IT** | Công nghệ tổng quát, sản phẩm tiêu dùng, không liên quan CNTT | *"Samsung ra mắt tủ lạnh thông minh mới tại Việt Nam"* |

---

## 📁 Cấu trúc thư mục

```
ScrapeData/
│
├── scrape_title/                   # Scripts cào dữ liệu
│   ├── scrape_form_TopDev.py       # Cào từ TopDev (danh mục lập trình)
│   ├── scrape_from_DT.py           # Cào từ Dân Trí (danh mục công nghệ)
│   ├── scrape_from_GenK.py         # Cào từ GenK (danh mục AI, ICT, Internet...)
│   └── scrape_from_VN-EP.py        # Cào từ VnExpress (danh mục khoa học-công nghệ)
│
├── raw_data/                       # Dữ liệu thô đã cào (JSON)
│   ├── titles_DT1.json             # Dân Trí batch 1 (AI/Internet)
│   ├── titles_DT2.json             # Dân Trí batch 2 (Gia dụng thông minh)
│   ├── titles_DT3.json             # Dân Trí batch 3 (An ninh mạng)
│   ├── titles_GenK1.json           # GenK batch 1 (AI)
│   ├── titles_GenK2.json           # GenK batch 2 (Internet)
│   ├── titles_GenK3.json           # GenK batch 3 (Đồ chơi số)
│   ├── titles_GenK4.json           # GenK batch 4 (Tin ICT)
│   ├── titles_TopDev1.json         # TopDev batch 1 (Công nghệ)
│   ├── titles_TopDev2.json         # TopDev batch 2 (Lập trình)
│   ├── titles_VN-EP1.json          # VnExpress batch 1 (AI)
│   ├── titles_VN-EP2.json          # VnExpress batch 2 (Chuyển đổi số)
│   └── titles_VN-EP3.json          # VnExpress batch 3 (Thiết bị)
│
├── label_title_data/               # Dữ liệu đã gán nhãn
│   ├── merge_title_data.py         # Script gộp tất cả file JSON đã label
│   ├── label_merged_titles.json    # File gộp (~1020 mẫu, đã shuffle)
│   ├── label_title.part1.json      # Phần 1/4 (~255 mẫu)
│   ├── label_title.part2.json      # Phần 2/4 (~255 mẫu)
│   ├── label_title.part3.json      # Phần 3/4 (~255 mẫu)
│   └── label_title.part4.json      # Phần 4/4 (~255 mẫu)
│
├── unlabel_title_data/             # Dữ liệu chưa gán nhãn
│   ├── merge_title_data.py         # Script gộp file JSON unlabeled
│   ├── split_title.py              # Script chia thành 4 phần để gán nhãn
│   ├── unlabel_merged_titles.json  # File gộp unlabeled (~1020 mẫu)
│   ├── unlabel_title.part1.json    # Phần 1/4
│   ├── unlabel_title.part2.json    # Phần 2/4
│   ├── unlabel_title.part3.json    # Phần 3/4
│   └── unlabel_title.part4.json    # Phần 4/4
│
├── phobert_title_classifier_best/  # Model PhoBERT đã fine-tune (best checkpoint)
│   ├── config.json
│   ├── model.safetensors           # Trọng số model (~515 MB)
│   ├── tokenizer_config.json
│   ├── vocab.txt
│   ├── bpe.codes
│   ├── added_tokens.json
│   └── training_args.bin
│
├── train_title_classifier.ipynb    # Notebook Kaggle: toàn bộ pipeline train
├── test.py                         # Script inference/test model trên máy local
├── requirement.txt                 # Các thư viện cần cài
└── .gitignore
```

---

## 📊 Thông tin Dataset

| Thuộc tính | Giá trị |
|-----------|---------|
| Tổng số mẫu | **~1,020 mẫu** (labeled) + **~1,020 mẫu** (unlabeled) |
| Tỉ lệ nhãn | Non-IT: **43.8%** (447) / IT: **56.2%** (573) |
| Nguồn dữ liệu | GenK, Dân Trí, VnExpress, TopDev |
| Định dạng | JSON — mỗi bản ghi gồm `title` và `source_name` |
| Train/Val/Test split | **80% / 10% / 10%** |

### Cấu trúc một bản ghi JSON

```json
{
  "title": "Google ra mắt mô hình AI Gemini 2.0 với khả năng lập trình tự động",
  "source_name": "GenK-Trang thông tin điện tử từ tổng hợp",
  "label": 1
}
```

---

## 🛠️ Cài đặt

### Yêu cầu hệ thống

- Python 3.8+
- Google Chrome + ChromeDriver (để chạy Selenium scraper)
- GPU (để fine-tune model — khuyến nghị dùng Kaggle/Colab)

### Cài đặt thư viện

```bash
pip install -r requirement.txt
```

**`requirement.txt`:**
```
selenium
underthesea
torch
transformers
requests
beautifulsoup4
```

> **Lưu ý**: Nếu fine-tune model cần thêm:
> ```bash
> pip install datasets scikit-learn accelerate
> ```

---

## 🚀 Hướng dẫn sử dụng

### Bước 1: Thu thập dữ liệu (Scraping)

Chạy các script trong thư mục `scrape_title/`. Mỗi script cào ~50–120 tiêu đề từ một nguồn báo, lưu kết quả vào `raw_data/`.

```bash
# Cào từ Dân Trí
python scrape_title/scrape_from_DT.py

# Cào từ GenK
python scrape_title/scrape_from_GenK.py

# Cào từ VnExpress
python scrape_title/scrape_from_VN-EP.py

# Cào từ TopDev
python scrape_title/scrape_form_TopDev.py
```

> **Lưu ý**: Trước khi chạy, mở script và chỉnh `source_url` và `output_file` theo batch muốn cào.

#### Cơ chế scraping

| Nguồn | Cơ chế | CSS Selector |
|-------|--------|-------------|
| **Dân Trí** | Phân trang (`trang-N.htm`) | `div.article-content > h3.article-title` |
| **VnExpress** | Phân trang (`-pN`) | `article.item-news > h2.title-news a` |
| **GenK** | Scroll + nút "Xem thêm" | `div.elp-list > h4.knswli-title a` |
| **TopDev** | Infinite scroll | `div.td-animation-stack > h3.td-module-title a` |

---

### Bước 2: Gộp dữ liệu

**Dữ liệu unlabeled** (chuẩn bị để gán nhãn):
```bash
python unlabel_title_data/merge_title_data.py
python unlabel_title_data/split_title.py   # Chia thành 4 phần để gán nhãn thủ công
```

**Dữ liệu labeled** (sau khi đã gán nhãn xong):
```bash
python label_title_data/merge_title_data.py
```

---

### Bước 3: Huấn luyện Model (Kaggle/Colab)

Mở notebook `train_title_classifier.ipynb` trên **Kaggle** hoặc **Google Colab** (cần GPU).

Notebook gồm 16 cells thực hiện toàn bộ pipeline:

| Cell | Nội dung |
|------|---------|
| 1 | Cài đặt packages |
| 2 | Import thư viện + kiểm tra GPU |
| 3 | Load & khám phá dataset |
| 4 | Loại bỏ bản ghi trùng lặp |
| 5 | Preprocessing với Underthesea (NER + Word Tokenize) |
| 6 | Test preprocessing & áp dụng toàn bộ |
| 7 | Train/Val/Test split (80/10/10) |
| 8 | Tokenization với PhoBERT AutoTokenizer |
| 9 | Load PhoBERT base model |
| 10 | Cấu hình training (TrainingArguments + Trainer) |
| 11 | Train model |
| 12 | Đánh giá (Accuracy, F1, Confusion Matrix) |
| 13 | Phân tích lỗi (Error Analysis) |
| 14 | Hàm inference `predict()` |
| 15 | Lưu model best checkpoint |
| 16 | Vẽ biểu đồ training history |

#### Cấu hình huấn luyện

```python
TrainingArguments(
    num_train_epochs=5,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    load_best_model_at_end=True,
    fp16=True,  # GPU mixed precision
)
```

---

### Bước 4: Inference / Suy diễn

Sau khi train xong và tải model về máy, chạy `test.py`:

```bash
python test.py
```

**Ví dụ kết quả:**

```
============================================================
🔮 DỰ ĐOÁN TIÊU ĐỀ
============================================================
Tiêu đề:    Google ra mắt mô hình AI Gemini 2.0 với khả năng lập trình tự động
Kết quả:    IT (confidence: 98.53%)
  P(Non-IT): 1.47% | P(IT): 98.53%

Tiêu đề:    Samsung ra mắt tủ lạnh thông minh mới tại Việt Nam
Kết quả:    Non-IT (confidence: 94.21%)
  P(Non-IT): 94.21% | P(IT): 5.79%
```

Tích hợp vào code Python:

```python
from test import predict_title

result = predict_title("Hướng dẫn deploy ứng dụng React lên AWS Lambda")
# {'label': 1, 'label_name': 'IT', 'confidence': 0.9712}
```

---

## 🧠 Kiến trúc Model

```
Tiêu đề thô
    │
    ▼
[Underthesea NER]
 Thay thế PER/ORG → "name" | LOC → "loc"
    │
    ▼
[Regex Normalization]
 Số, ngày tháng, phần trăm → token đặc biệt
    │
    ▼
[Underthesea Word Tokenize]
 "khởi_nghiệp", "lập_trình", ...
    │
    ▼
[PhoBERT Tokenizer]
 BPE + SentencePiece (max_length=256)
    │
    ▼
[PhoBERT Base Encoder]
 vinai/phobert-base (12 layers, 768 hidden)
    │
    ▼
[Linear Classifier Head]
 768 → 2 (IT / Non-IT)
    │
    ▼
Xác suất + Nhãn dự đoán
```

### Vì sao chọn Underthesea thay VnCoreNLP?

| Tiêu chí | VnCoreNLP | Underthesea |
|----------|-----------|-------------|
| Cài đặt | Cần Java, download JAR ~200MB | `pip install underthesea` |
| Phụ thuộc | Java Runtime | Pure Python |
| Word Segmentation | `rdrsegmenter.tokenize()` | `word_tokenize(text, format="text")` |
| NER output | `[(word, tag)]` | `[(word, pos, chunk, ner_tag)]` |
| Ưu điểm | Accuracy cao | Nhẹ, dễ cài, không cần Java |

---

## 📈 Kết quả đánh giá

Model được đánh giá trên **test set** với các metrics:

- **Accuracy** — Tỉ lệ phân loại đúng
- **F1-score (macro)** — Cân bằng giữa 2 class
- **Precision & Recall** — Cho từng class
- **Confusion Matrix** — Phân tích phân bố lỗi

---

## 🔧 Tùy chỉnh

### Thêm nguồn cào mới

Tạo script mới trong `scrape_title/`, theo mẫu:
```python
data.append({
    "title": title,      # Tiêu đề bài báo
    "source_name": name  # Tên nguồn báo
})
```
Lưu vào `raw_data/titles_<Nguồn><Batch>.json`.

### Thêm danh mục cào

Trong mỗi script scraper có comment các `source_url` khác nhau. Bỏ comment dòng URL mong muốn và chạy lại script.

### Thay đổi tham số training

Chỉnh các giá trị trong `TrainingArguments` tại notebook `train_title_classifier.ipynb`:
- `num_train_epochs` — Số epoch (mặc định: 5)
- `per_device_train_batch_size` — Batch size (mặc định: 16)
- `learning_rate` — Learning rate (mặc định: 2e-5)
- `max_length` — Độ dài tối đa token (mặc định: 256)

---

## 📦 Nguồn dữ liệu

| Nguồn | URL | Loại nội dung |
|-------|-----|--------------|
| **GenK** | genk.vn | AI, Internet, ICT, Đồ chơi số |
| **Dân Trí** | dantri.com.vn/cong-nghe | AI, An ninh mạng, Gia dụng thông minh |
| **VnExpress** | vnexpress.net/khoa-hoc-cong-nghe | AI, Chuyển đổi số, Thiết bị |
| **TopDev** | topdev.vn/blog | Công nghệ, Lập trình |

---

## 🤝 Đóng góp

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add: mô tả thay đổi"`
4. Push to branch: `git push origin feature/your-feature`
5. Tạo Pull Request

---

## 📄 License

Dự án sử dụng cho mục đích học thuật và nghiên cứu.

---

*Powered by [PhoBERT](https://github.com/VinAIResearch/PhoBERT) · [Underthesea](https://github.com/undertheseanlp/underthesea) · [HuggingFace Transformers](https://huggingface.co/docs/transformers)*
