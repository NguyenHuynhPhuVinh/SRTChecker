#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để sửa lỗi định dạng file SRT (version động - nhận file path từ argument)
"""

import re
import os
import sys

class SRTFixer:
    def __init__(self):
        pass
            
    def log(self, message):
        """In message ra console"""
        print(message)
        
    def fix_time_format(self, time_str):
        """Sửa định dạng thời gian với validation kỹ hơn"""
        time_str = time_str.strip()
        original_time = time_str

        patterns = [
            (r'^(\d{1,2}):(\d{2}),(\d{3})$', lambda m: f'00:{m.group(1).zfill(2)}:{m.group(2)},{m.group(3)}'),
            (r'^(\d):(\d{2}):(\d{3})$', lambda m: f'00:0{m.group(1)}:{m.group(2)},{m.group(3)}'),
            (r'^(\d{2}):(\d{2}):(\d{3})$', lambda m: f'00:{m.group(1)}:{m.group(2)},{m.group(3)}'),
            (r'^(\d):(\d{2}),(\d{3})$', lambda m: f'00:0{m.group(1)}:{m.group(2)},{m.group(3)}'),
            (r'^(\d{2}):0(\d{1}),(\d{3})$', lambda m: f'{m.group(1)}:0{m.group(2)},{m.group(3)}'),
            (r'^(\d{2}):0(\d{1}):(\d{3})$', lambda m: f'{m.group(1)}:0{m.group(2)},{m.group(3)}'),
            (r'^(\d{2}):(\d{3}),(\d{3})$', lambda m: f'{m.group(1)}:0{m.group(2)[0]}:{m.group(2)[1:]},{m.group(3)}'),
            (r'^(\d{2}):(\d{3}):(\d{3})$', lambda m: f'{m.group(1)}:0{m.group(2)[0]}:{m.group(2)[1:]},{m.group(3)}'),
        ]

        for pattern, replacement in patterns:
            match = re.match(pattern, time_str)
            if match:
                if callable(replacement):
                    fixed_time = replacement(match)
                    if self.validate_time_format(fixed_time):
                        return fixed_time
                else:
                    fixed_time = re.sub(pattern, replacement, time_str)
                    if self.validate_time_format(fixed_time):
                        return fixed_time

        if self.validate_time_format(time_str):
            return time_str

        return original_time

    def validate_time_format(self, time_str):
        """Kiểm tra định dạng thời gian có đúng chuẩn SRT không"""
        pattern = r'^(\d{2}):(\d{2}):(\d{2}),(\d{3})$'
        match = re.match(pattern, time_str)
        if not match:
            return False

        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        milliseconds = int(match.group(4))

        return (0 <= hours <= 99 and
                0 <= minutes <= 59 and
                0 <= seconds <= 59 and
                0 <= milliseconds <= 999)

    def time_to_milliseconds(self, time_str):
        """Chuyển đổi thời gian sang milliseconds"""
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
        
    def fix_srt_file(self, input_file):
        """Sửa file SRT"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.log(f"Đã đọc file: {input_file}")

            lines = content.split('\n')
            fixed_lines = []
            format_fixes_count = 0
            timeline_issues_count = 0

            time_pattern = r'^(.+?)\s*-->\s*(.+?)$'
            subtitles = []

            for i, line in enumerate(lines):
                original_line = line
                line = line.strip()

                match = re.match(time_pattern, line)
                if match:
                    start_time = match.group(1).strip()
                    end_time = match.group(2).strip()

                    fixed_start = self.fix_time_format(start_time)
                    fixed_end = self.fix_time_format(end_time)

                    fixed_line = f"{fixed_start} --> {fixed_end}"

                    if fixed_line != line:
                        self.log(f"[FORMAT] Dòng {i+1}: {line}")
                        self.log(f"  -> {fixed_line}")
                        format_fixes_count += 1

                    subtitle_info = {
                        'line_number': i + 1,
                        'subtitle_number': len(subtitles) + 1,
                        'start_time': fixed_start,
                        'end_time': fixed_end,
                        'start_ms': self.time_to_milliseconds(fixed_start),
                        'end_ms': self.time_to_milliseconds(fixed_end)
                    }
                    subtitles.append(subtitle_info)

                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(original_line.rstrip())

            self.log(f"\n=== KIỂM TRA TIMELINE ===")

            for i, subtitle in enumerate(subtitles):
                if subtitle['start_ms'] is not None and subtitle['end_ms'] is not None:
                    if subtitle['start_ms'] >= subtitle['end_ms']:
                        self.log(f"[ERROR] Subtitle {subtitle['subtitle_number']}: Thời gian bắt đầu >= kết thúc")
                        self.log(f"  {subtitle['start_time']} --> {subtitle['end_time']}")
                        timeline_issues_count += 1

                if i < len(subtitles) - 1:
                    next_subtitle = subtitles[i + 1]
                    if (subtitle['end_ms'] is not None and
                        next_subtitle['start_ms'] is not None and
                        subtitle['end_ms'] > next_subtitle['start_ms']):

                        self.log(f"[ERROR] Subtitle {subtitle['subtitle_number']} và {next_subtitle['subtitle_number']}: Overlap")
                        timeline_issues_count += 1

            if timeline_issues_count == 0:
                self.log("✓ Timeline OK!")

            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_fixed.srt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))

            self.log(f"\n=== KẾT QUẢ ===")
            self.log(f"✓ Đã sửa {format_fixes_count} lỗi định dạng")
            
            if timeline_issues_count > 0:
                self.log(f"✗ Phát hiện {timeline_issues_count} lỗi timeline!")
                self.log(f"📁 File đã sửa: {output_file}")
                return False, output_file, format_fixes_count
            
            self.log(f"📁 File đã sửa: {output_file}")
            return True, output_file, format_fixes_count

        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
            return False, None, 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python fix_srt_dynamic.py <file.srt>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print("=" * 60)
    print("SRT Format Fixer")
    print("=" * 60)
    print(f"File: {file_path}")
    print()
    
    if not os.path.exists(file_path):
        print(f"ERROR: File không tồn tại: {file_path}")
        sys.exit(1)
    
    app = SRTFixer()
    success, output_file, fixes_count = app.fix_srt_file(file_path)
    
    print()
    print("=" * 60)
    if success:
        print(f"✓ PASS! File SRT hợp lệ")
        print(f"✓ Đã sửa {fixes_count} lỗi định dạng")
        sys.exit(0)
    else:
        print(f"✗ FAIL! File SRT có lỗi timeline")
        sys.exit(1)
