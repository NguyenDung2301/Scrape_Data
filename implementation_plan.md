# Huấn luyện Model Phân loại Tiêu đề Công nghệ với PhoBERT + Underthesea

## Bối cảnh

Dựa trên cấu trúc huấn luyện của repo `Vietnamese-stock-article-classification`, xây dựng một pipeline phân loại tiêu đề bài báo công nghệ sử dụng **PhoBERT** (`vinai/phobert-base`) thay thế VnCoreNLP bằng **Underthesea**.

### Dataset hiện có

- **File**: [label_merged_titles.json](file:///c:/Users/Admin/MyProject/ScrapeData/label_title_data/label_merged_titles.json)
- **Tổng**: 1020 mẫu
- **Labels**: 2 classes (binary classification)
  - `0` — Tin công nghệ chung / Sản phẩm / Không liên quan trực tiếp đến ngành IT: **447 mẫu (43.8%)**
  - `1` — Tin liên quan trực tiếp đến ngành CNTT / AI / Lập trình: **573 mẫu (56.2%)**
- **Sources**: GenK, Dân trí, VnExpress, TopDev, v.v.

### So sánh VnCoreNLP vs Underthesea

| Tiêu chí | VnCoreNLP (repo gốc) | Underthesea (mới) |
|----------|----------------------|-------------------|
| Cài đặt | Cần Java, download JAR ~200MB | `pip install underthesea` |
| Word Segmentation | `rdrsegmenter.tokenize(text)` | `word_tokenize(text, format="text")` |
| NER | `rdrsegmenter.ner(text)` | `ner(text)` |
| Output NER | `[(word, tag), ...]` | `[(word, pos, chunk, ner_tag), ...]` |
| Ưu điểm | Accuracy cao, có Java backend | Pure Python, dễ cài, không cần Java |

---

## User Review Required

> [!IMPORTANT]
> **Lựa chọn approach**: Repo gốc dùng cách cũ (fairseq + fastBPE + manual training loop). Hiện tại HuggingFace hỗ trợ **`vinai/phobert-base`** trực tiếp qua `AutoTokenizer` — code sạch hơn, hiện đại hơn, không cần download model thủ công. **Tôi đề xuất dùng approach hiện đại** (HuggingFace Transformers API). Bạn có đồng ý không?

> [!IMPORTANT]
> **Ý nghĩa của label**: Từ dữ liệu tôi quan sát, label `0` = tin công nghệ chung/sản phẩm, label `1` = tin liên quan ngành IT/AI/lập trình. Bạn xác nhận ý nghĩa label 0 và 1 là gì?

> [!WARNING]
> **Môi trường chạy**: Fine-tune PhoBERT cần **GPU**. Bạn muốn chạy trên:
> - **Google Colab** (miễn phí GPU T4) — giống repo gốc
> - **Máy local** (cần NVIDIA GPU + CUDA)
> - **Kaggle** (miễn phí GPU P100)

---

## Proposed Changes

Tạo notebook/script huấn luyện trong thư mục `ScrapeData/` với các bước sau:

### Component 1: Cài đặt & Chuẩn bị

#### [NEW] [train_title_classifier.py](file:///c:/Users/Admin/MyProject/ScrapeData/train_title_classifier.py)

Script Python chính (hoặc chuyển thành `.ipynb` nếu dùng Colab) chứa toàn bộ pipeline.

**Bước 1 — Cài đặt packages**:
```
pip install transformers torch underthesea scikit-learn datasets accelerate
```

---

### Component 2: Tiền xử lý dữ liệu (Preprocessing)

Thay hàm `del_test()` của repo gốc (dùng VnCoreNLP) bằng Underthesea:

```python
from underthesea import word_tokenize, ner
import re

def preprocess_title(text):
    """Tiền xử lý title: NER → thay thế thực thể → tách từ"""
    # 1. NER bằng Underthesea
    entities = ner(text)
    for word, pos, chunk, ner_tag in entities:
        if ner_tag in ('B-PER', 'I-PER', 'B-ORG', 'I-ORG'):
            text = text.replace(word, 'name')
        elif ner_tag in ('B-LOC', 'I-LOC'):
            text = text.replace(word, 'loc')
    
    # 2. Thay thế số, ngày tháng, phần trăm
    text = re.sub(r'\d+[%]', 'percent', text)
    text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', 'date', text)
    text = re.sub(r'\d+', 'number', text)
    
    # 3. Loại bỏ dấu câu
    text = re.sub(r'[.,;:!?\"\'()\[\]{}\-–—…""'']', ' ', text)
    
    # 4. Word segmentation bằng Underthesea
    text = word_tokenize(text, format="text")  # "khởi_nghiệp" format
    
    # 5. Lowercase
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text
```

---

### Component 3: Tokenization + Dataset

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

# Tokenize đã word-segmented text
def tokenize_function(examples):
    return tokenizer(
        examples["text"], 
        padding="max_length", 
        truncation=True, 
        max_length=256
    )
```

**Chia dữ liệu**: 80% train / 10% validation / 10% test (giống repo gốc)

---

### Component 4: Huấn luyện Model

```python
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer

model = AutoModelForSequenceClassification.from_pretrained(
    "vinai/phobert-base", 
    num_labels=2  # binary classification
)

training_args = TrainingArguments(
    output_dir="./phobert_title_classifier",
    num_train_epochs=5,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    fp16=True,  # GPU acceleration
)
```

---

### Component 5: Đánh giá & Inference

- **Metrics**: Accuracy, F1-score (macro), Precision, Recall
- **Confusion matrix** để xem phân bố lỗi
- **Hàm `predict()`** để dự đoán tiêu đề mới

---

## Tổng quan các file cần tạo

| File | Mô tả |
|------|--------|
| `train_title_classifier.py` (hoặc `.ipynb`) | Script/notebook chính: preprocessing → train → evaluate |
| `phobert_title_classifier/` | Thư mục output chứa model đã train + checkpoints |

---

## Open Questions

> [!IMPORTANT]
> 1. **Approach**: Dùng HuggingFace Trainer API (hiện đại, code sạch) hay viết manual training loop giống repo gốc (PyTorch thuần)?
> 2. **Label meaning**: Xác nhận ý nghĩa label 0 và label 1?
> 3. **Môi trường**: Chạy trên Colab, Kaggle hay máy local?
> 4. **Output format**: Script `.py` hay Jupyter notebook `.ipynb`?

---

## Verification Plan

### Automated Tests
- Kiểm tra preprocessing trên 5-10 sample titles
- Train 1 epoch nhanh để verify pipeline hoạt động
- So sánh accuracy/F1 trên test set

### Manual Verification
- Thử `predict()` trên một số tiêu đề mới chưa có trong dataset
- Kiểm tra confusion matrix để phát hiện pattern lỗi
