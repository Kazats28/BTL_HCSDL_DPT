import os
from pathlib import Path
import re

# Thư mục chứa file txt
text_folder = Path("Text")

# Hàm kiểm tra kết thúc câu
def ends_with_punctuation(line):
    return bool(re.search(r"[.!?]$", line.strip()))

# Xử lý từng file
for file_path in text_folder.glob("*.txt"):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]

        # Ghép các dòng thành đoạn
        paragraphs = []
        paragraph = ""
        for line in lines:
            if paragraph:
                paragraph += " " + line
            else:
                paragraph = line

            if ends_with_punctuation(line):
                paragraphs.append(paragraph.strip())
                paragraph = ""

        # Nếu đoạn cuối chưa kết thúc vẫn lưu
        if paragraph:
            paragraphs.append(paragraph.strip())

        # Ghi lại file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(paragraphs))  # Tách đoạn bằng 2 dòng trắng

        print(f"✅ Đã ghép đoạn và chuẩn hóa: {file_path.name}")

    except Exception as e:
        print(f"❌ Lỗi với {file_path.name}: {e}")
