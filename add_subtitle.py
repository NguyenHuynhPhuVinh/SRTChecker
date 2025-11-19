#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để tự động ghép file SRT vào video
Sử dụng ffmpeg với CPU encoding (ultrafast)
"""

import sys
import os
import subprocess

def check_ffmpeg():
    """Kiểm tra ffmpeg đã được cài đặt chưa"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def add_subtitle_to_video(video_path, srt_path, output_path=None):
    """
    Ghép file SRT vào video (BURN - CPU ultrafast)
    
    Args:
        video_path: Đường dẫn file video
        srt_path: Đường dẫn file SRT
        output_path: Đường dẫn file output (mặc định: video_with_sub.mp4)
    """
    
    print("=" * 60)
    print("Video Subtitle Merger - TỐC ĐỘ NHANH NHẤT + CHẤT LƯỢNG CAO NHẤT")
    print("=" * 60)
    
    # Kiểm tra ffmpeg
    if not check_ffmpeg():
        print("ERROR: Chưa cài đặt ffmpeg!")
        print("Tải tại: https://ffmpeg.org/download.html")
        return False
    
    # Kiểm tra file tồn tại
    if not os.path.exists(video_path):
        print(f"ERROR: File video không tồn tại: {video_path}")
        return False
    
    if not os.path.exists(srt_path):
        print(f"ERROR: File SRT không tồn tại: {srt_path}")
        return False
    
    # Tạo tên file output
    if output_path is None:
        base_name = os.path.splitext(video_path)[0]
        output_path = f"{base_name}_with_sub.mp4"
    
    print(f"Video: {video_path}")
    print(f"Subtitle: {srt_path}")
    print(f"Output: {output_path}")
    print()
    
    # CPU encoding - TỐC ĐỘ NHANH NHẤT + CHẤT LƯỢNG CAO NHẤT
    print("✓ Sử dụng CPU encoding - TỐC ĐỘ NHANH NHẤT + CHẤT LƯỢNG CAO NHẤT")
    
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"subtitles='{srt_path}'",
        '-c:v', 'libx264',
        '-preset', 'ultrafast',  # Nhanh nhất
        '-crf', '18',  # Chất lượng cao nhất (0-51, thấp = tốt hơn)
        '-qp', '0',  # Quantization parameter = 0 (lossless)
        '-c:a', 'copy',
        '-y',
        output_path
    ]
    
    print()
    print("Đang burn subtitle vào video...")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        
        print()
        print("=" * 60)
        print("✓ BURN SUBTITLE THÀNH CÔNG!")
        print(f"✓ File đã lưu: {output_path}")
        print("=" * 60)
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print(f"✗ LỖI: Không thể ghép subtitle")
        print(f"Chi tiết: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Cách dùng: python add_subtitle.py <video_file> <srt_file> [output_file]")
        print()
        print("Ví dụ:")
        print("  python add_subtitle.py video.mp4 subtitle.srt")
        print("  python add_subtitle.py video.mp4 subtitle.srt output.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    srt_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) >= 4 else None
    
    success = add_subtitle_to_video(video_path, srt_path, output_path)
    sys.exit(0 if success else 1)
