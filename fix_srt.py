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
        
        # Chọn file
        ttk.Label(main_frame, text="Chọn file SRT cần sửa:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="Chọn file", 
                  command=self.select_file).grid(row=0, column=1)
        
        file_frame.columnconfigure(0, weight=1)
        
        # Nút sửa
        ttk.Button(main_frame, text="Sửa lỗi SRT", 
                  command=self.fix_srt_threaded).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Text area để hiển thị log
        ttk.Label(main_frame, text="Kết quả:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(text_frame, height=15, width=70)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Cấu hình grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file SRT",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            
    def log(self, message):
        """Thêm message vào log text"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def fix_time_format(self, time_str):
        """Sửa định dạng thời gian với validation kỹ hơn"""
        # Loại bỏ khoảng trắng
        time_str = time_str.strip()
        original_time = time_str

        # Các pattern để sửa lỗi định dạng thời gian
        patterns = [
            # Pattern 1: MM:SS,mmm (thiếu giờ) -> 00:MM:SS,mmm
            (r'^(\d{1,2}):(\d{2}),(\d{3})$', lambda m: f'00:{m.group(1).zfill(2)}:{m.group(2)},{m.group(3)}'),

            # Pattern 2: H:MM:mmm (dấu : thay vì ,) -> 0H:MM,mmm
            (r'^(\d):(\d{2}):(\d{3})$', lambda m: f'00:0{m.group(1)}:{m.group(2)},{m.group(3)}'),

            # Pattern 3: HH:MM:mmm (dấu : thay vì ,) -> HH:MM,mmm
            (r'^(\d{2}):(\d{2}):(\d{3})$', lambda m: f'00:{m.group(1)}:{m.group(2)},{m.group(3)}'),

            # Pattern 4: H:MM,mmm -> 0H:MM,mmm
            (r'^(\d):(\d{2}),(\d{3})$', lambda m: f'00:0{m.group(1)}:{m.group(2)},{m.group(3)}'),

            # Pattern 5: 00:0MM,mmm (thiếu số 0 ở phút) -> 00:MM,mmm
            (r'^(\d{2}):0(\d{1}),(\d{3})$', lambda m: f'{m.group(1)}:0{m.group(2)},{m.group(3)}'),

            # Pattern 6: 00:0MM:mmm (thiếu số 0 ở phút + dấu : thay vì ,) -> 00:0MM,mmm
            (r'^(\d{2}):0(\d{1}):(\d{3})$', lambda m: f'{m.group(1)}:0{m.group(2)},{m.group(3)}'),

            # Pattern 7: 00:MMM,mmm (3 chữ số phút - lỗi format) -> 00:0M:MM,mmm
            (r'^(\d{2}):(\d{3}),(\d{3})$', lambda m: f'{m.group(1)}:0{m.group(2)[0]}:{m.group(2)[1:]},{m.group(3)}'),

            # Pattern 8: 00:MMM:mmm (3 chữ số phút + dấu : thay vì ,) -> 00:0M:MM,mmm
            (r'^(\d{2}):(\d{3}):(\d{3})$', lambda m: f'{m.group(1)}:0{m.group(2)[0]}:{m.group(2)[1:]},{m.group(3)}'),
        ]

        for pattern, replacement in patterns:
            match = re.match(pattern, time_str)
            if match:
                if callable(replacement):
                    fixed_time = replacement(match)
                    # Validate format sau khi sửa
                    if self.validate_time_format(fixed_time):
                        return fixed_time
                else:
                    fixed_time = re.sub(pattern, replacement, time_str)
                    if self.validate_time_format(fixed_time):
                        return fixed_time

        # Nếu không match pattern nào, kiểm tra format chuẩn
        if self.validate_time_format(time_str):
            return time_str

        # Nếu vẫn không đúng format, trả về original và log warning
        return original_time

    def validate_time_format(self, time_str):
        """Kiểm tra định dạng thời gian có đúng chuẩn SRT không"""
        # Format chuẩn: HH:MM:SS,mmm
        pattern = r'^(\d{2}):(\d{2}):(\d{2}),(\d{3})$'
        match = re.match(pattern, time_str)
        if not match:
            return False

        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        milliseconds = int(match.group(4))

        # Kiểm tra giá trị hợp lệ
        return (0 <= hours <= 99 and
                0 <= minutes <= 59 and
                0 <= seconds <= 59 and
                0 <= milliseconds <= 999)

    def time_to_milliseconds(self, time_str):
        """Chuyển đổi thời gian sang milliseconds để so sánh"""
        if not self.validate_time_format(time_str):
            return None

        pattern = r'^(\d{2}):(\d{2}):(\d{2}),(\d{3})$'
        match = re.match(pattern, time_str)
        if not match:
            return None

        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        milliseconds = int(match.group(4))

        total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
        return total_ms

    def milliseconds_to_time(self, ms):
        """Chuyển đổi milliseconds về format thời gian SRT"""
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        milliseconds = ms % 1000

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
        
    def fix_srt_file(self, input_file):
        """Sửa file SRT với validation timeline"""
        try:
            # Đọc file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.log(f"Đã đọc file: {input_file}")

            lines = content.split('\n')
            fixed_lines = []
            format_fixes_count = 0
            timeline_fixes_count = 0

            # Pattern cho dòng thời gian - hỗ trợ nhiều định dạng
            time_pattern = r'^(.+?)\s*-->\s*(.+?)$'

            # Lưu trữ thông tin subtitle để kiểm tra timeline
            subtitles = []
            current_subtitle = {}

            # Pass 1: Sửa định dạng thời gian và thu thập thông tin subtitle
            for i, line in enumerate(lines):
                original_line = line
                line = line.strip()

                # Kiểm tra nếu là dòng thời gian
                match = re.match(time_pattern, line)
                if match:
                    start_time = match.group(1).strip()
                    end_time = match.group(2).strip()

                    # Sửa định dạng thời gian
                    fixed_start = self.fix_time_format(start_time)
                    fixed_end = self.fix_time_format(end_time)

                    fixed_line = f"{fixed_start} --> {fixed_end}"

                    # Kiểm tra xem có thay đổi không
                    if fixed_line != line:
                        self.log(f"[FORMAT] Dòng {i+1}: {line}")
                        self.log(f"  -> {fixed_line}")
                        format_fixes_count += 1

                    # Lưu thông tin subtitle
                    current_subtitle = {
                        'line_number': i,
                        'start_time': fixed_start,
                        'end_time': fixed_end,
                        'start_ms': self.time_to_milliseconds(fixed_start),
                        'end_ms': self.time_to_milliseconds(fixed_end)
                    }
                    subtitles.append(current_subtitle)

                    fixed_lines.append(fixed_line)
                else:
                    # Giữ nguyên dòng không phải thời gian
                    fixed_lines.append(original_line.rstrip())

            # Pass 2: Kiểm tra và sửa timeline logic
            self.log(f"\n=== KIỂM TRA TIMELINE ===")

            for i, subtitle in enumerate(subtitles):
                timeline_fixed = False

                # Kiểm tra start_time < end_time
                if subtitle['start_ms'] is not None and subtitle['end_ms'] is not None:
                    if subtitle['start_ms'] >= subtitle['end_ms']:
                        self.log(f"[TIMELINE] Subtitle {i+1}: Thời gian bắt đầu >= thời gian kết thúc")
                        self.log(f"  Trước: {subtitle['start_time']} --> {subtitle['end_time']}")

                        # Sửa bằng cách thêm 1 giây vào end_time
                        new_end_ms = subtitle['start_ms'] + 1000
                        new_end_time = self.milliseconds_to_time(new_end_ms)
                        subtitle['end_time'] = new_end_time
                        subtitle['end_ms'] = new_end_ms

                        # Cập nhật trong fixed_lines
                        fixed_lines[subtitle['line_number']] = f"{subtitle['start_time']} --> {subtitle['end_time']}"

                        self.log(f"  Sau: {subtitle['start_time']} --> {subtitle['end_time']}")
                        timeline_fixes_count += 1
                        timeline_fixed = True

                # Kiểm tra overlap với subtitle tiếp theo
                if i < len(subtitles) - 1:
                    next_subtitle = subtitles[i + 1]
                    if (subtitle['end_ms'] is not None and
                        next_subtitle['start_ms'] is not None and
                        subtitle['end_ms'] > next_subtitle['start_ms']):

                        self.log(f"[TIMELINE] Subtitle {i+1} và {i+2}: Thời gian overlap")
                        self.log(f"  Subtitle {i+1} kết thúc: {subtitle['end_time']}")
                        self.log(f"  Subtitle {i+2} bắt đầu: {next_subtitle['start_time']}")

                        # Sửa bằng cách điều chỉnh end_time của subtitle hiện tại
                        # để kết thúc 100ms trước khi subtitle tiếp theo bắt đầu
                        new_end_ms = max(subtitle['start_ms'] + 500, next_subtitle['start_ms'] - 100)
                        new_end_time = self.milliseconds_to_time(new_end_ms)
                        subtitle['end_time'] = new_end_time
                        subtitle['end_ms'] = new_end_ms

                        # Cập nhật trong fixed_lines
                        fixed_lines[subtitle['line_number']] = f"{subtitle['start_time']} --> {subtitle['end_time']}"

                        self.log(f"  Đã sửa subtitle {i+1} kết thúc: {subtitle['end_time']}")
                        timeline_fixes_count += 1
                        timeline_fixed = True

            # Tạo tên file output
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_fixed.srt"

            # Ghi file đã sửa
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))

            total_fixes = format_fixes_count + timeline_fixes_count
            self.log(f"\n=== KẾT QUẢ ===")
            self.log(f"Đã sửa {format_fixes_count} lỗi định dạng thời gian")
            self.log(f"Đã sửa {timeline_fixes_count} lỗi timeline")
            self.log(f"Tổng cộng: {total_fixes} lỗi được sửa")
            self.log(f"File đã sửa được lưu tại: {output_file}")

            return True, output_file, total_fixes

        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
            return False, None, 0
            
    def fix_srt_threaded(self):
        """Chạy fix SRT trong thread riêng"""
        def run_fix():
            file_path = self.file_path_var.get()
            
            if not file_path:
                messagebox.showerror("Lỗi", "Vui lòng chọn file SRT!")
                return
                
            if not os.path.exists(file_path):
                messagebox.showerror("Lỗi", "File không tồn tại!")
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
                messagebox.showinfo("Thành công", 
                                  f"Đã sửa {fixes_count} lỗi!\nFile đã lưu: {output_file}")
            else:
                messagebox.showerror("Lỗi", "Có lỗi xảy ra khi sửa file!")
        
        # Chạy trong thread riêng để không block UI
        thread = threading.Thread(target=run_fix)
        thread.daemon = True
        thread.start()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SRTFixer()
    app.run()