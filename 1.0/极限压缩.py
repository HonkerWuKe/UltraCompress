import py7zr
import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from datetime import datetime

class CompressionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("极限压缩工具")
        self.root.geometry("600x500")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 配置根窗口的网格权重，使内容居中
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # 配置主框架的网格权重
        for i in range(6):  # 6行
            main_frame.grid_rowconfigure(i, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)  # 中间列可伸缩
        
        # 输入框架
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=0, column=0, columnspan=3, pady=5, sticky=(tk.E, tk.W))
        input_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="输入路径:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.input_path = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path)
        input_entry.grid(row=0, column=1, padx=5, sticky=(tk.E, tk.W))
        ttk.Button(input_frame, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        # 输出框架
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky=(tk.E, tk.W))
        output_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="输出路径:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path)
        output_entry.grid(row=0, column=1, padx=5, sticky=(tk.E, tk.W))
        ttk.Button(output_frame, text="浏览", command=self.browse_output).grid(row=0, column=2, padx=5)
        
        # 压缩选项框架
        options_frame = ttk.LabelFrame(main_frame, text="压缩选项", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.E, tk.W))
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(4, weight=1)
        
        # 字典大小选择
        ttk.Label(options_frame, text="字典大小:").grid(row=0, column=0, padx=5)
        self.dict_size = tk.StringVar(value="1024")
        dict_entry = ttk.Entry(options_frame, textvariable=self.dict_size, width=10)
        dict_entry.grid(row=0, column=1, padx=5)
        ttk.Label(options_frame, text="MB").grid(row=0, column=2, padx=5)
        
        # 线程数选择
        ttk.Label(options_frame, text="线程数:").grid(row=0, column=3, padx=5)
        self.thread_count = tk.StringVar(value=str(os.cpu_count()))
        thread_entry = ttk.Entry(options_frame, textvariable=self.thread_count, width=10)
        thread_entry.grid(row=0, column=4, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate', 
                                      variable=self.progress_var)
        self.progress.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.E, tk.W))
        
        # 状态文本框
        self.status_text = tk.Text(main_frame, height=10)
        self.status_text.grid(row=4, column=0, columnspan=3, pady=5, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="开始压缩", command=self.start_compression).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT, padx=5)

        # 添加参数说明
        help_text = """
参数说明：
1. 字典大小：
   - 推荐值：256-4096 MB
   - 越大压缩率越高，但需要更多内存
   - 建议不超过物理内存的1/3

2. 线程数：
   - 推荐值：等于CPU核心数
   - 可以适当增加但不建议超过核心数的2倍
"""
        self.status_text.insert(tk.END, help_text)

    def browse_input(self):
        path = filedialog.askopenfilename(title="选择要压缩的文件") or \
               filedialog.askdirectory(title="选择要压缩的文件夹")
        if path:
            self.input_path.set(path)
            # 自动设置输出路径
            self.output_path.set(str(Path(path).with_suffix('.7z')))

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".7z",
            filetypes=[("7Z files", "*.7z"), ("All files", "*.*")]
        )
        if path:
            self.output_path.set(path)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        
    def start_compression(self):
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入路径")
            return
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出路径")
            return
            
        # 在新线程中运行压缩
        threading.Thread(target=self.compress_task, daemon=True).start()
        
    def compress_task(self):
        try:
            input_path = Path(self.input_path.get()).resolve()  # 获取绝对路径
            output_path = Path(self.output_path.get()).resolve()
            
            # 验证输入路径
            if not input_path.exists():
                raise FileNotFoundError("输入文件或文件夹不存在")
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 获取用户输入的值并进行验证
            try:
                dict_size = int(self.dict_size.get())
                if dict_size <= 0:
                    raise ValueError("字典大小必须大于0")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的字典大小")
                return
                
            try:
                thread_count = int(self.thread_count.get())
                if thread_count <= 0:
                    raise ValueError("线程数必须大于0")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的线程数")
                return
            
            self.log_message(f"开始压缩: {input_path}")
            start_time = time.time()
            
            # 修改压缩处理逻辑
            with py7zr.SevenZipFile(str(output_path), 'w') as archive:
                if input_path.is_file():
                    # 如果是单个文件，直接添加
                    archive.write(input_path, input_path.name)
                else:
                    # 如果是目录，遍历添加所有文件
                    for file_path in input_path.rglob('*'):
                        if file_path.is_file():
                            # 计算相对路径
                            rel_path = file_path.relative_to(input_path)
                            archive.write(file_path, rel_path)
                            self.log_message(f"正在压缩: {rel_path}")
            
            end_time = time.time()
            
            # 计算压缩比
            original_size = self.get_size(input_path)
            compressed_size = output_path.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            self.log_message(f"压缩完成!")
            self.log_message(f"原始大小: {self.format_size(original_size)}")
            self.log_message(f"压缩后大小: {self.format_size(compressed_size)}")
            self.log_message(f"压缩比: {ratio:.2f}%")
            self.log_message(f"耗时: {end_time - start_time:.2f}秒")
            
            messagebox.showinfo("完成", "压缩已完成！")
            
        except Exception as e:
            self.log_message(f"错误: {str(e)}")
            messagebox.showerror("错误", str(e))

    def get_size(self, path):
        if os.path.isfile(path):
            return os.path.getsize(path)
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionGUI(root)
    root.mainloop()
