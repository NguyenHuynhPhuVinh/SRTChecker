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

class SRTFixer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SRT Format Fixer - Sửa lỗi định dạng file SRT")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Tạo giao diện
        self.create_widgets()
        
    def create_widgets(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="SRT Format Fixer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Chọn file chính
        ttk.Label(main_frame, text="File SRT chính (cần sửa):").grid(row=1, column=0, sticky=tk.W, pady=5)

        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(file_frame, text="Chọn file",
                  command=self.select_file).grid(row=0, column=1)

        file_frame.columnconfigure(0, weight=1)

        # Chọn file phụ để merge
        ttk.Label(main_frame, text="File SRT phụ (để chèn vào chỗ thiếu) - Tùy chọn:").grid(row=3, column=0, sticky=tk.W, pady=(15, 5))

        merge_frame = ttk.Frame(main_frame)
        merge_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.merge_file_var = tk.StringVar()
        self.merge_entry = ttk.Entry(merge_frame, textvariable=self.merge_file_var, width=50)
        self.merge_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Button(merge_frame, text="Chọn file",
                  command=self.select_merge_file).grid(row=0, column=1)

        merge_frame.columnconfigure(0, weight=1)
        
        # Tùy chọn
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn", padding="5")
        options_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.fix_structure_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Sửa cấu trúc SRT",
                       variable=self.fix_structure_var).grid(row=0, column=0, sticky=tk.W)

        self.fix_encoding_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Sửa lỗi encoding",
                       variable=self.fix_encoding_var).grid(row=0, column=1, sticky=tk.W)

        self.validate_time_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Kiểm tra logic thời gian",
                       variable=self.validate_time_var).grid(row=1, column=0, sticky=tk.W)

        self.merge_subtitles_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Chèn subtitle từ file phụ",
                       variable=self.merge_subtitles_var).grid(row=1, column=1, sticky=tk.W)

        # Tùy chọn merge
        merge_options_frame = ttk.Frame(options_frame)
        merge_options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(merge_options_frame, text="Khoảng cách tối thiểu (giây):").grid(row=0, column=0, sticky=tk.W)
        self.min_gap_var = tk.StringVar(value="2.0")
        ttk.Entry(merge_options_frame, textvariable=self.min_gap_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(merge_options_frame, text="Độ dài tối thiểu (giây):").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.min_duration_var = tk.StringVar(value="1.0")
        ttk.Entry(merge_options_frame, textvariable=self.min_duration_var, width=10).grid(row=0, column=3, padx=5)

        # Nút sửa
        ttk.Button(main_frame, text="Sửa lỗi SRT",
                  command=self.fix_srt_threaded).grid(row=6, column=0, columnspan=2, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Text area để hiển thị log
        ttk.Label(main_frame, text="Kết quả:").grid(row=8, column=0, sticky=tk.W, pady=(20, 5))

        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(text_frame, height=15, width=70)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Cấu hình grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(9, weight=1)
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
        """Thêm message vào log text"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
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
                    self.log(f"Đã đọc file với encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                raise Exception("Không thể đọc file với bất kỳ encoding nào")

            self.log(f"Đã đọc file: {input_file}")

            # Chuẩn hóa line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.split('\n')

            # Bước 1: Sửa cấu trúc SRT (nếu được chọn)
            structure_fixes = 0
            if self.fix_structure_var.get():
                self.log("Đang kiểm tra cấu trúc SRT...")
                original_lines_count = len(lines)
                lines = self.validate_srt_structure(lines)
                structure_fixes = abs(len(lines) - original_lines_count)
                if structure_fixes > 0:
                    self.log(f"Đã sửa {structure_fixes} lỗi cấu trúc")

            # Bước 2: Sửa định dạng thời gian
            self.log("Đang sửa định dạng thời gian...")
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

            # Bước 3: Merge subtitle từ file phụ (nếu được chọn)
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
                
            # Bắt đầu progress bar
            self.progress.start()
            
            # Xóa log cũ
            self.log_text.delete(1.0, tk.END)
            
            self.log("Bắt đầu sửa file SRT...")
            
            success, output_file, fixes_count = self.fix_srt_file(file_path)
            
            # Dừng progress bar
            self.progress.stop()
            
            if success:
                merge_text = ""
                if self.merge_subtitles_var.get() and self.merge_file_var.get():
                    merge_text = f"\nĐã merge subtitle từ file phụ!"

                messagebox.showinfo("Thành công",
                                  f"Hoàn thành xử lý với {fixes_count} thay đổi!{merge_text}\nFile đã lưu: {output_file}")
            else:
                messagebox.showerror("Lỗi", "Có lỗi xảy ra khi xử lý file!")
        
        # Chạy trong thread riêng để không block UI
        thread = threading.Thread(target=run_fix)
        thread.daemon = True
        thread.start()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SRTFixer()
    app.run()
