import os
import shutil

# Đường dẫn đến folder gốc chứa các file txt
source_folder = "data"
# Đường dẫn đến folder đích để lưu các file đạt yêu cầu
destination_folder = "data_text"

# Tạo folder đích nếu chưa tồn tại
os.makedirs(destination_folder, exist_ok=True)

# Duyệt qua từng file trong folder gốc
for filename in os.listdir(source_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(source_folder, filename)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            word_count = len(content.split())

        if word_count in range(6000, 200000):
            shutil.copy(file_path, os.path.join(destination_folder, filename))
            print(f"Đã sao chép: {filename} ({word_count} từ)")
