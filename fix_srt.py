#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để sửa lỗi định dạng file SRT
Sửa các lỗi thời gian không đúng format chuẩn SRT
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
        """Sửa file SRT - chỉ sửa định dạng, báo cáo timeline"""
        try:
            # Đọc file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.log(f"Đã đọc file: {input_file}")

            lines = content.split('\n')
            fixed_lines = []
            format_fixes_count = 0
            timeline_issues_count = 0

            # Pattern cho dòng thời gian - hỗ trợ nhiều định dạng
            time_pattern = r'^(.+?)\s*-->\s*(.+?)$'

            # Lưu trữ thông tin subtitle để kiểm tra timeline
            subtitles = []

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

                    # Lưu thông tin subtitle để kiểm tra timeline
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
                    # Giữ nguyên dòng không phải thời gian
                    fixed_lines.append(original_line.rstrip())

            # Pass 2: Chỉ kiểm tra và báo cáo timeline (KHÔNG SỬA)
            self.log(f"\n=== KIỂM TRA TIMELINE (CHỈ BÁO CÁO) ===")

            for i, subtitle in enumerate(subtitles):
                # Kiểm tra start_time < end_time
                if subtitle['start_ms'] is not None and subtitle['end_ms'] is not None:
                    if subtitle['start_ms'] >= subtitle['end_ms']:
                        self.log(f"[TIMELINE ERROR] Subtitle {subtitle['subtitle_number']} (dòng {subtitle['line_number']}): Thời gian bắt đầu >= thời gian kết thúc")
                        self.log(f"  {subtitle['start_time']} --> {subtitle['end_time']}")
                        timeline_issues_count += 1

                # Kiểm tra overlap với subtitle tiếp theo
                if i < len(subtitles) - 1:
                    next_subtitle = subtitles[i + 1]
                    if (subtitle['end_ms'] is not None and
                        next_subtitle['start_ms'] is not None and
                        subtitle['end_ms'] > next_subtitle['start_ms']):

                        self.log(f"[TIMELINE ERROR] Subtitle {subtitle['subtitle_number']} và {next_subtitle['subtitle_number']}: Thời gian overlap")
                        self.log(f"  Subtitle {subtitle['subtitle_number']} kết thúc: {subtitle['end_time']}")
                        self.log(f"  Subtitle {next_subtitle['subtitle_number']} bắt đầu: {next_subtitle['start_time']}")
                        timeline_issues_count += 1

            # Pass 3: Kiểm tra khoảng lặng > 2.5 giây
            self.log(f"\n=== KIỂM TRA KHOẢNG LẶNG > 2.5 GIÂY ===")
            silence_gaps = []
            silence_threshold_ms = 2500  # 2.5 giây

            for i in range(len(subtitles) - 1):
                current_subtitle = subtitles[i]
                next_subtitle = subtitles[i + 1]

                if (current_subtitle['end_ms'] is not None and
                    next_subtitle['start_ms'] is not None):

                    gap_ms = next_subtitle['start_ms'] - current_subtitle['end_ms']

                    if gap_ms > silence_threshold_ms:
                        gap_seconds = gap_ms / 1000.0
                        silence_gaps.append({
                            'gap_seconds': gap_seconds,
                            'gap_ms': gap_ms,
                            'current_sub': current_subtitle['subtitle_number'],
                            'next_sub': next_subtitle['subtitle_number'],
                            'end_time': current_subtitle['end_time'],
                            'start_time': next_subtitle['start_time']
                        })

            # Sắp xếp từ cao xuống thấp
            silence_gaps.sort(key=lambda x: x['gap_seconds'], reverse=True)

            # Hiển thị kết quả đã sắp xếp
            silence_gaps_count = len(silence_gaps)
            if silence_gaps_count > 0:
                for gap in silence_gaps:
                    self.log(f"[SILENCE GAP] Khoảng lặng {gap['gap_seconds']:.1f}s giữa subtitle {gap['current_sub']} và {gap['next_sub']}")
                    self.log(f"  Từ {gap['end_time']} đến {gap['start_time']}")
            else:
                self.log("✓ Không phát hiện khoảng lặng > 2.5 giây")

            if timeline_issues_count == 0 and silence_gaps_count == 0:
                self.log("✓ Timeline hoàn toàn ổn!")

            # Tạo tên file output
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_fixed.srt"

            # Ghi file đã sửa
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))

            self.log(f"\n=== KẾT QUẢ ===")
            self.log(f"✓ Đã sửa {format_fixes_count} lỗi định dạng thời gian")
            self.log(f"⚠ Phát hiện {timeline_issues_count} vấn đề timeline (chỉ báo cáo)")
            self.log(f"� Phát hiện {silence_gaps_count} khoảng lặng > 2.5 giây")
            self.log(f"�📁 File đã sửa được lưu tại: {output_file}")

            return True, output_file, format_fixes_count

        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
            return False, None, 0

if __name__ == "__main__":
    # File path cố định
    file_path = r"C:\Users\tomis\Documents\SRTChecker\pricone.srt"
    
    print("=" * 60)
    print("SRT Format Fixer - Sửa lỗi định dạng file SRT")
    print("=" * 60)
    print(f"Đang kiểm tra file: {file_path}")
    print()
    
    # Kiểm tra file tồn tại
    if not os.path.exists(file_path):
        print(f"LỖI: File không tồn tại: {file_path}")
        sys.exit(1)
    
    # Tạo instance và chạy
    app = SRTFixer()
    success, output_file, fixes_count = app.fix_srt_file(file_path)
    
    print()
    print("=" * 60)
    if success:
        print(f"✓ HOÀN THÀNH! Đã sửa {fixes_count} lỗi định dạng")
        print(f"✓ File đã lưu: {output_file}")
    else:
        print("✗ CÓ LỖI XẢY RA!")
        sys.exit(1)
    print("=" * 60)