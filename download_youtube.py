#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để tải video YouTube với chất lượng cao nhất
Sử dụng yt-dlp
"""

import sys
import os

def download_youtube_video(url, output_path="."):
    """
    Tải video YouTube với chất lượng cao nhất
    
    Args:
        url: URL của video YouTube
        output_path: Thư mục lưu video (mặc định là thư mục hiện tại)
    """
    try:
        import yt_dlp
    except ImportError:
        print("ERROR: Chưa cài đặt yt-dlp!")
        print("Vui lòng chạy: pip install yt-dlp")
        sys.exit(1)
    
    # Cấu hình tải video
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
    }
    
    print("=" * 60)
    print("YouTube Video Downloader")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Thư mục lưu: {output_path}")
    print()
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Đang tải thông tin video...")
            info = ydl.extract_info(url, download=False)
            print(f"Tiêu đề: {info.get('title', 'N/A')}")
            print(f"Kênh: {info.get('uploader', 'N/A')}")
            print(f"Thời lượng: {info.get('duration', 0) // 60} phút")
            print()
            
            print("Đang tải video...")
            ydl.download([url])
            
            print()
            print("=" * 60)
            print("✓ TẢI THÀNH CÔNG!")
            print("=" * 60)
            return True
            
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ LỖI: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python download_youtube.py <URL>")
        print("Ví dụ: python download_youtube.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Thư mục lưu (có thể thay đổi)
    output_path = "."
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    
    success = download_youtube_video(url, output_path)
    sys.exit(0 if success else 1)
