import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os
import webbrowser
import threading
from search_engine.loader import load_all_data
from search_engine.engine import search_query

# Load dữ liệu một lần
vocab, metadata, tfidf_data, inverted_index, norm2, idf = load_all_data()

class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tìm Kiếm Văn Bản")
        self.root.geometry("900x600")
        self.root.configure(bg="#e9ecef")
        self.file_path = None

        # Font styles
        self.title_font = ("Segoe UI", 20, "bold")
        self.label_font = ("Segoe UI", 12)
        self.button_font = ("Segoe UI", 11, "bold")

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=self.button_font, padding=10, background="#007bff", foreground="white")
        self.style.map("TButton", background=[("active", "#0056b3")])
        self.style.configure("Accent.TButton", background="#28a745")
        self.style.map("Accent.TButton", background=[("active", "#218838")])
        self.style.configure("TLabel", background="#e9ecef", foreground="#333")
        self.style.configure("Treeview", font=self.label_font, rowheight=30)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

        # Main frame
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        # Title
        self.title_label = ttk.Label(
            self.main_frame, text="Tìm Kiếm Văn Bản", font=self.title_font
        )
        self.title_label.pack(pady=(0, 20))

        # File selection frame
        self.file_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.file_frame.pack(fill="x", pady=10, padx=20)

        self.file_label = ttk.Label(
            self.file_frame, text="Chọn file truy vấn:", font=self.label_font
        )
        self.file_label.pack(side="left", padx=15, pady=10)

        self.choose_btn = ttk.Button(
            self.file_frame, text="📁 Chọn File", command=self.choose_file, style="TButton"
        )
        self.choose_btn.pack(side="right", padx=15, pady=10)

        # Search button
        self.search_btn = ttk.Button(
            self.main_frame, text="🔍 Tìm Kiếm", command=self.search_thread, style="Accent.TButton"
        )
        self.search_btn.pack(pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame, mode="indeterminate", length=400
        )
        self.progress.pack(pady=(0, 20))
        self.progress.pack_forget()

        # Result frame
        self.result_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.result_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.result_label = ttk.Label(
            self.result_frame, text="", font=self.label_font, foreground="#dc3545"
        )
        self.result_label.pack(anchor="w", pady=(10, 5))

        # Result table
        self.result_tree = ttk.Treeview(
            self.result_frame, columns=("STT", "File", "Score"), show="headings", selectmode="browse"
        )
        self.result_tree.heading("STT", text="STT")
        self.result_tree.heading("File", text="Tên File")
        self.result_tree.heading("Score", text="Độ Tương Đồng")
        self.result_tree.column("STT", width=50, anchor="center")
        self.result_tree.column("File", width=400)
        self.result_tree.column("Score", width=150, anchor="center")
        self.result_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.result_tree.bind("<Double-1>", self.open_file)

        # Custom frame style for card effect
        self.style.configure("Card.TFrame", background="white", relief="flat")
        self.main_frame.bind("<Configure>", lambda e: self.apply_shadow())

    def apply_shadow(self):
        # Simulate card shadow effect
        self.file_frame.configure(style="Card.TFrame")
        self.result_frame.configure(style="Card.TFrame")

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.file_path:
            self.file_label.config(text=f"Đã chọn: {os.path.basename(self.file_path)}")
        else:
            self.file_label.config(text="Chọn file truy vấn:")

    def search_thread(self):
        if not self.file_path:
            messagebox.showerror("Lỗi", "Vui lòng chọn file trước khi tìm kiếm!")
            return

        self.choose_btn.config(state="disabled")
        self.search_btn.config(state="disabled")
        self.progress.pack(pady=(0, 20))
        self.progress.start()

        # Clear previous results
        self.result_label.config(text="Đang tìm kiếm...")
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        # Start search in a separate thread
        threading.Thread(target=self.search_background, daemon=True).start()

    def search_background(self):
        start = time.time()
        try:
            top_results = search_query(self.file_path, vocab, tfidf_data, inverted_index, norm2, idf)
            duration = time.time() - start
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            messagebox.showerror("Lỗi", f"{type(e).__name__}: {e}\n\n{traceback_str}")
            print(traceback_str)
            self.root.after(0, self.reset_ui)
            return

        # Update GUI on main thread
        self.root.after(0, lambda: self.show_results(top_results, duration))

    def show_results(self, top_results, duration):
        self.progress.stop()
        self.progress.pack_forget()

        if not top_results:
            self.result_label.config(text="Không tìm thấy kết quả.")
        else:
            self.result_label.config(text=f"Thời gian tìm kiếm: {duration:.2f} giây")

        for i, (doc_id, score) in enumerate(top_results[:3], 1):
            file_path = os.path.abspath(metadata[doc_id]["filepath"])
            file_name = os.path.basename(file_path)
            self.result_tree.insert(
                "", "end", values=(i, file_name, f"{score:.4f}"), tags=(file_path,)
            )

        self.reset_ui()

    def reset_ui(self):
        self.choose_btn.config(state="normal")
        self.search_btn.config(state="normal")

    def open_file(self, event):
        item = self.result_tree.selection()
        if item:
            file_path = self.result_tree.item(item, "tags")[0]
            if file_path and os.path.exists(file_path):
                webbrowser.open(f"file://{file_path}")
            else:
                messagebox.showerror("Lỗi", "Không thể mở file. File không tồn tại.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()