import os
from pathlib import Path
import re

# Thư mục chứa file txt
text_folder = Path("data")

# Hàm kiểm tra kết thúc câu
def ends_with_punctuation(line):
    return bool(re.search(r"[.!?]$", line.strip()))

# Hàm xóa ký tự không thuộc bảng chữ cái Latin
def remove_non_latin(text):
    # Giữ lại các ký tự Latin cơ bản và một số dấu phổ biến
    return re.sub(r"[^\x00-\x7F]+", "", text)

# Xử lý từng file
for file_path in text_folder.glob("*.txt"):
    try:
        encodings = ["utf-8", "utf-16", "utf-16le", "utf-16be", "cp1252", "latin1", "ascii"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc, errors="strict") as f:
                    # Loại bỏ ký tự không phải Latin ngay sau khi đọc từng dòng
                    lines = [remove_non_latin(line.strip()) for line in f if line.strip()]
                break  # Đọc thành công thì thoát vòng lặp
            except Exception:
                lines = None
        if lines is None:
            raise ValueError("Không đọc được file với các encoding phổ biến.")

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

        print(f"✅ Đã ghép đoạn và loại ký tự không Latin: {file_path.name}")

    except Exception as e:
        print(f"❌ Lỗi với {file_path.name}: {e}")
