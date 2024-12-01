import py7zr
import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from datetime import datetime, timedelta
import psutil
import json
from typing import List, Dict
import sqlite3
import tempfile
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CompressionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("极限压缩工具")
        self.root.geometry("800x600")
        
        # 初始化所有需要的变量，使用推荐值
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.compression_level = tk.StringVar(value="NORMAL")  # 推荐的平衡模式
        self.thread_count = tk.StringVar(value=str(max(1, os.cpu_count() - 1)))  # 推荐值：CPU核心数-1
        self.progress_var = tk.DoubleVar()
        self.dict_size = tk.StringVar(value="32")  # 推荐值：32MB
        self.password = tk.StringVar()  # 加密密码
        
        # 高级设置的推荐值
        self.solid_mode = tk.BooleanVar(value=True)  # 推荐开启固实压缩
        self.split_size = tk.StringVar(value="0")  # 默认不分卷
        self.encrypt_filenames = tk.BooleanVar(value=False)  # 默认不加密文件名
        self.verify_after_compress = tk.BooleanVar(value=True)  # 推荐开启压缩后验证
        
        # 性能监控相关
        self.cpu_usage = tk.StringVar(value="CPU: 0%")
        self.memory_usage = tk.StringVar(value="内存: 0%")
        self.estimated_time = tk.StringVar(value="预计剩余时间: --:--:--")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)
        
        # 添加伪装相关变量
        self.disguise_enabled = tk.BooleanVar(value=False)
        self.disguise_type = tk.StringVar(value="MP4视频")  # 默认选择MP4
        self.disguise_file = tk.StringVar()  # 用于合并的伪装文件路径
        
        # 添加提取功能相关变量
        self.extract_input = tk.StringVar()  # 要提取的伪装文件路径
        self.extract_output = tk.StringVar()  # 提取后的输出路径
        
        # 设置界面
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架，使用网格布局
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # 配置根窗口和主框架的网格权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # 创建左右分栏
        left_frame = ttk.Frame(main_frame)
        right_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W), padx=(0, 5))
        right_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # 左侧：基本设置
        basic_frame = ttk.LabelFrame(left_frame, text="基本设置", padding="5")
        basic_frame.pack(fill=tk.X, expand=True, pady=(0, 5))
        
        # 文件选择区域
        ttk.Label(basic_frame, text="输入路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(basic_frame, textvariable=self.input_path).grid(row=0, column=1, sticky=(tk.E, tk.W), padx=5)
        ttk.Button(basic_frame, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        ttk.Label(basic_frame, text="输出路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(basic_frame, textvariable=self.output_path).grid(row=1, column=1, sticky=(tk.E, tk.W), padx=5)
        ttk.Button(basic_frame, text="浏览", command=self.browse_output).grid(row=1, column=2, padx=5)
        
        # 压缩选项
        ttk.Label(basic_frame, text="压缩级别:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        levels = ["STORE", "FASTEST", "FAST", "NORMAL", "MAXIMUM", "ULTRA"]
        ttk.Combobox(basic_frame, textvariable=self.compression_level, values=levels, state="readonly").grid(
            row=2, column=1, columnspan=2, sticky=(tk.E, tk.W), padx=5)
        
        ttk.Label(basic_frame, text="线程数:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(basic_frame, textvariable=self.thread_count).grid(row=3, column=1, columnspan=2, sticky=(tk.E, tk.W), padx=5)
        
        # 密码设置
        ttk.Label(basic_frame, text="加密密码:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        password_entry = ttk.Entry(basic_frame, textvariable=self.password, show="*")
        password_entry.grid(row=4, column=1, columnspan=2, sticky=(tk.E, tk.W), padx=5)
        
        # 左侧：高级功能
        advanced_frame = ttk.LabelFrame(left_frame, text="高级功能", padding="5")
        advanced_frame.pack(fill=tk.BOTH, expand=True)
        
        advanced_notebook = ttk.Notebook(advanced_frame)
        advanced_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 伪装设置页面
        disguise_frame = ttk.Frame(advanced_notebook)
        advanced_notebook.add(disguise_frame, text="文件伪装")
        
        option_frame = ttk.LabelFrame(disguise_frame, text="伪装选项")
        option_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(option_frame, text="伪装类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        disguise_types = ["MP4视频", "JPG图片", "PDF文档", "合并到其他文件"]
        type_combo = ttk.Combobox(option_frame, values=disguise_types, textvariable=self.disguise_type, state="readonly", width=25)
        type_combo.grid(row=0, column=1, sticky=(tk.E, tk.W), padx=5)
        
        ttk.Label(option_frame, text="伪装文件:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(option_frame, textvariable=self.disguise_file).grid(row=1, column=1, sticky=(tk.E, tk.W), padx=5)
        ttk.Button(option_frame, text="浏览", command=self.browse_disguise_file).grid(row=1, column=2, padx=5)
        
        # 提取功能页面
        extract_frame = ttk.Frame(advanced_notebook)
        advanced_notebook.add(extract_frame, text="文件提取")
        
        extract_option = ttk.LabelFrame(extract_frame, text="提取选项")
        extract_option.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(extract_option, text="伪装文件:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(extract_option, textvariable=self.extract_input).grid(row=0, column=1, sticky=(tk.E, tk.W), padx=5)
        ttk.Button(extract_option, text="浏览", command=self.browse_extract_file).grid(row=0, column=2, padx=5)
        
        ttk.Label(extract_option, text="输出路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(extract_option, textvariable=self.extract_output).grid(row=1, column=1, sticky=(tk.E, tk.W), padx=5)
        ttk.Button(extract_option, text="浏览", command=self.browse_extract_output).grid(row=1, column=2, padx=5)
        
        ttk.Button(extract_option, text="提取文件", command=self.extract_file).grid(row=2, column=1, pady=5)
        
        # 右侧：压缩详情和状态
        info_frame = ttk.LabelFrame(right_frame, text="压缩详情", padding="5")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 系统监控
        monitor_frame = ttk.Frame(info_frame)
        monitor_frame.pack(fill=tk.X, pady=5)
        ttk.Label(monitor_frame, textvariable=self.cpu_usage).pack(side=tk.LEFT, padx=5)
        ttk.Label(monitor_frame, textvariable=self.memory_usage).pack(side=tk.LEFT, padx=5)
        ttk.Label(monitor_frame, textvariable=self.estimated_time).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(info_frame, mode='determinate', variable=self.progress_var)
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # 状态日志
        log_frame = ttk.LabelFrame(right_frame, text="状态日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # 底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="开始压缩", command=self.start_compression).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="高级设置", command=self.show_advanced_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="性能监控", command=self.show_performance_monitor).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="使用说明", command=self.show_help).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT, padx=5)
    
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
            
        # 分析文件并提供建议
        self.analyze_files(self.input_path.get())
        
        # 启动系统监控
        self.monitoring = True
        threading.Thread(target=self.monitor_system_resources, daemon=True).start()
        
        # 启动性能监控
        self.performance_monitor = PerformanceMonitor()
        self.performance_monitor.start_monitoring(
            interval=float(self.performance_interval.get())
        )
        
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
            
            # 获取用户输入的值进行验证
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
            
            # 获取压缩设置
            compression_level = self.compression_level.get()
            password = self.password.get() or None
            try:
                split_size = int(self.split_size.get()) * 1024 * 1024  # 换为字节
            except ValueError:
                split_size = 0
            
            filters = [
                {'id': py7zr.FILTER_LZMA2, 'preset': dict_size},
            ]
            
            self.log_message(f"开始压缩: {input_path}")
            start_time = time.time()
            total_size = self.get_size(input_path)
            processed_size = 0
            
            # 压缩过程中更新进度和估算时间
            def update_progress(file_size):
                nonlocal processed_size
                processed_size += file_size
                progress = (processed_size / total_size) * 100
                self.progress_var.set(progress)
                
                remaining_time = self.estimate_remaining_time(processed_size, total_size, start_time)
                self.estimated_time.set(remaining_time)
            
            # 如果需要分卷
            if split_size > 0:
                base_name = output_path.stem
                volume_number = 1
                current_archive = None
                current_size = 0
                
                for file_path in input_path.rglob('*'):
                    if file_path.is_file():
                        if current_archive is None or current_size >= split_size:
                            if current_archive:
                                current_archive.close()
                            volume_path = output_path.with_name(f"{base_name}.{volume_number:03d}.7z")
                            current_archive = py7zr.SevenZipFile(
                                str(volume_path), 'w',
                                filters=filters,
                                password=password
                            )
                            volume_number += 1
                            current_size = 0
                        
                        rel_path = file_path.relative_to(input_path)
                        current_archive.write(file_path, rel_path)
                        current_size += file_path.stat().st_size
                        self.log_message(f"正在压缩: {rel_path}")
                        update_progress(file_path.stat().st_size)
                
                if current_archive:
                    current_archive.close()
            else:
                # 单文件压缩
                with py7zr.SevenZipFile(
                    str(output_path), 'w',
                    filters=filters,
                    password=password
                ) as archive:
                    if input_path.is_file():
                        archive.write(input_path, input_path.name)
                    else:
                        for file_path in input_path.rglob('*'):
                            if file_path.is_file():
                                rel_path = file_path.relative_to(input_path)
                                archive.write(file_path, rel_path)
                                self.log_message(f"正在压缩: {rel_path}")
                                update_progress(file_path.stat().st_size)
            
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
            
            # 记录压缩历史
            compression_record = {
                'input_path': str(input_path),
                'output_path': str(output_path),
                'original_size': self.get_size(input_path),
                'compressed_size': compressed_size,
                'compression_level': self.compression_level.get(),
                'duration': end_time - start_time,
                'settings': {
                    'dict_size': self.dict_size.get(),
                    'thread_count': self.thread_count.get(),
                    'split_size': self.split_size.get()
                }
            }
            
            # 保存历史记录
            self.compression_history.add_record(compression_record)
            
            # 更新历史显示
            self.update_history_display()
            
            # 保存性能日志
            if self.log_performance.get():
                self.performance_monitor.save_performance_log(
                    f"performance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
            
            # 生成性能报告
            report = self.performance_monitor.generate_performance_report()
            self.log_message("性能报告:")
            self.log_message(f"平均CPU使用率: {report['cpu']['average']:.1f}%")
            self.log_message(f"最大CPU使用率: {report['cpu']['max']:.1f}%")
            self.log_message(f"平均内存使用: {report['memory']['average_used'] / 1024 / 1024:.1f}MB")
            self.log_message(f"峰值内存使用: {report['memory']['peak_used'] / 1024 / 1024:.1f}MB")
            
            # 如果使用了密码，在日志中提示（但不显示密码）
            if password:
                self.log_message("文件已加密保护")
            
            # 如果启用了伪装
            if self.disguise_enabled.get():
                output_path = self.apply_file_disguise(output_path)
            
        except Exception as e:
            self.log_message(f"错误: {str(e)}")
            messagebox.showerror("错误", str(e))
        finally:
            self.monitoring = False
            self.performance_monitor.stop_monitoring()
    
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

    def analyze_files(self, path):
        """分析文件类型并提供压缩建议"""
        file_types = {}
        total_size = 0
        
        def scan_files(path):
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                size = os.path.getsize(path)
                file_types[ext] = file_types.get(ext, 0) + size
                return size
            
            total = 0
            for item in os.scandir(path):
                if item.is_file():
                    ext = os.path.splitext(item.name)[1].lower()
                    size = item.stat().st_size
                    file_types[ext] = file_types.get(ext, 0) + size
                    total += size
                elif item.is_dir():
                    total += scan_files(item.path)
            return total
        
        total_size = scan_files(path)
        
        # 根据文件类型提供建议
        suggestions = []
        compressed_types = {'.jpg', '.jpeg', '.png', '.zip', '.rar', '.7z', '.gz', '.mp4', '.avi', '.mkv'}
        text_types = {'.txt', '.log', '.csv', '.xml', '.json'}
        
        for ext, size in file_types.items():
            percentage = (size / total_size) * 100
            if percentage < 1:  # 忽略占比很小的文件类型
                continue
                
            if ext in compressed_types:
                suggestions.append(f"{ext}文件 ({percentage:.1f}%) 建议使用STORE级别")
            elif ext in text_types:
                suggestions.append(f"{ext}文件 ({percentage:.1f}%) 建议使用ULTRA级别")
            else:
                suggestions.append(f"{ext}文件 ({percentage:.1f}%) 建议使用NORMAL级别")
        
        self.suggestion_text.configure(state='normal')
        self.suggestion_text.delete(1.0, tk.END)
        self.suggestion_text.insert(tk.END, "文件分析建议：\n" + "\n".join(suggestions))
        self.suggestion_text.configure(state='disabled')
        
    def monitor_system_resources(self):
        """监控系统资源使用情况"""
        while self.monitoring:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            self.cpu_usage.set(f"CPU: {cpu_percent}%")
            self.memory_usage.set(f"内存: {memory.percent}%")
            
            time.sleep(1)
            
    def estimate_remaining_time(self, processed_size, total_size, start_time):
        """估算剩余时间"""
        if processed_size == 0:
            return "预计剩余时间: 计算中..."
            
        elapsed_time = time.time() - start_time
        progress = processed_size / total_size
        if progress == 0:
            return "预计剩余时间: 计算中..."
            
        total_estimated_time = elapsed_time / progress
        remaining_time = total_estimated_time - elapsed_time
        
        # 转换为时分秒格式
        remaining = str(timedelta(seconds=int(remaining_time)))
        return f"预计剩余时间: {remaining}"
        
    def load_history(self):
        """加载历史记录"""
        history = self.compression_history.get_history()
        for record in history:
            self.history_tree.insert('', 'end', values=(
                record['timestamp'],
                record['input_path'],
                self.format_size(record['original_size']),
                f"{100 - (record['compressed_size'] / record['original_size']) * 100:.2f}%",
                str(timedelta(seconds=int(record['duration'])))
            ))
    
    def update_history_display(self):
        """更新历史记录显示"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.load_history()
    
    def add_batch_task(self):
        """添加批量任务"""
        paths = filedialog.askopenfilenames(title="选择要压缩的文件")
        if not paths:
            return
            
        for path in paths:
            # 获取优化建议
            recommendations = self.optimization_engine.analyze_file(path)
            
            task = {
                'input_path': path,
                'output_path': str(Path(path).with_suffix('.7z')),
                'status': '等待中',
                'settings': recommendations
            }
            
            self.task_queue.append(task)
            self.batch_tree.insert('', 'end', values=(
                task['status'],
                task['input_path'],
                f"级别:{recommendations['compression_level']}, 字典:{recommendations['dict_size']}MB"
            ))
    
    def start_batch_tasks(self):
        """开始执行批量任务"""
        if not self.task_queue:
            messagebox.showinfo("提示", "没有待处理的任务")
            return
            
        threading.Thread(target=self.process_batch_tasks, daemon=True).start()
    
    def process_batch_tasks(self):
        """处理批量任务队列"""
        while self.task_queue:
            task = self.task_queue[0]
            
            # 新任务状态
            task['status'] = '处理中'
            self.update_batch_display()
            
            # 应用推荐设置
            self.compression_level.set(task['settings']['compression_level'])
            self.dict_size.set(str(task['settings']['dict_size']))
            self.thread_count.set(str(task['settings']['thread_count']))
            self.split_size.set(str(task['settings']['split_size']))
            
            # 执行压缩
            self.input_path.set(task['input_path'])
            self.output_path.set(task['output_path'])
            self.compress_task()
            
            # 移除已完成的任务
            self.task_queue.pop(0)
            self.update_batch_display()
    
    def clear_batch_tasks(self):
        """清空任务队列"""
        self.task_queue.clear()
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)
    
    def show_advanced_settings(self):
        AdvancedSettingsDialog(self.root)
    
    def show_performance_monitor(self):
        if not hasattr(self, 'performance_monitor'):
            return
        if not self.performance_monitor.visualizer:
            self.performance_monitor.visualizer = PerformanceVisualizer(self.root)
    
    def show_help(self):
        """显示详细使用说明窗口"""
        help_window = tk.Toplevel(self.root)
        help_window.title("极限压缩工具 - 详细使用说明")
        help_window.geometry("800x600")
        
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 快速入门
        quick_frame = ttk.Frame(notebook)
        notebook.add(quick_frame, text="快速入门")
        quick_text = tk.Text(quick_frame, wrap=tk.WORD)
        quick_text.pack(fill=tk.BOTH, expand=True)
        quick_text.insert(tk.END, """
=== 快速入门指南 ===

【基本压缩步骤】
1. 选择文件或文件夹
   - 点击"浏览"按钮
   - 或直接拖放文件到输入框
   - 支持选择多个文件/文件夹

2. 确认输出位置
   - 默认在源文件同目录下创建.7z文件
   - 可点击输出路径旁的"浏览"按钮修改

3. 选择压缩级别
   - 普通文件推荐使用 NORMAL
   - 追求速度选择 FASTEST
   - 追求压缩比选择 ULTRA
   - 图片/视频等用 STORE

4. 点击"开压缩"即可

【界面说明】
• 左侧面板：基本设置区
  - 文件选择
  - 压缩级别选择
  - 线程数调整

• 右侧面板：压缩详情
  - 显示压缩建议
  - 文件分析结果

• 底部区域：
  - 系统资源监控
  - 压缩进度显示
  - 状态日志输出
""")
        quick_text.configure(state='disabled')
        
        # 压缩级别详解
        level_frame = ttk.Frame(notebook)
        notebook.add(level_frame, text="压缩级别详解")
        level_text = tk.Text(level_frame, wrap=tk.WORD)
        level_text.pack(fill=tk.BOTH, expand=True)
        level_text.insert(tk.END, """
=== 压缩级别详细说明 ===

【STORE - 存储模式】
• 特点：仅打包，不压缩
• 速度：极快
• CPU使用：最低
• 适用场景：
  - 已压缩的文件（jpg/png/mp4等）
  - 需要快速打包的场合
  - 加密文件但不需要压缩时

【FASTEST - 最快模式】
• 特点：基础压缩，速度优先
• 压缩比：10-20%
• CPU使用：低
• 适用场景：
  - 临时文件压缩
  - 大量小文件打包
  - 需要快速压缩的场合

【FAST - 快速模式】
• 特点：快速压缩，适中压缩比
• 压缩比：20-40%
• CPU使用：中低
• 适用场景：
  - 日常文件备份
  - 一般文档压缩
  - 需要较快速度时

【NORMAL - 标准模式】
• 特点：平衡速度和压缩比
• 压缩比：40-60%
• CPU使用：中等
• 适用场景：
  - 常规文件压缩
  - 日常使用推荐
  - 大多数情况的最佳选择

【MAXIMUM - 最大压缩】
• 特点：高压缩比优先
• 压缩比：60-70%
• CPU使用：高
• 适用场景：
  - 需要高压缩比的文件
  - 长期存储的文档
  - 网络传输大文件时

【ULTRA - 极限压缩】
• 特点：最高压缩比
• 压缩比：70-80%
• CPU使用：极高
• 适用场景：
  - 纯文本文件
  - 追求极限压缩比
  - 存储空间极其有限时
""")
        level_text.configure(state='disabled')
        
        # 高级功能说明
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="高级功能")
        advanced_text = tk.Text(advanced_frame, wrap=tk.WORD)
        advanced_text.pack(fill=tk.BOTH, expand=True)
        advanced_text.insert(tk.END, """
=== 高级功能说明 ===

【字典大小设置】
• 作用：影响压缩比和内存使用
• 范围：4MB - 1GB
• 建议：
  - 4MB：内存小于4GB时
  - 16MB：日常使用推荐
  - 64MB：追求压缩比时
  - 256MB以上：大文件压缩

【线程数调整】
• 默认：等于CPU核心数
• 建议：
  - 日常使用：核心数-1
  - 后台运行：核心数/2
  - 极限能：核心数+1

【分卷压缩】
• 功能：将大文件分割成小块
• 使用场景：
  - 压缩超大文件
  - 网络传输方便
  - 备份到移动设备
• 设置建议：
  - FAT32：4GB以下
  - 邮件附件：50MB以下
  - 网盘上传：根据限制设置

【加密功能】
• 加密方式：AES-256
• 可选功能：
  - 文件加密
  - 文件名加密
  - 加密算法选择
• 注意事项：
  - 请记住密码
  - 加密会降低压缩速度
  - 建议备份密码
                             
【文件伪装功能】
• 功能说明：
  - 将压缩文件隐藏在普通文件中
  - 保持文件可用性
  - 支持多种文件格式

• 支持的伪装类型：
  - MP4视频：将数据隐藏在视频文件的元数据中，视频可正常播放
  - JPG图片：在图片文件的注释段中存储数据，图片可正常查看
  - PDF文档：将数据存储在PDF文件的注释中，文档可正常打开
  - 合并到其他文件：可以选择任意文件作为载体，更加灵活

• 使用建议：
  - 选择较大的文件作为载体以避免引起注意
  - 建议对重要数据进行加密保护
  - 记录使用的伪装类型，方便后续提取

• 提取说明：
  1. 选择包含压缩数据的伪装文件
  2. 指定提取后的保存位置
  3. 点击"提取文件"开始提取
  4. 如果文件加密了，提取后需要输入密码

• 注意事项：
  - 伪装后文件大小会增加
  - 不同格式的文件有不同的存储限制
  - 建议先测试小文件再处理大文件
  - 定期备份重要数据

""")
        advanced_text.configure(state='disabled')
        
        # 性能优化建议
        optimization_frame = ttk.Frame(notebook)
        notebook.add(optimization_frame, text="性能优化")
        optimization_text = tk.Text(optimization_frame, wrap=tk.WORD)
        optimization_text.pack(fill=tk.BOTH, expand=True)
        optimization_text.insert(tk.END, """
=== 性能优化建议 ===

【系统要求】
• 最低配置：
  - CPU：双核心
  - 内存：4GB
  - 硬盘：速度>100MB/s
• 推荐配置：
  - CPU：四核心以上
  - 内存：8GB以上
  - 硬盘：SSD

【优化建议】
1. 提升压缩速度：
   • 降低压缩级别
   • 减小字典大小
   • 关闭不必要程序
   • 使用SSD存储

2. 提高压缩比：
   • 提高压缩级别
   • 增大字典大小
   • 启用固实压缩
   • 使用过滤器

3. 节省内存：
   • 降低字典大小
   • 减少线程数
   • 使用分卷压缩
   • 关闭其他程序

4. 提升稳定性：
   • 定期清理临时文件
   • 保持足够磁盘空间
   • 避免同时压缩多个文件
   • 定期检查系统更新
""")
        optimization_text.configure(state='disabled')
        
        # 常见问题
        faq_frame = ttk.Frame(notebook)
        notebook.add(faq_frame, text="常见问题")
        faq_text = tk.Text(faq_frame, wrap=tk.WORD)
        faq_text.pack(fill=tk.BOTH, expand=True)
        faq_text.insert(tk.END, """
=== 常见问题解答 ===

【压缩相关】
Q: 如何选择合适的压缩级别？
A: 根据文件类型和需求选择：
   • 图片/视频等用STORE
   • 日常文件用NORMAL
   • 追求压缩比用ULTRA

Q: 压缩速度很慢怎么办？
A: 可以尝试以下方法：
   • 降低压缩级别
   • 减少线程数
   • 减小字典大小
   • 关闭其他程序

Q: 压缩文件很大怎么办？
A: 建议使用分卷压缩：
   • 设置合适的分卷大小
   • 考虑传输方式
   • 注意存储介质限制

【错误处理】
Q: 提"内存不足"？
A: 尝试以下解决方案：
   • 减小字典大小
   • 关闭其他程序
   • 使用分卷压缩
   • 增加虚拟内存

Q: 压缩过程中断了怎么办？
A: 程序支持断点续传：
   • 重新打开程序
   • 选择相同设置
   • 继续未完成的任务

Q: 无法打开压缩文件？
A: 检查以下几点：
   • 文件是否完整
   • 密码是否正确
   • 7z格式是否支持
   • 尝试修复压缩包
""")
        faq_text.configure(state='disabled')
        
        # 底部按钮
        button_frame = ttk.Frame(help_window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="关闭", command=help_window.destroy).pack(side=tk.RIGHT)

    def browse_disguise_file(self):
        """浏览伪装文件"""
        filetypes = [
            ("MP4视频", "*.mp4"),
            ("JPG图片", "*.jpg;*.jpeg"),
            ("PDF文档", "*.pdf"),
            ("所有文件", "*.*")
        ]
        path = filedialog.askopenfilename(
            title="选择伪装文件",
            filetypes=filetypes
        )
        if path:
            self.disguise_file.set(path)

    def browse_extract_file(self):
        """浏览要提取的伪装文件"""
        path = filedialog.askopenfilename(
            title="选择伪装文件",
            filetypes=[
                ("所有支持的文件", "*.mp4;*.jpg;*.jpeg;*.pdf;*.*"),
                ("MP4文件", "*.mp4"),
                ("图片文件", "*.jpg;*.jpeg"),
                ("PDF文档", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )
        if path:
            self.extract_input.set(path)
            # 自动设置输出路径
            default_output = str(Path(path).with_name(f"extracted_{Path(path).stem}.7z"))
            self.extract_output.set(default_output)

    def browse_extract_output(self):
        """选择提取文件的输出路径"""
        path = filedialog.asksaveasfilename(
            title="选择输出路径",
            defaultextension=".7z",
            filetypes=[("7Z files", "*.7z"), ("All files", "*.*")]
        )
        if path:
            self.extract_output.set(path)

    def extract_file(self):
        """执行文件提取"""
        if not self.extract_input.get():
            messagebox.showerror("错误", "请选择要提取的文件")
            return
        if not self.extract_output.get():
            messagebox.showerror("错误", "请选择输出路径")
            return
        
        try:
            if self.extract_original_file(self.extract_input.get(), self.extract_output.get()):
                messagebox.showinfo("成功", "文件提取成功！")
                self.log_message(f"已从 {self.extract_input.get()} 提取文件到 {self.extract_output.get()}")
            else:
                messagebox.showerror("错误", "文件提取失败")
        except Exception as e:
            messagebox.showerror("错误", f"提取过程出错: {str(e)}")

    def apply_file_disguise(self, compressed_file):
        """
        将压缩文件伪装成其他格式，保持文件可用性
        """
        try:
            disguise_type = self.disguise_type.get()
            output_path = Path(compressed_file)
            
            if disguise_type == "合并到其他文件":
                if not self.disguise_file.get():
                    raise ValueError("请选择伪装文件")
                    
                disguise_path = Path(self.disguise_file.get())
                final_path = output_path.with_name(f"{disguise_path.stem}_merged{disguise_path.suffix}")
                
                # 读取原始文件
                with open(disguise_path, 'rb') as f:
                    original_data = f.read()
                    
                # 读取压缩数据
                with open(compressed_file, 'rb') as f:
                    compressed_data = f.read()
                
                # 根据文件类型选择合并方法
                if disguise_path.suffix.lower() in ['.jpg', '.jpeg']:
                    # 在JPEG文件的注释段中插入数据
                    final_data = self._merge_into_jpeg(original_data, compressed_data)
                elif disguise_path.suffix.lower() == '.mp4':
                    # 在MP4文件的metadata中插入数据
                    final_data = self._merge_into_mp4(original_data, compressed_data)
                elif disguise_path.suffix.lower() == '.pdf':
                    # 在PDF文件的注释中插入数据
                    final_data = self._merge_into_pdf(original_data, compressed_data)
                else:
                    # 默认方法：在文件末尾添加数据
                    final_data = original_data + b'[COMPRESSED_DATA]' + compressed_data
                
                # 写入最终文件
                with open(final_path, 'wb') as f:
                    f.write(final_data)
                
                # 删除原始压缩文件
                os.remove(compressed_file)
                self.log_message(f"文件已伪装为: {final_path.name}")
                return str(final_path)
            
            return compressed_file
            
        except Exception as e:
            self.log_message(f"伪装处理失败: {str(e)}")
            return compressed_file

    def _merge_into_jpeg(self, jpeg_data, compressed_data):
        """将压缩数据合并到JPEG文件中"""
        # 在JPEG的COM段中插入数据
        # FF FE 表示注释段开始
        comment_marker = b'\xFF\xFE'
        comment_length = len(compressed_data) + 2  # +2 for length bytes
        comment_header = comment_marker + comment_length.to_bytes(2, 'big')
        
        # 找到JPEG文件结尾标记
        eof_marker = b'\xFF\xD9'
        split_pos = jpeg_data.rindex(eof_marker)
        
        # 组合数据
        return jpeg_data[:split_pos] + comment_header + compressed_data + eof_marker

    def _merge_into_mp4(self, mp4_data, compressed_data):
        """压缩数据合并到MP4文件中"""
        # 在MP4的metadata atom中插入数据
        meta_header = b'meta'
        meta_size = len(compressed_data) + 8  # +8 for size and type
        meta_box = meta_size.to_bytes(4, 'big') + meta_header + compressed_data
        
        # 在moov atom之前插入meta atom
        moov_pos = mp4_data.find(b'moov')
        if moov_pos == -1:
            # 如果找不到moov atom，就添加到文件末尾
            return mp4_data + meta_box
        
        return mp4_data[:moov_pos] + meta_box + mp4_data[moov_pos:]

    def _merge_into_pdf(self, pdf_data, compressed_data):
        """将压缩数据合并到PDF文件中"""
        # 在PDF注释中插入数据
        comment = f"\n% Begin compressed data\n% {compressed_data.hex()}\n% End compressed data\n"
        
        # 在PDF文件末尾添加注释
        return pdf_data + comment.encode('utf-8')

    @staticmethod
    def extract_original_file(disguised_file, output_path):
        """从伪装文件中提取原始压缩文件"""
        try:
            with open(disguised_file, 'rb') as f:
                data = f.read()
            
            # 尝试不同的提取方法
            compressed_data = None
            
            # 检查文件类型
            if disguised_file.lower().endswith(('.jpg', '.jpeg')):
                # 从JPEG注释段提取
                comment_marker = b'\xFF\xFE'
                pos = data.find(comment_marker)
                if pos != -1:
                    length = int.from_bytes(data[pos+2:pos+4], 'big')
                    compressed_data = data[pos+4:pos+4+length-2]
            
            elif disguised_file.lower().endswith('.mp4'):
                # 从MP4 meta atom提取
                meta_pos = data.find(b'meta')
                if meta_pos != -1:
                    size = int.from_bytes(data[meta_pos-4:meta_pos], 'big')
                    compressed_data = data[meta_pos+4:meta_pos+size]
            
            elif disguised_file.lower().endswith('.pdf'):
                # 从PDF注释提取
                start_marker = b'% Begin compressed data\n% '
                end_marker = b'\n% End compressed data'
                start_pos = data.find(start_marker)
                if start_pos != -1:
                    end_pos = data.find(end_marker, start_pos)
                    hex_data = data[start_pos+len(start_marker):end_pos].decode('utf-8')
                    compressed_data = bytes.fromhex(hex_data)
            
            else:
                # 默认方法：查找标记
                marker = b'[COMPRESSED_DATA]'
                pos = data.find(marker)
                if pos != -1:
                    compressed_data = data[pos+len(marker):]
            
            if compressed_data:
                with open(output_path, 'wb') as f:
                    f.write(compressed_data)
                return True
            
            raise ValueError("无法从文件中提取压缩数据")
            
        except Exception as e:
            print(f"提取失败: {str(e)}")
            return False

    def on_disguise_type_changed(self, event=None):
        """处理伪装类型变更"""
        self.disguise_enabled.set(True)  # 选择类型时自动启用伪装
        disguise_type = self.disguise_type.get()
        if disguise_type == "合并到其他文件":
            self.browse_disguise_file()  # 自动打开文件选择对话框

class AdvancedSettingsDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("高级设置")
        self.dialog.geometry("600x700")
        self.dialog.resizable(False, False)
        
        # 创建设置变量
        self.create_variables()
        # 创建界面
        self.setup_ui()
        
    def create_variables(self):
        # 算法设置
        self.solid_mode = tk.BooleanVar(value=True)
        self.compression_method = tk.StringVar(value="LZMA2")
        self.block_size = tk.StringVar(value="16M")
        
        # 过滤器设置
        self.exclude_patterns = tk.StringVar()
        self.include_patterns = tk.StringVar()
        self.exclude_hidden = tk.BooleanVar(value=True)
        
        # 性能设置
        self.cpu_priority = tk.StringVar(value="Normal")
        self.memory_limit = tk.StringVar(value="50")
        self.temp_folder = tk.StringVar(value=tempfile.gettempdir())
        
        # 安全设置
        self.encrypt_filenames = tk.BooleanVar(value=False)
        self.encryption_method = tk.StringVar(value="AES-256")
        self.verify_after_compress = tk.BooleanVar(value=True)
        
        # 高级压缩设置
        self.fast_bytes = tk.StringVar(value="32")
        self.match_finder = tk.StringVar(value="BT4")
        self.word_size = tk.StringVar(value="32")
        
    def setup_ui(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 算法设置页面
        algorithm_frame = ttk.Frame(notebook)
        notebook.add(algorithm_frame, text="算法设置")
        self.setup_algorithm_frame(algorithm_frame)
        
        # 过滤器设置页面
        filter_frame = ttk.Frame(notebook)
        notebook.add(filter_frame, text="过滤器")
        self.setup_filter_frame(filter_frame)
        
        # 性能设置页面
        performance_frame = ttk.Frame(notebook)
        notebook.add(performance_frame, text="性能")
        self.setup_performance_frame(performance_frame)
        
        # 安全设置页面
        security_frame = ttk.Frame(notebook)
        notebook.add(security_frame, text="安全")
        self.setup_security_frame(security_frame)
        
        # 高级压缩设置页面
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="高级压缩")
        self.setup_advanced_frame(advanced_frame)
        
        # 按钮
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="确定", command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
    def setup_algorithm_frame(self, parent):
        # 固实压缩
        ttk.Checkbutton(parent, text="启用固实压缩（提高压缩比，但降低随机访问性能）", 
                       variable=self.solid_mode).pack(anchor=tk.W, padx=5, pady=5)
        
        # 压缩方法
        method_frame = ttk.LabelFrame(parent, text="压缩方法")
        method_frame.pack(fill=tk.X, padx=5, pady=5)
        methods = ["LZMA2", "LZMA", "BZip2", "PPMd", "Deflate"]
        for method in methods:
            ttk.Radiobutton(method_frame, text=method, value=method, 
                          variable=self.compression_method).pack(anchor=tk.W, padx=5, pady=2)
        
        # 块大小
        block_frame = ttk.LabelFrame(parent, text="块大小")
        block_frame.pack(fill=tk.X, padx=5, pady=5)
        sizes = ["4M", "8M", "16M", "32M", "64M", "128M", "256M"]
        ttk.Label(block_frame, text="更大的块大小可能提高压缩比，但需要更多内存").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Combobox(block_frame, values=sizes, textvariable=self.block_size, state="readonly").pack(padx=5, pady=2)
        
    def setup_filter_frame(self, parent):
        # 排除模式
        exclude_frame = ttk.LabelFrame(parent, text="排除文件/文件夹")
        exclude_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(exclude_frame, text="每行一个模式，支持通配符 * 和 ?").pack(anchor=tk.W, padx=5, pady=2)
        exclude_text = tk.Text(exclude_frame, height=5, width=50)
        exclude_text.pack(padx=5, pady=2)
        
        # 包含模式
        include_frame = ttk.LabelFrame(parent, text="仅包含文件/文件夹")
        include_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(include_frame, text="留空表示包含所有文件").pack(anchor=tk.W, padx=5, pady=2)
        include_text = tk.Text(include_frame, height=5, width=50)
        include_text.pack(padx=5, pady=2)
        
        # 其他选项
        ttk.Checkbutton(parent, text="排除隐藏文件和文件夹", 
                       variable=self.exclude_hidden).pack(anchor=tk.W, padx=5, pady=5)
        
    def setup_performance_frame(self, parent):
        # CPU优先级
        priority_frame = ttk.LabelFrame(parent, text="CPU优先级")
        priority_frame.pack(fill=tk.X, padx=5, pady=5)
        priorities = ["Low", "Below Normal", "Normal", "Above Normal", "High"]
        for priority in priorities:
            ttk.Radiobutton(priority_frame, text=priority, value=priority, 
                          variable=self.cpu_priority).pack(anchor=tk.W, padx=5, pady=2)
        
        # 内存限制
        memory_frame = ttk.LabelFrame(parent, text="内存使用限制")
        memory_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(memory_frame, text="系统内存使用上限 (%)").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Scale(memory_frame, from_=10, to=90, variable=self.memory_limit, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=2)
        
        # 临时文件夹
        temp_frame = ttk.LabelFrame(parent, text="临时文件夹")
        temp_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Entry(temp_frame, textvariable=self.temp_folder).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        ttk.Button(temp_frame, text="浏览", command=self.browse_temp).pack(side=tk.RIGHT, padx=5, pady=2)
        
    def setup_security_frame(self, parent):
        # 加密设置
        encrypt_frame = ttk.LabelFrame(parent, text="加密设置")
        encrypt_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(encrypt_frame, text="加密文件名", 
                       variable=self.encrypt_filenames).pack(anchor=tk.W, padx=5, pady=2)
        
        # 加密方法
        methods = ["AES-256", "AES-192", "AES-128"]
        ttk.Label(encrypt_frame, text="加密算法:").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Combobox(encrypt_frame, values=methods, textvariable=self.encryption_method, 
                    state="readonly").pack(padx=5, pady=2)
        
        # 验证设置
        verify_frame = ttk.LabelFrame(parent, text="验证设置")
        verify_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Checkbutton(verify_frame, text="压缩后验证文件完整性", 
                       variable=self.verify_after_compress).pack(anchor=tk.W, padx=5, pady=2)
        
    def setup_advanced_frame(self, parent):
        # 快速节设置
        fast_frame = ttk.LabelFrame(parent, text="Fast Bytes")
        fast_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(fast_frame, text="更大的值可能提高压缩比，但会降低速度").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Entry(fast_frame, textvariable=self.fast_bytes).pack(padx=5, pady=2)
        
        # 匹配查找器
        finder_frame = ttk.LabelFrame(parent, text="Match Finder")
        finder_frame.pack(fill=tk.X, padx=5, pady=5)
        finders = ["HC4", "BT2", "BT3", "BT4"]
        for finder in finders:
            ttk.Radiobutton(finder_frame, text=finder, value=finder, 
                          variable=self.match_finder).pack(anchor=tk.W, padx=5, pady=2)
        
        # 字长设置
        word_frame = ttk.LabelFrame(parent, text="Word Size")
        word_frame.pack(fill=tk.X, padx=5, pady=5)
        sizes = ["8", "16", "32", "64"]
        ttk.Label(word_frame, text="更大的字长可能提高压缩比，但需要更多内存").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Combobox(word_frame, values=sizes, textvariable=self.word_size, 
                    state="readonly").pack(padx=5, pady=2)
        
    def browse_temp(self):
        folder = filedialog.askdirectory(title="选择临时文件夹")
        if folder:
            self.temp_folder.set(folder)
            
    def save_settings(self):
        # 保存设置到配置文件
        settings = {
            'algorithm': {
                'solid_mode': self.solid_mode.get(),
                'compression_method': self.compression_method.get(),
                'block_size': self.block_size.get()
            },
            'filter': {
                'exclude_patterns': self.exclude_patterns.get(),
                'include_patterns': self.include_patterns.get(),
                'exclude_hidden': self.exclude_hidden.get()
            },
            'performance': {
                'cpu_priority': self.cpu_priority.get(),
                'memory_limit': self.memory_limit.get(),
                'temp_folder': self.temp_folder.get()
            },
            'security': {
                'encrypt_filenames': self.encrypt_filenames.get(),
                'encryption_method': self.encryption_method.get(),
                'verify_after_compress': self.verify_after_compress.get()
            },
            'advanced': {
                'fast_bytes': self.fast_bytes.get(),
                'match_finder': self.match_finder.get(),
                'word_size': self.word_size.get()
            }
        }
        
        with open('compression_settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
            
        self.dialog.destroy()

class CompressionHistory:
    def __init__(self):
        self.db_path = "compression_history.db"
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS compression_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    input_path TEXT,
                    output_path TEXT,
                    original_size INTEGER,
                    compressed_size INTEGER,
                    compression_level TEXT,
                    duration REAL,
                    settings TEXT
                )
            """)
    
    def add_record(self, record: Dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO compression_history 
                (timestamp, input_path, output_path, original_size, 
                compressed_size, compression_level, duration, settings)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                record['input_path'],
                record['output_path'],
                record['original_size'],
                record['compressed_size'],
                record['compression_level'],
                record['duration'],
                json.dumps(record['settings'])
            ))
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM compression_history 
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

class OptimizationEngine:
    def __init__(self):
        self.file_type_stats = {}
        self.compression_stats = {}
    
    def analyze_file(self, file_path: str) -> Dict:
        """分析文件并提供优化建议"""
        ext = Path(file_path).suffix.lower()
        size = os.path.getsize(file_path)
        
        recommendations = {
            'compression_level': self.recommend_compression_level(ext, size),
            'dict_size': self.recommend_dict_size(size),
            'thread_count': self.recommend_thread_count(size),
            'split_size': self.recommend_split_size(size)
        }
        
        return recommendations
    
    def recommend_compression_level(self, ext: str, size: int) -> str:
        """根据文件类型和大小推荐压缩级别"""
        compressed_types = {'.jpg', '.jpeg', '.png', '.zip', '.rar', '.7z', '.gz', '.mp4', '.avi', '.mkv'}
        text_types = {'.txt', '.log', '.csv', '.xml', '.json', '.py', '.java', '.cpp', '.h'}
        
        if ext in compressed_types:
            return "STORE"
        elif ext in text_types:
            return "ULTRA"
        elif size > 1024 * 1024 * 1024:  # 大于1GB
            return "MAXIMUM"
        else:
            return "NORMAL"
    
    def recommend_dict_size(self, file_size: int) -> int:
        """推荐字典大小"""
        available_memory = psutil.virtual_memory().available
        if file_size < 100 * 1024 * 1024:  # 小于100MB
            return 16
        elif file_size < 1024 * 1024 * 1024:  # 小于1GB
            return min(256, available_memory // (1024 * 1024 * 4))
        else:
            return min(1024, available_memory // (1024 * 1024 * 4))
    
    def recommend_thread_count(self, file_size: int) -> int:
        """推荐线程数"""
        cpu_count = os.cpu_count() or 4
        if file_size < 100 * 1024 * 1024:  # 小于100MB
            return max(1, cpu_count // 2)
        else:
            return cpu_count
    
    def recommend_split_size(self, file_size: int) -> int:
        """推荐分卷大小（MB）"""
        if file_size < 1024 * 1024 * 1024:  # 小于1GB
            return 0
        elif file_size < 4 * 1024 * 1024 * 1024:  # 小于4GB
            return 2048
        else:
            return 4096

class PerformanceMonitor:
    def __init__(self):
        self.monitoring = False
        self.data = {
            'cpu': [],
            'memory': [],
            'disk_io': [],
            'compression': [],
            'speed': []
        }
        
        self.visualizer = None
        self.advisor = OptimizationAdvisor()
        self.warnings_enabled = True
        
    def start_monitoring(self, interval=1):
        self.monitoring = True
        threading.Thread(target=self.monitor_loop, args=(interval,), 
                       daemon=True).start()
        
    def stop_monitoring(self):
        self.monitoring = False
        
    def monitor_loop(self, interval):
        while self.monitoring:
            # CPU使用率
            if self.monitor_cpu_cores:
                cpu_percent = psutil.cpu_percent(percpu=True)
                self.data['cpu'].append({
                    'timestamp': time.time(),
                    'values': cpu_percent
                })
            
            # 内存使情况
            if self.monitor_memory_details:
                memory = psutil.virtual_memory()
                self.data['memory'].append({
                    'timestamp': time.time(),
                    'total': memory.total,
                    'used': memory.used,
                    'free': memory.free,
                    'cached': memory.cached
                })
            
            # 磁盘I/O
            if self.monitor_disk_io:
                disk_io = psutil.disk_io_counters()
                self.data['disk_io'].append({
                    'timestamp': time.time(),
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes
                })
            
            time.sleep(interval)
            
    def save_performance_log(self, filename):
        """保存性能监控数据到文件"""
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=4)
            
    def generate_performance_report(self):
        """生成性能报告"""
        report = {
            'cpu': {
                'average': sum(d['values'][0] for d in self.data['cpu']) / len(self.data['cpu']),
                'max': max(d['values'][0] for d in self.data['cpu'])
            },
            'memory': {
                'average_used': sum(d['used'] for d in self.data['memory']) / len(self.data['memory']),
                'peak_used': max(d['used'] for d in self.data['memory'])
            },
            'disk_io': {
                'total_read': self.data['disk_io'][-1]['read_bytes'] - self.data['disk_io'][0]['read_bytes'],
                'total_write': self.data['disk_io'][-1]['write_bytes'] - self.data['disk_io'][0]['write_bytes']
            }
        }
        return report
    
    def update_visualization(self):
        if not self.visualizer:
            return
            
        # 更新CPU图表
        self.visualizer.cpu_ax.clear()
        self.visualizer.cpu_ax.plot(self.get_cpu_data())
        
        # 更新内存图表
        self.visualizer.mem_ax.clear()
        self.visualizer.mem_ax.plot(self.get_memory_data())
        
        # 更新速度图表
        self.visualizer.speed_ax.clear()
        self.visualizer.speed_ax.plot(self.get_speed_data())
        
        self.visualizer.canvas.draw()
        
    def check_warnings(self):
        if not self.warnings_enabled:
            return
            
        warnings, suggestions = self.advisor.analyze_performance(self.get_current_data())
        if warnings:
            messagebox.showwarning("性能警告", 
                                 "\n".join(warnings) + "\n\n建议：\n" + "\n".join(suggestions))

class PerformanceVisualizer:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("性能监控")
        self.window.geometry("800x600")
        
        # 创建图表
        self.setup_charts()
        
    def setup_charts(self):
        # 使用matplotlib创建图表
        self.fig = Figure(figsize=(8, 6))
        
        # CPU使用率图表
        self.cpu_ax = self.fig.add_subplot(311)
        self.cpu_ax.set_title("CPU使用率")
        self.cpu_ax.set_ylabel("%")
        
        # 内存使用图表
        self.mem_ax = self.fig.add_subplot(312)
        self.mem_ax.set_title("内存使用")
        self.mem_ax.set_ylabel("MB")
        
        # 压缩速度图表
        self.speed_ax = self.fig.add_subplot(313)
        self.speed_ax.set_title("压缩速度")
        self.speed_ax.set_ylabel("MB/s")
        
        # 添加到界面
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

class OptimizationAdvisor:
    def __init__(self):
        self.thresholds = {
            'cpu_warning': 90,
            'memory_warning': 80,
            'speed_warning': 5
        }
        
    def analyze_performance(self, data):
        warnings = []
        suggestions = []
        
        # 分析CPU使用
        if data['cpu']['average'] > self.thresholds['cpu_warning']:
            warnings.append("CPU使用率过高")
            suggestions.append("建议降低压缩级别或减少线程数")
            
        # 分析内存使用
        if data['memory']['usage_percent'] > self.thresholds['memory_warning']:
            warnings.append("内存使用率过高")
            suggestions.append("建议减小字典大小或降低压缩级别")
            
        return warnings, suggestions

if __name__ == "__main__":
    root = tk.Tk()
    app = CompressionGUI(root)
    root.mainloop()
