#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để sửa lỗi định dạng file SRT
Sửa các lỗi thời gian không đúng format chuẩn SRT
"""

import re
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from tkinter import font

class SRTFixer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔧 SRT Format Fixer - Công cụ sửa lỗi định dạng file SRT")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Cấu hình theme và màu sắc
        self.setup_theme()

        # Tạo giao diện
        self.create_widgets()

    def setup_theme(self):
        """Cấu hình theme và màu sắc"""
        # Cấu hình màu nền
        self.root.configure(bg='#f0f0f0')

        # Tạo style cho ttk
        self.style = ttk.Style()

        # Thử sử dụng theme hiện đại
        try:
            self.style.theme_use('clam')
        except:
            try:
                self.style.theme_use('alt')
            except:
                pass

        # Cấu hình màu sắc custom
        self.colors = {
            'primary': '#2196F3',      # Blue
            'secondary': '#4CAF50',    # Green
            'accent': '#FF9800',       # Orange
            'danger': '#F44336',       # Red
            'dark': '#212121',         # Dark Gray
            'light': '#FAFAFA',        # Light Gray
            'white': '#FFFFFF',
            'text': '#333333'
        }

        # Cấu hình style cho các widget
        self.style.configure('Title.TLabel',
                           font=('Segoe UI', 18, 'bold'),
                           foreground=self.colors['primary'])

        self.style.configure('Heading.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           foreground=self.colors['dark'])

        self.style.configure('Custom.TButton',
                           font=('Segoe UI', 10),
                           padding=(10, 5))

        self.style.configure('Primary.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(15, 8))

        self.style.configure('Custom.TFrame',
                           relief='solid',
                           borderwidth=1)

        # Cấu hình icon cho window
        try:
            # Tạo icon đơn giản bằng text
            self.root.iconname("SRT Fixer")
        except:
            pass
        
    def create_widgets(self):
        # Container chính với padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header với icon và tiêu đề
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame,
                               text="🔧 SRT Format Fixer",
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(header_frame,
                                 text="Công cụ chuyên nghiệp sửa lỗi định dạng file SRT",
                                 font=('Segoe UI', 10),
                                 foreground='#666666')
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Section chọn file với card style
        files_card = ttk.LabelFrame(main_container, text="📁 Chọn File",
                                   style='Custom.TFrame', padding="15")
        files_card.pack(fill=tk.X, pady=(0, 15))

        # File chính
        main_file_frame = ttk.Frame(files_card)
        main_file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_file_frame, text="File SRT chính (cần sửa):",
                 style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))

        file_input_frame = ttk.Frame(main_file_frame)
        file_input_frame.pack(fill=tk.X)

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_input_frame, textvariable=self.file_path_var,
                                   font=('Segoe UI', 10))
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        ttk.Button(file_input_frame, text="📂 Chọn file",
                  command=self.select_file, style='Custom.TButton').pack(side=tk.RIGHT)

        # File phụ để merge
        merge_file_frame = ttk.Frame(files_card)
        merge_file_frame.pack(fill=tk.X)

        ttk.Label(merge_file_frame, text="File SRT phụ (để chèn vào chỗ thiếu) - Tùy chọn:",
                 style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))

        merge_input_frame = ttk.Frame(merge_file_frame)
        merge_input_frame.pack(fill=tk.X)

        self.merge_file_var = tk.StringVar()
        self.merge_entry = ttk.Entry(merge_input_frame, textvariable=self.merge_file_var,
                                   font=('Segoe UI', 10))
        self.merge_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        ttk.Button(merge_input_frame, text="📂 Chọn file",
                  command=self.select_merge_file, style='Custom.TButton').pack(side=tk.RIGHT)
        
        # Section tùy chọn với card style
        options_card = ttk.LabelFrame(main_container, text="⚙️ Tùy chọn xử lý",
                                     style='Custom.TFrame', padding="15")
        options_card.pack(fill=tk.X, pady=(0, 15))

        # Chia thành 2 cột
        left_options = ttk.Frame(options_card)
        left_options.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        right_options = ttk.Frame(options_card)
        right_options.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Cột trái
        self.fix_structure_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_options, text="🔧 Sửa cấu trúc SRT",
                       variable=self.fix_structure_var,
                       style='Custom.TCheckbutton').pack(anchor=tk.W, pady=2)

        self.fix_encoding_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_options, text="🔤 Sửa lỗi encoding",
                       variable=self.fix_encoding_var,
                       style='Custom.TCheckbutton').pack(anchor=tk.W, pady=2)

        self.validate_time_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(left_options, text="⏰ Kiểm tra logic thời gian",
                       variable=self.validate_time_var,
                       style='Custom.TCheckbutton').pack(anchor=tk.W, pady=2)

        # Cột phải
        self.merge_subtitles_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_options, text="🔗 Chèn subtitle từ file phụ",
                       variable=self.merge_subtitles_var,
                       style='Custom.TCheckbutton').pack(anchor=tk.W, pady=2)

        self.check_strange_chars_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_options, text="🔍 Kiểm tra ký tự lạ",
                       variable=self.check_strange_chars_var,
                       style='Custom.TCheckbutton').pack(anchor=tk.W, pady=2)

        # Tùy chọn merge (hiển thị khi cần)
        merge_options_frame = ttk.Frame(options_card)
        merge_options_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(merge_options_frame, text="🔧 Cài đặt merge:",
                 style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))

        merge_settings = ttk.Frame(merge_options_frame)
        merge_settings.pack(fill=tk.X)

        # Khoảng cách tối thiểu
        gap_frame = ttk.Frame(merge_settings)
        gap_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(gap_frame, text="Khoảng cách tối thiểu (giây):").pack(anchor=tk.W)
        self.min_gap_var = tk.StringVar(value="2.0")
        ttk.Entry(gap_frame, textvariable=self.min_gap_var, width=8,
                 font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(2, 0))

        # Độ dài tối thiểu
        duration_frame = ttk.Frame(merge_settings)
        duration_frame.pack(side=tk.LEFT)

        ttk.Label(duration_frame, text="Độ dài tối thiểu (giây):").pack(anchor=tk.W)
        self.min_duration_var = tk.StringVar(value="1.0")
        ttk.Entry(duration_frame, textvariable=self.min_duration_var, width=8,
                 font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(2, 0))

        # Section action với nút chính
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(0, 15))

        # Nút chính với style đẹp
        self.main_button = ttk.Button(action_frame, text="🚀 Bắt đầu xử lý SRT",
                                     command=self.fix_srt_threaded,
                                     style='Primary.TButton')
        self.main_button.pack(pady=10)

        # Progress bar với style đẹp hơn
        progress_frame = ttk.Frame(action_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 5))

        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress.pack()

        # Status label
        self.status_label = ttk.Label(action_frame, text="Sẵn sàng xử lý",
                                     font=('Segoe UI', 9), foreground='#666666')
        self.status_label.pack()

        # Section kết quả với card style
        results_card = ttk.LabelFrame(main_container, text="📋 Kết quả xử lý",
                                     style='Custom.TFrame', padding="15")
        results_card.pack(fill=tk.BOTH, expand=True)

        # Text area với style đẹp hơn
        text_frame = ttk.Frame(results_card)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(text_frame,
                               font=('Consolas', 10),
                               bg='#f8f9fa',
                               fg='#333333',
                               relief='flat',
                               borderwidth=0,
                               wrap=tk.WORD,
                               padx=10,
                               pady=10)

        # Scrollbar với style đẹp
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Thêm placeholder text
        self.log_text.insert(tk.END, "💡 Chọn file SRT và nhấn 'Bắt đầu xử lý' để bắt đầu...\n")
        self.log_text.insert(tk.END, "📝 Kết quả xử lý sẽ hiển thị ở đây.\n")
        self.log_text.configure(state='disabled')
        
        # Cấu hình responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file SRT chính",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)

    def select_merge_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file SRT phụ để merge",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        if file_path:
            self.merge_file_var.set(file_path)
            
    def log(self, message):
        """Thêm message vào log text với style đẹp"""
        self.log_text.configure(state='normal')

        # Xóa placeholder text nếu đây là log đầu tiên
        if "💡 Chọn file SRT" in self.log_text.get(1.0, tk.END):
            self.log_text.delete(1.0, tk.END)

        # Thêm timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Format message với màu sắc
        if message.startswith("✓"):
            # Success message - màu xanh
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        elif message.startswith("⚠️") or message.startswith("Cảnh báo"):
            # Warning message - màu cam
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        elif message.startswith("❌") or message.startswith("Lỗi"):
            # Error message - màu đỏ
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        else:
            # Normal message
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")

        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()

    def update_status(self, status):
        """Cập nhật status label"""
        self.status_label.configure(text=status)
        
    def normalize_time_components(self, hours, minutes, seconds, milliseconds):
        """Chuẩn hóa các thành phần thời gian"""
        try:
            h = int(hours) if hours else 0
            m = int(minutes) if minutes else 0
            s = int(seconds) if seconds else 0
            ms = int(milliseconds) if milliseconds else 0

            # Đảm bảo giá trị hợp lệ
            h = max(0, min(99, h))  # Giới hạn giờ 0-99
            m = max(0, min(59, m))  # Phút 0-59
            s = max(0, min(59, s))  # Giây 0-59
            ms = max(0, min(999, ms))  # Millisecond 0-999

            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        except ValueError:
            return None

    def fix_time_format(self, time_str):
        """Sửa định dạng thời gian - phiên bản cải tiến"""
        # Loại bỏ khoảng trắng và ký tự đặc biệt
        time_str = time_str.strip()
        if not time_str:
            return time_str

        # Loại bỏ các ký tự không mong muốn
        time_str = re.sub(r'[^\d:,.\-]', '', time_str)

        # Thay thế dấu chấm bằng dấu phẩy cho milliseconds
        time_str = re.sub(r'\.(\d{1,3})$', r',\1', time_str)

        # Các pattern để sửa lỗi định dạng thời gian (từ cụ thể đến tổng quát)
        patterns = [
            # Pattern 1: Định dạng chuẩn HH:MM:SS,mmm - chỉ cần validate
            (r'^(\d{1,2}):(\d{1,2}):(\d{1,2}),(\d{1,3})$',
             lambda m: self.normalize_time_components(m.group(1), m.group(2), m.group(3), m.group(4))),

            # Pattern 2: HH:MM:SS.mmm (dấu chấm thay vì phẩy)
            (r'^(\d{1,2}):(\d{1,2}):(\d{1,2})\.(\d{1,3})$',
             lambda m: self.normalize_time_components(m.group(1), m.group(2), m.group(3), m.group(4))),

            # Pattern 3: MM:SS,mmm (thiếu giờ)
            (r'^(\d{1,2}):(\d{1,2}),(\d{1,3})$',
             lambda m: self.normalize_time_components(0, m.group(1), m.group(2), m.group(3))),

            # Pattern 4: MM:SS.mmm (thiếu giờ, dấu chấm)
            (r'^(\d{1,2}):(\d{1,2})\.(\d{1,3})$',
             lambda m: self.normalize_time_components(0, m.group(1), m.group(2), m.group(3))),

            # Pattern 5: HH:MM:SS (thiếu milliseconds)
            (r'^(\d{1,2}):(\d{1,2}):(\d{1,2})$',
             lambda m: self.normalize_time_components(m.group(1), m.group(2), m.group(3), 0)),

            # Pattern 6: MM:SS (thiếu giờ và milliseconds)
            (r'^(\d{1,2}):(\d{1,2})$',
             lambda m: self.normalize_time_components(0, m.group(1), m.group(2), 0)),

            # Pattern 7: HH:MM:SS:mmm (dấu : thay vì ,)
            (r'^(\d{1,2}):(\d{1,2}):(\d{1,2}):(\d{1,3})$',
             lambda m: self.normalize_time_components(m.group(1), m.group(2), m.group(3), m.group(4))),

            # Pattern 8: HHMMSS,mmm (thiếu dấu :)
            (r'^(\d{1,2})(\d{2})(\d{2}),(\d{1,3})$',
             lambda m: self.normalize_time_components(m.group(1), m.group(2), m.group(3), m.group(4))),

            # Pattern 9: HHMMSS (thiếu dấu : và milliseconds)
            (r'^(\d{1,2})(\d{2})(\d{2})$',
             lambda m: self.normalize_time_components(m.group(1), m.group(2), m.group(3), 0)),

            # Pattern 10: Chỉ có số (giây)
            (r'^(\d+)$',
             lambda m: self.normalize_time_components(0, 0, m.group(1), 0)),
        ]

        for pattern, replacement in patterns:
            match = re.match(pattern, time_str)
            if match:
                result = replacement(match)
                if result:  # Chỉ trả về nếu normalize thành công
                    return result

        # Nếu không match pattern nào, thử parse bằng cách khác
        return self.fallback_time_parse(time_str)

    def fallback_time_parse(self, time_str):
        """Phương pháp dự phòng để parse thời gian"""
        # Tách tất cả các số từ chuỗi
        numbers = re.findall(r'\d+', time_str)

        if not numbers:
            return time_str  # Không thể parse, trả về nguyên bản

        # Pad với 0 nếu thiếu thành phần
        while len(numbers) < 4:
            numbers.insert(0, '0')

        # Lấy 4 thành phần cuối (h, m, s, ms)
        if len(numbers) >= 4:
            h, m, s, ms = numbers[-4:]
        elif len(numbers) == 3:
            h, m, s, ms = '0', numbers[0], numbers[1], numbers[2]
        elif len(numbers) == 2:
            h, m, s, ms = '0', '0', numbers[0], numbers[1]
        else:
            h, m, s, ms = '0', '0', '0', numbers[0]

        return self.normalize_time_components(h, m, s, ms)

    def validate_srt_structure(self, lines):
        """Kiểm tra và sửa cấu trúc SRT - phiên bản cải tiến"""
        fixed_lines = []
        subtitle_number = 1
        i = 0

        # Loại bỏ BOM từ dòng đầu tiên nếu có
        if lines and lines[0].startswith('\ufeff'):
            lines[0] = lines[0][1:]

        while i < len(lines):
            line = lines[i].strip()

            # Bỏ qua dòng trống
            if not line:
                # Chỉ thêm dòng trống nếu không phải cuối file
                if i < len(lines) - 1:
                    fixed_lines.append('')
                i += 1
                continue

            # Sửa lỗi BOM trong từng dòng
            line = self.fix_encoding_issues(line)

            # Kiểm tra xem có phải số thứ tự subtitle không
            if line.isdigit():
                # Đảm bảo số thứ tự đúng
                fixed_lines.append(str(subtitle_number))
                subtitle_number += 1
                i += 1

                # Tìm dòng thời gian tiếp theo
                if i < len(lines):
                    time_line = lines[i].strip()
                    time_line = self.fix_encoding_issues(time_line)

                    if '-->' in time_line:
                        fixed_lines.append(time_line)
                        i += 1

                        # Thêm nội dung subtitle
                        content_lines = []
                        while (i < len(lines) and
                               lines[i].strip() and
                               not lines[i].strip().isdigit() and
                               '-->' not in lines[i]):
                            content = lines[i].rstrip()
                            content = self.fix_encoding_issues(content)
                            if content:  # Chỉ thêm nếu không rỗng
                                content_lines.append(content)
                            i += 1

                        # Thêm nội dung (ít nhất 1 dòng)
                        if content_lines:
                            fixed_lines.extend(content_lines)
                        else:
                            fixed_lines.append("...")  # Placeholder nếu thiếu nội dung

                        # Thêm dòng trống sau subtitle
                        fixed_lines.append('')
                    else:
                        # Thiếu dòng thời gian - có thể là lỗi cấu trúc
                        if self.is_likely_content(time_line):
                            # Đây có thể là nội dung bị lỗi cấu trúc
                            fixed_lines.append("00:00:00,000 --> 00:00:01,000")
                            fixed_lines.append(time_line)
                            fixed_lines.append('')
                        i += 1

            elif '-->' in line:
                # Dòng thời gian mà thiếu số thứ tự
                fixed_lines.append(str(subtitle_number))
                subtitle_number += 1
                fixed_lines.append(line)
                i += 1

                # Thêm nội dung subtitle
                content_lines = []
                while (i < len(lines) and
                       lines[i].strip() and
                       not lines[i].strip().isdigit() and
                       '-->' not in lines[i]):
                    content = lines[i].rstrip()
                    content = self.fix_encoding_issues(content)
                    if content:
                        content_lines.append(content)
                    i += 1

                if content_lines:
                    fixed_lines.extend(content_lines)
                else:
                    fixed_lines.append("...")

                fixed_lines.append('')

            else:
                # Dòng có thể là nội dung bị lỗi cấu trúc
                if self.is_likely_content(line):
                    # Tạo subtitle mới cho nội dung này
                    fixed_lines.append(str(subtitle_number))
                    subtitle_number += 1
                    fixed_lines.append("00:00:00,000 --> 00:00:01,000")
                    fixed_lines.append(line)
                    fixed_lines.append('')
                i += 1

        return fixed_lines

    def is_likely_content(self, text):
        """Kiểm tra xem text có phải là nội dung subtitle không"""
        if not text or text.isdigit():
            return False

        # Các từ khóa thường xuất hiện trong tên nhân vật hoặc nội dung
        content_indicators = ['...', '!', '?', 'Lv.', 'Hoàng Đế', 'Công Chúa']

        # Nếu có ký tự đặc biệt hoặc từ khóa, có thể là nội dung
        return any(indicator in text for indicator in content_indicators) or len(text) > 3
        
    def fix_srt_file(self, input_file):
        """Sửa file SRT - phiên bản cải tiến"""
        try:
            # Thử đọc với nhiều encoding khác nhau
            content = None
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']

            for encoding in encodings:
                try:
                    with open(input_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    self.log(f"📖 Đã đọc file với encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                raise Exception("Không thể đọc file với bất kỳ encoding nào")

            self.log(f"📁 Đã đọc file: {input_file}")

            # Chuẩn hóa line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.split('\n')

            # Bước 1: Sửa cấu trúc SRT (nếu được chọn)
            structure_fixes = 0
            if self.fix_structure_var.get():
                self.log("🔧 Đang kiểm tra cấu trúc SRT...")
                original_lines_count = len(lines)
                lines = self.validate_srt_structure(lines)
                structure_fixes = abs(len(lines) - original_lines_count)
                if structure_fixes > 0:
                    self.log(f"Đã sửa {structure_fixes} lỗi cấu trúc")

            # Bước 2: Kiểm tra ký tự lạ (nếu được chọn)
            strange_char_count = 0
            if self.check_strange_chars_var.get():
                self.log("🔍 Đang kiểm tra ký tự lạ...")
                strange_chars = self.check_strange_characters(lines)
                strange_char_count = self.report_strange_characters(strange_chars)

            # Bước 3: Sửa định dạng thời gian
            self.log("⏰ Đang sửa định dạng thời gian...")
            fixed_lines = []
            time_fixes = 0
            encoding_fixes = 0

            # Pattern cho dòng thời gian - linh hoạt hơn
            time_pattern = r'^(.+?)\s*-->\s*(.+?)$'

            for i, line in enumerate(lines):
                original_line = line
                line = line.strip()

                # Sửa lỗi encoding phổ biến (nếu được chọn)
                if self.fix_encoding_var.get():
                    fixed_encoding_line = self.fix_encoding_issues(line)
                    if fixed_encoding_line != line:
                        line = fixed_encoding_line
                        encoding_fixes += 1

                # Kiểm tra nếu là dòng thời gian
                match = re.match(time_pattern, line)
                if match:
                    start_time = match.group(1).strip()
                    end_time = match.group(2).strip()

                    # Sửa định dạng thời gian
                    fixed_start = self.fix_time_format(start_time)
                    fixed_end = self.fix_time_format(end_time)

                    # Kiểm tra logic thời gian (nếu được chọn)
                    if self.validate_time_var.get() and self.compare_timestamps(fixed_start, fixed_end) >= 0:
                        self.log(f"Cảnh báo dòng {i+1}: Thời gian kết thúc <= thời gian bắt đầu")
                        # Tự động sửa bằng cách thêm 1 giây
                        fixed_end = self.add_seconds_to_timestamp(fixed_start, 1)
                        self.log(f"  -> Đã tự động sửa thành: {fixed_start} --> {fixed_end}")

                    fixed_line = f"{fixed_start} --> {fixed_end}"

                    # Kiểm tra xem có thay đổi không
                    if fixed_line != line:
                        self.log(f"Dòng {i+1}: {line}")
                        self.log(f"  -> {fixed_line}")
                        time_fixes += 1

                    fixed_lines.append(fixed_line)
                else:
                    # Giữ nguyên dòng không phải thời gian, nhưng chuẩn hóa dòng trống
                    cleaned_line = original_line.rstrip()
                    fixed_lines.append(cleaned_line)

            # Tạo tên file output
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_fixed.srt"

            # Bước 4: Merge subtitle từ file phụ (nếu được chọn)
            merge_count = 0
            if self.merge_subtitles_var.get() and self.merge_file_var.get():
                merge_file = self.merge_file_var.get()
                if os.path.exists(merge_file):
                    self.log(f"\nĐang merge subtitle từ file: {merge_file}")

                    try:
                        min_gap = float(self.min_gap_var.get())
                        min_duration = float(self.min_duration_var.get())
                    except ValueError:
                        min_gap = 2.0
                        min_duration = 1.0
                        self.log("Sử dụng giá trị mặc định: gap=2s, duration=1s")

                    # Parse cả 2 file thành subtitle objects
                    main_subs = self.parse_srt_file_from_lines(fixed_lines)
                    merge_subs = self.parse_srt_file(merge_file)

                    if main_subs and merge_subs:
                        merged_subs, merge_count = self.merge_subtitles(
                            main_subs, merge_subs, min_gap, min_duration
                        )

                        # Chuyển lại thành format SRT
                        fixed_lines = self.subtitles_to_srt_content(merged_subs).split('\n')
                    else:
                        self.log("Không thể parse file để merge")
                else:
                    self.log(f"File merge không tồn tại: {merge_file}")

            # Chuẩn hóa dòng trống trước khi ghi file
            self.log("Đang chuẩn hóa dòng trống...")
            fixed_lines = self.normalize_blank_lines(fixed_lines)

            # Ghi file đã sửa với UTF-8 BOM để tương thích tốt hơn
            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(fixed_lines))

            total_fixes = time_fixes + encoding_fixes + structure_fixes + merge_count
            self.log(f"\n=== KẾT QUẢ ===")
            self.log(f"Sửa lỗi thời gian: {time_fixes}")
            self.log(f"Sửa lỗi encoding: {encoding_fixes}")
            self.log(f"Sửa lỗi cấu trúc: {structure_fixes}")
            self.log(f"Chèn subtitle: {merge_count}")
            if self.check_strange_chars_var.get():
                self.log(f"Ký tự lạ phát hiện: {strange_char_count}")
            self.log(f"Tổng cộng: {total_fixes} thay đổi")
            self.log(f"File đã sửa được lưu tại: {output_file}")

            return True, output_file, total_fixes

        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
            return False, None, 0

    def fix_encoding_issues(self, text):
        """Sửa các lỗi encoding phổ biến"""
        # Loại bỏ BOM (Byte Order Mark)
        if text.startswith('\ufeff'):
            text = text[1:]

        # Mapping các ký tự bị lỗi encoding phổ biến
        encoding_fixes = {
            'Ã¡': 'á', 'Ã ': 'à', 'Ã¢': 'â', 'Ã£': 'ã', 'Ã¤': 'ä',
            'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã«': 'ë',
            'Ã­': 'í', 'Ã¬': 'ì', 'Ã®': 'î', 'Ã¯': 'ï',
            'Ã³': 'ó', 'Ã²': 'ò', 'Ã´': 'ô', 'Ãµ': 'õ', 'Ã¶': 'ö',
            'Ãº': 'ú', 'Ã¹': 'ù', 'Ã»': 'û', 'Ã¼': 'ü',
            'Ã½': 'ý', 'Ã¿': 'ÿ',
            'Ã§': 'ç', 'Ã±': 'ñ',
            'â€™': "'", 'â€œ': '"', 'â€': '"', 'â€"': '–', 'â€"': '—',
            'Â': '', 'â€¦': '...', 'â€¢': '•',
            '\ufeff': '',  # BOM character
        }

        for wrong, correct in encoding_fixes.items():
            text = text.replace(wrong, correct)

        return text

    def compare_timestamps(self, time1, time2):
        """So sánh 2 timestamp, trả về -1 nếu time1 < time2, 0 nếu bằng, 1 nếu time1 > time2"""
        def time_to_seconds(time_str):
            try:
                # Parse HH:MM:SS,mmm
                time_part, ms_part = time_str.split(',')
                h, m, s = map(int, time_part.split(':'))
                ms = int(ms_part)
                return h * 3600 + m * 60 + s + ms / 1000.0
            except:
                return 0

        seconds1 = time_to_seconds(time1)
        seconds2 = time_to_seconds(time2)

        if seconds1 < seconds2:
            return -1
        elif seconds1 > seconds2:
            return 1
        else:
            return 0

    def add_seconds_to_timestamp(self, timestamp, seconds):
        """Thêm số giây vào timestamp"""
        try:
            time_part, ms_part = timestamp.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)

            total_seconds = h * 3600 + m * 60 + s + seconds
            total_ms = ms

            # Tính lại h, m, s
            new_h = total_seconds // 3600
            new_m = (total_seconds % 3600) // 60
            new_s = total_seconds % 60

            return f"{new_h:02d}:{new_m:02d}:{new_s:02d},{total_ms:03d}"
        except:
            return timestamp

    def normalize_blank_lines(self, lines):
        """Chuẩn hóa dòng trống trong SRT - đảm bảo chỉ có 1 dòng trống giữa các subtitle"""
        normalized = []
        prev_was_blank = False

        for line in lines:
            is_blank = not line.strip()

            if is_blank:
                # Chỉ thêm dòng trống nếu dòng trước không phải dòng trống
                if not prev_was_blank:
                    normalized.append('')
                prev_was_blank = True
            else:
                normalized.append(line)
                prev_was_blank = False

        # Loại bỏ dòng trống ở cuối file
        while normalized and not normalized[-1].strip():
            normalized.pop()

        return normalized

    def check_strange_characters(self, lines):
        """Kiểm tra và báo cáo ký tự lạ trong file"""
        strange_chars_found = []

        # Định nghĩa các ký tự được phép
        allowed_chars = set()

        # Chữ cái tiếng Anh
        allowed_chars.update('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # Số
        allowed_chars.update('0123456789')

        # Ký tự đặc biệt thông thường
        allowed_chars.update(' .,!?;:()[]{}"\'-_+=*&%$#@/\\|`~^<>')

        # Ký tự xuống dòng và tab
        allowed_chars.update('\n\r\t')

        # Ký tự tiếng Việt có dấu
        vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
        vietnamese_chars += vietnamese_chars.upper()
        allowed_chars.update(vietnamese_chars)

        # CHỈ cho phép ký tự cơ bản - TẤT CẢ ký tự tượng hình sẽ được báo cáo
        # Chỉ một số ký tự đặc biệt cơ bản nhất
        allowed_chars.update('…""''–—')

        # KHÔNG cho phép:
        # - Emoji và ký tự tượng hình
        # - Ký tự Nhật Bản (Hiragana, Katakana, Kanji)
        # - Ký tự Trung Quốc
        # - Các biểu tượng khác
        # => TẤT CẢ sẽ được báo cáo là ký tự lạ

        for line_num, line in enumerate(lines, 1):
            for char_pos, char in enumerate(line, 1):
                if char not in allowed_chars:
                    # Phân loại ký tự lạ
                    char_type = self.classify_strange_char(char)

                    # Tìm thấy ký tự lạ
                    char_info = {
                        'line': line_num,
                        'position': char_pos,
                        'char': char,
                        'unicode': ord(char),
                        'hex': hex(ord(char)),
                        'type': char_type,
                        'context': line.strip()[:50] + ('...' if len(line.strip()) > 50 else '')
                    }
                    strange_chars_found.append(char_info)

        return strange_chars_found

    def classify_strange_char(self, char):
        """Phân loại ký tự lạ"""
        unicode_val = ord(char)

        # Ký tự Nhật Bản
        if (0x3041 <= unicode_val <= 0x3096 or  # Hiragana
            0x30A1 <= unicode_val <= 0x30FA):   # Katakana
            return "KÝ TỰ NHẬT BẢN (HIRAGANA/KATAKANA)"

        # Ký tự Trung Quốc/Kanji
        if 0x4E00 <= unicode_val <= 0x9FFF:
            return "KÝ TỰ TRUNG QUỐC/KANJI"

        # Emoji và ký tự tượng hình
        if (0x1F600 <= unicode_val <= 0x1F64F or  # Emoticons
            0x1F300 <= unicode_val <= 0x1F5FF or  # Miscellaneous Symbols
            0x1F680 <= unicode_val <= 0x1F6FF or  # Transport and Map
            0x1F700 <= unicode_val <= 0x1F77F or  # Alchemical Symbols
            0x1F780 <= unicode_val <= 0x1F7FF or  # Geometric Shapes Extended
            0x1F800 <= unicode_val <= 0x1F8FF or  # Supplemental Arrows-C
            0x1F900 <= unicode_val <= 0x1F9FF or  # Supplemental Symbols and Pictographs
            0x1FA00 <= unicode_val <= 0x1FA6F or  # Chess Symbols
            0x1FA70 <= unicode_val <= 0x1FAFF or  # Symbols and Pictographs Extended-A
            0x2600 <= unicode_val <= 0x26FF or    # Miscellaneous Symbols
            0x2700 <= unicode_val <= 0x27BF or    # Dingbats
            0x2B00 <= unicode_val <= 0x2BFF):     # Miscellaneous Symbols and Arrows
            return "EMOJI/BIỂU TƯỢNG"

        # Ký tự điều khiển
        if unicode_val < 32 and char not in '\n\r\t':
            return "KÝ TỰ ĐIỀU KHIỂN"

        # BOM và ký tự đặc biệt
        if unicode_val == 0xFEFF:
            return "BOM (BYTE ORDER MARK)"

        # Ký tự thay thế/lỗi
        if unicode_val == 0xFFFD:
            return "KÝ TỰ THAY THẾ (ENCODING LỖI)"

        # Ký tự Latin mở rộng có thể là lỗi encoding
        if 0x00C0 <= unicode_val <= 0x024F:
            return "LATIN MỞ RỘNG (CÓ THỂ LỖI ENCODING)"

        # Các ký tự tượng hình khác
        if (0x2000 <= unicode_val <= 0x206F or  # General Punctuation
            0x2070 <= unicode_val <= 0x209F or  # Superscripts and Subscripts
            0x20A0 <= unicode_val <= 0x20CF or  # Currency Symbols
            0x20D0 <= unicode_val <= 0x20FF or  # Combining Diacritical Marks for Symbols
            0x2100 <= unicode_val <= 0x214F or  # Letterlike Symbols
            0x2150 <= unicode_val <= 0x218F or  # Number Forms
            0x2190 <= unicode_val <= 0x21FF or  # Arrows
            0x2200 <= unicode_val <= 0x22FF or  # Mathematical Operators
            0x2300 <= unicode_val <= 0x23FF or  # Miscellaneous Technical
            0x2400 <= unicode_val <= 0x243F or  # Control Pictures
            0x2440 <= unicode_val <= 0x245F or  # Optical Character Recognition
            0x2460 <= unicode_val <= 0x24FF or  # Enclosed Alphanumerics
            0x2500 <= unicode_val <= 0x257F or  # Box Drawing
            0x2580 <= unicode_val <= 0x259F or  # Block Elements
            0x25A0 <= unicode_val <= 0x25FF):   # Geometric Shapes
            return "KÝ TỰ TƯỢNG HÌNH/BIỂU TƯỢNG"

        # Ký tự khác
        return "KÝ TỰ KHÔNG XÁC ĐỊNH"

    def report_strange_characters(self, strange_chars):
        """Báo cáo ký tự lạ lên UI"""
        if not strange_chars:
            self.log("✓ Không tìm thấy ký tự lạ nào trong file")
            return 0

        self.log(f"\n⚠️  PHÁT HIỆN {len(strange_chars)} KÝ TỰ LẠ:")
        self.log("=" * 60)

        # Thống kê theo loại
        type_stats = {}
        for char_info in strange_chars:
            char_type = char_info.get('type', 'KHÔNG XÁC ĐỊNH')
            if char_type not in type_stats:
                type_stats[char_type] = 0
            type_stats[char_type] += 1

        self.log("📊 THỐNG KÊ THEO LOẠI:")
        for char_type, count in sorted(type_stats.items()):
            self.log(f"  • {char_type}: {count} ký tự")
        self.log("")

        # Thống kê theo loại
        type_stats = {}
        for char_info in strange_chars:
            char_type = char_info.get('type', 'KHÔNG XÁC ĐỊNH')
            if char_type not in type_stats:
                type_stats[char_type] = 0
            type_stats[char_type] += 1

        self.log("📊 THỐNG KÊ THEO LOẠI:")
        for char_type, count in sorted(type_stats.items()):
            self.log(f"  • {char_type}: {count} ký tự")
        self.log("")

        # Nhóm theo ký tự để tránh spam
        char_groups = {}
        for char_info in strange_chars:
            char = char_info['char']
            if char not in char_groups:
                char_groups[char] = []
            char_groups[char].append(char_info)

        for char, occurrences in char_groups.items():
            char_type = occurrences[0].get('type', 'KHÔNG XÁC ĐỊNH')
            self.log(f"\nKý tự: '{char}' - Loại: {char_type}")
            self.log(f"Unicode: {occurrences[0]['unicode']}, Hex: {occurrences[0]['hex']}")
            self.log(f"Xuất hiện {len(occurrences)} lần tại:")

            # Hiển thị tối đa 5 vị trí đầu tiên
            for i, info in enumerate(occurrences[:5]):
                self.log(f"  - Dòng {info['line']}, vị trí {info['position']}: {info['context']}")

            if len(occurrences) > 5:
                self.log(f"  ... và {len(occurrences) - 5} vị trí khác")

        self.log("=" * 60)
        self.log("💡 Gợi ý: Kiểm tra encoding file hoặc sử dụng tùy chọn 'Sửa lỗi encoding'")

        return len(strange_chars)

    def parse_srt_file(self, file_path):
        """Parse file SRT thành danh sách các subtitle"""
        try:
            # Đọc file với nhiều encoding
            content = None
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                return []

            # Chuẩn hóa line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')

            subtitles = []
            blocks = content.split('\n\n')

            for block in blocks:
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                if len(lines) >= 3:
                    # Tìm dòng thời gian
                    time_line = None
                    text_lines = []

                    for line in lines:
                        # Sửa lỗi BOM trước khi xử lý
                        line = self.fix_encoding_issues(line)

                        if '-->' in line:
                            time_line = line
                        elif not line.isdigit() and line.strip():  # Bỏ qua số thứ tự và dòng trống
                            text_lines.append(line)

                    if time_line and text_lines:
                        # Parse thời gian
                        try:
                            start_str, end_str = time_line.split('-->')
                            start_time = self.timestamp_to_seconds(start_str.strip())
                            end_time = self.timestamp_to_seconds(end_str.strip())

                            subtitles.append({
                                'start': start_time,
                                'end': end_time,
                                'text': '\n'.join(text_lines),
                                'original_time': time_line.strip()
                            })
                        except:
                            continue

            return sorted(subtitles, key=lambda x: x['start'])

        except Exception as e:
            self.log(f"Lỗi khi parse file {file_path}: {str(e)}")
            return []

    def timestamp_to_seconds(self, timestamp):
        """Chuyển timestamp thành giây"""
        try:
            time_part, ms_part = timestamp.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            return h * 3600 + m * 60 + s + ms / 1000.0
        except:
            return 0

    def seconds_to_timestamp(self, seconds):
        """Chuyển giây thành timestamp"""
        try:
            total_ms = int((seconds % 1) * 1000)
            total_seconds = int(seconds)

            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60

            return f"{h:02d}:{m:02d}:{s:02d},{total_ms:03d}"
        except:
            return "00:00:00,000"

    def find_gaps_in_subtitles(self, subtitles, min_gap=2.0):
        """Tìm các khoảng trống trong subtitle"""
        gaps = []

        for i in range(len(subtitles) - 1):
            current_end = subtitles[i]['end']
            next_start = subtitles[i + 1]['start']

            gap_duration = next_start - current_end
            if gap_duration >= min_gap:
                gaps.append({
                    'start': current_end,
                    'end': next_start,
                    'duration': gap_duration
                })

        return gaps

    def merge_subtitles(self, main_subtitles, merge_subtitles, min_gap=2.0, min_duration=1.0):
        """Merge subtitle từ file phụ vào file chính"""
        # Tìm khoảng trống trong file chính
        gaps = self.find_gaps_in_subtitles(main_subtitles, min_gap)

        merged_count = 0
        result_subtitles = main_subtitles.copy()

        self.log(f"Tìm thấy {len(gaps)} khoảng trống trong file chính")

        for gap in gaps:
            # Tìm subtitle từ file phụ phù hợp với khoảng trống này
            suitable_subs = []

            for sub in merge_subtitles:
                # Kiểm tra xem subtitle có nằm trong khoảng trống không
                if (sub['start'] >= gap['start'] and
                    sub['end'] <= gap['end'] and
                    (sub['end'] - sub['start']) >= min_duration):

                    # Kiểm tra không bị trùng với subtitle hiện có
                    overlap = False
                    for existing in result_subtitles:
                        if not (sub['end'] <= existing['start'] or sub['start'] >= existing['end']):
                            overlap = True
                            break

                    if not overlap:
                        suitable_subs.append(sub)

            # Thêm các subtitle phù hợp
            for sub in suitable_subs:
                result_subtitles.append(sub)
                merged_count += 1
                self.log(f"Đã chèn subtitle: {self.seconds_to_timestamp(sub['start'])} --> {self.seconds_to_timestamp(sub['end'])}")
                self.log(f"  Nội dung: {sub['text'][:50]}...")

        # Sắp xếp lại theo thời gian
        result_subtitles.sort(key=lambda x: x['start'])

        self.log(f"Đã chèn {merged_count} subtitle từ file phụ")
        return result_subtitles, merged_count

    def subtitles_to_srt_content(self, subtitles):
        """Chuyển danh sách subtitle thành nội dung SRT"""
        lines = []

        for i, sub in enumerate(subtitles, 1):
            lines.append(str(i))

            start_time = self.seconds_to_timestamp(sub['start'])
            end_time = self.seconds_to_timestamp(sub['end'])
            lines.append(f"{start_time} --> {end_time}")

            lines.append(sub['text'])

            # Chỉ thêm dòng trống nếu không phải subtitle cuối cùng
            if i < len(subtitles):
                lines.append('')

        return '\n'.join(lines)

    def parse_srt_file_from_lines(self, lines):
        """Parse SRT từ danh sách lines đã được xử lý"""
        try:
            content = '\n'.join(lines)

            subtitles = []
            blocks = content.split('\n\n')

            for block in blocks:
                block_lines = [line.strip() for line in block.split('\n') if line.strip()]
                if len(block_lines) >= 3:
                    # Tìm dòng thời gian
                    time_line = None
                    text_lines = []

                    for line in block_lines:
                        # Sửa lỗi BOM trước khi xử lý
                        line = self.fix_encoding_issues(line)

                        if '-->' in line:
                            time_line = line
                        elif not line.isdigit() and line.strip():  # Bỏ qua số thứ tự và dòng trống
                            text_lines.append(line)

                    if time_line and text_lines:
                        # Parse thời gian
                        try:
                            start_str, end_str = time_line.split('-->')
                            start_time = self.timestamp_to_seconds(start_str.strip())
                            end_time = self.timestamp_to_seconds(end_str.strip())

                            subtitles.append({
                                'start': start_time,
                                'end': end_time,
                                'text': '\n'.join(text_lines),
                                'original_time': time_line.strip()
                            })
                        except:
                            continue

            return sorted(subtitles, key=lambda x: x['start'])

        except Exception as e:
            self.log(f"Lỗi khi parse lines: {str(e)}")
            return []
            
    def fix_srt_threaded(self):
        """Chạy fix SRT trong thread riêng"""
        def run_fix():
            file_path = self.file_path_var.get()

            if not file_path:
                messagebox.showerror("Lỗi", "Vui lòng chọn file SRT chính!")
                return

            if not os.path.exists(file_path):
                messagebox.showerror("Lỗi", "File chính không tồn tại!")
                return

            # Kiểm tra file merge nếu được chọn
            if self.merge_subtitles_var.get():
                merge_file = self.merge_file_var.get()
                if not merge_file:
                    messagebox.showerror("Lỗi", "Vui lòng chọn file SRT phụ để merge!")
                    return
                if not os.path.exists(merge_file):
                    messagebox.showerror("Lỗi", "File SRT phụ không tồn tại!")
                    return
                
            # Bắt đầu progress bar và cập nhật UI
            self.progress.start()
            self.main_button.configure(state='disabled', text="⏳ Đang xử lý...")
            self.update_status("Đang xử lý file...")

            # Xóa log cũ
            self.log_text.configure(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.configure(state='disabled')

            self.log("🚀 Bắt đầu xử lý file SRT...")
            
            success, output_file, fixes_count = self.fix_srt_file(file_path)
            
            # Dừng progress bar và khôi phục UI
            self.progress.stop()
            self.main_button.configure(state='normal', text="🚀 Bắt đầu xử lý SRT")

            if success:
                self.update_status("✅ Hoàn thành!")
                merge_text = ""
                if self.merge_subtitles_var.get() and self.merge_file_var.get():
                    merge_text = f"\n🔗 Đã merge subtitle từ file phụ!"

                messagebox.showinfo("🎉 Thành công!",
                                  f"✅ Hoàn thành xử lý với {fixes_count} thay đổi!{merge_text}\n\n📁 File đã lưu: {output_file}")
            else:
                self.update_status("❌ Có lỗi xảy ra")
                messagebox.showerror("❌ Lỗi", "Có lỗi xảy ra khi xử lý file!")
        
        # Chạy trong thread riêng để không block UI
        thread = threading.Thread(target=run_fix)
        thread.daemon = True
        thread.start()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SRTFixer()
    app.run()
