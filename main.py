#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script chính để tải video YouTube và tạo cấu trúc thư mục tự động
"""

import sys
import os
import re

def sanitize_filename(filename):
    """Loại bỏ ký tự không hợp lệ trong tên file/folder"""
    # Loại bỏ ký tự đặc biệt
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Loại bỏ khoảng trắng thừa
    filename = re.sub(r'\s+', ' ', filename).strip()
    # Giới hạn độ dài
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def create_process_bat(folder_path, video_name, srt_name, script_dir, video_title):
    """Tạo file BAT để xử lý subtitle, ghép vào video và upload lên YouTube"""
    bat_content = f"""@echo off
chcp 65001 >nul
echo ============================================================
echo Video Subtitle Processing + YouTube Upload
echo ============================================================
echo.

REM Đường dẫn tới các script
set SCRIPT_DIR={script_dir}
set FIX_SRT_SCRIPT=%SCRIPT_DIR%\\fix_srt_dynamic.py
set ADD_SUB_SCRIPT=%SCRIPT_DIR%\\add_subtitle.py
set UPLOAD_SCRIPT=%SCRIPT_DIR%\\upload_youtube.py

REM File trong thư mục hiện tại
set VIDEO_FILE={video_name}
set SRT_FILE={srt_name}
set SRT_FIXED=video_fixed.srt
set OUTPUT_VIDEO=video_with_sub.mp4
set VIDEO_TITLE={video_title}

echo Bước 1: Kiểm tra và sửa file SRT...
echo.
python "%FIX_SRT_SCRIPT%" "%SRT_FILE%"

if errorlevel 1 (
    echo.
    echo [ERROR] File SRT có lỗi! Vui lòng kiểm tra lại.
    pause
    exit /b 1
)

echo.
echo Bước 2: Burn subtitle - TỐC ĐỘ NHANH NHẤT + CHẤT LƯỢNG CAO NHẤT...
echo.
python "%ADD_SUB_SCRIPT%" "%VIDEO_FILE%" "%SRT_FIXED%" "%OUTPUT_VIDEO%"

if errorlevel 1 (
    echo.
    echo [ERROR] Không thể ghép subtitle vào video!
    pause
    exit /b 1
)

echo.
echo Bước 3: Đổi tên video...
echo.
set FINAL_VIDEO=%VIDEO_TITLE% - AIVietSub.mp4
ren "%OUTPUT_VIDEO%" "%FINAL_VIDEO%"

if errorlevel 1 (
    echo [WARNING] Không thể đổi tên video
    set FINAL_VIDEO=%OUTPUT_VIDEO%
) else (
    echo Đã đổi tên: %FINAL_VIDEO%
)

echo.
echo Bước 4: Upload video lên VLC Mobile...
echo.
python "%SCRIPT_DIR%\\upload_vlc.py" "%FINAL_VIDEO%" "http://192.168.137.92:8080"

if errorlevel 1 (
    echo.
    echo [ERROR] Không thể upload video lên VLC!
    pause
    exit /b 1
)

echo.
echo Bước 5: Đổi tên thư mục thành COMPLETE...
echo.

REM Lấy tên thư mục hiện tại
for %%I in (.) do set CURRENT_FOLDER=%%~nxI

REM Tạo tên thư mục mới với prefix COMPLETE
set NEW_FOLDER=COMPLETE_%CURRENT_FOLDER%

REM Di chuyển lên thư mục cha và đổi tên
cd ..
ren "%CURRENT_FOLDER%" "%NEW_FOLDER%"

if errorlevel 1 (
    echo [WARNING] Không thể đổi tên thư mục
) else (
    echo Đã đổi tên thư mục thành: %NEW_FOLDER%
)

echo.
echo ============================================================
echo HOÀN THÀNH! Video đã được upload lên YouTube
echo ============================================================
pause
"""
    
    bat_path = os.path.join(folder_path, "process.bat")
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    return bat_path

def main():
    """Hàm chính"""
    try:
        import yt_dlp
    except ImportError:
        print("ERROR: Chưa cài đặt yt-dlp!")
        print("Vui lòng chạy: pip install yt-dlp")
        sys.exit(1)
    
    print("=" * 60)
    print("YouTube Video Downloader & Subtitle Processor")
    print("=" * 60)
    print()
    
    # Nhập URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Nhập URL YouTube: ").strip()
    
    if not url:
        print("ERROR: URL không được để trống!")
        sys.exit(1)
    
    # Lấy thông tin video
    print()
    print("Đang lấy thông tin video...")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            video_id = info.get('id', 'unknown')
            
    except Exception as e:
        print(f"ERROR: Không thể lấy thông tin video: {str(e)}")
        sys.exit(1)
    
    print(f"Tiêu đề: {video_title}")
    print(f"ID: {video_id}")
    print()
    
    # Tạo tên thư mục
    folder_name = sanitize_filename(video_title)
    
    # Tạo đường dẫn thư mục video
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_base_dir = os.path.join(script_dir, "video")
    video_folder = os.path.join(video_base_dir, folder_name)
    
    # Tạo thư mục
    os.makedirs(video_folder, exist_ok=True)
    print(f"Đã tạo thư mục: {video_folder}")
    print()
    
    # Tải video
    video_path = os.path.join(video_folder, "video.mp4")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': video_path,
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
    }
    
    print("Đang tải video...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"ERROR: Không thể tải video: {str(e)}")
        sys.exit(1)
    
    print(f"✓ Đã tải video: {video_path}")
    print()
    
    # Tạo file SRT rỗng
    srt_path = os.path.join(video_folder, "video.srt")
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write("1\n00:00:00,000 --> 00:00:05,000\nThêm subtitle của bạn vào đây\n\n")
    
    print(f"✓ Đã tạo file SRT: {srt_path}")
    print()
    
    # Tạo file BAT
    bat_path = create_process_bat(video_folder, "video.mp4", "video.srt", script_dir, video_title)
    print(f"✓ Đã tạo file xử lý: {bat_path}")
    print()
    
    # Tạo file README
    readme_path = os.path.join(video_folder, "README.txt")
    readme_content = f"""Video: {video_title}
URL: {url}

Hướng dẫn:
1. Chỉnh sửa file video.srt để thêm subtitle
2. Chạy file process.bat để kiểm tra SRT và ghép vào video
3. Video có subtitle sẽ được tạo với tên: video_with_sub.mp4
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✓ Đã tạo file README: {readme_path}")
    print()
    
    print("=" * 60)
    print("✓ HOÀN THÀNH!")
    print("=" * 60)
    print(f"Thư mục: {video_folder}")
    print()
    print("Các bước tiếp theo:")
    print("1. Mở thư mục và chỉnh sửa file video.srt")
    print("2. Chạy process.bat để xử lý và ghép subtitle")
    print("=" * 60)

if __name__ == "__main__":
    main()
