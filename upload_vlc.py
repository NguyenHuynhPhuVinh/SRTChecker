#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để tự động upload video lên VLC mobile qua WiFi
"""

import sys
import os
import requests
from datetime import datetime

def log(message):
    """In log với timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def upload_to_vlc(video_path, vlc_url):
    """
    Upload video lên VLC mobile
    
    Args:
        video_path: Đường dẫn file video
        vlc_url: URL của VLC (ví dụ: http://192.168.1.100:8080)
    """
    
    print("=" * 60)
    print("VLC Mobile Uploader")
    print("=" * 60)
    print()
    
    log("Bắt đầu upload video lên VLC...")
    
    # Kiểm tra file tồn tại
    if not os.path.exists(video_path):
        log(f"ERROR: File không tồn tại: {video_path}")
        return False
    
    # Lấy thông tin file
    file_size = os.path.getsize(video_path)
    file_size_mb = file_size / (1024 * 1024)
    file_name = os.path.basename(video_path)
    
    log(f"File: {file_name}")
    log(f"Kích thước: {file_size_mb:.2f} MB")
    log(f"VLC URL: {vlc_url}")
    print()
    
    # VLC có nhiều endpoint khác nhau, thử cả 3
    upload_endpoints = [
        f"{vlc_url}/upload.json",
        f"{vlc_url}/upload",
        vlc_url
    ]
    
    try:
        # Mở file và upload
        with open(video_path, 'rb') as f:
            files = {'file': (file_name, f, 'video/mp4')}
            
            log("Đang upload...")
            print()
            
            # Thử từng endpoint
            success = False
            for upload_url in upload_endpoints:
                try:
                    log(f"Thử endpoint: {upload_url}")
                    response = requests.post(
                        upload_url,
                        files=files,
                        timeout=300  # 5 phút timeout
                    )
                    
                    if response.status_code == 200 or response.status_code == 201:
                        print()
                        log("✓ Upload thành công!")
                        log("Video đã có sẵn trong VLC trên điện thoại")
                        success = True
                        break
                    else:
                        log(f"  Status code: {response.status_code}, thử endpoint khác...")
                        # Reset file pointer
                        f.seek(0)
                except Exception as e:
                    log(f"  Lỗi: {str(e)}, thử endpoint khác...")
                    f.seek(0)
                    continue
            
            if not success:
                print()
                log("✗ Upload thất bại với tất cả endpoint!")
                log("Vui lòng upload thủ công qua browser:")
                log(f"  1. Mở {vlc_url} trên browser")
                log(f"  2. Kéo thả file: {file_name}")
                return False
            
            return True
                
    except requests.exceptions.ConnectionError:
        print()
        log("✗ Không thể kết nối tới VLC!")
        log("Kiểm tra:")
        log("  1. VLC đã bật 'Sharing via WiFi' chưa?")
        log("  2. Máy tính và điện thoại cùng mạng WiFi?")
        log("  3. URL có đúng không?")
        return False
        
    except Exception as e:
        print()
        log(f"✗ Lỗi: {str(e)}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Cách dùng: python upload_vlc.py <video_file> <vlc_url>")
        print()
        print("Ví dụ:")
        print("  python upload_vlc.py video_with_sub.mp4 http://192.168.1.100:8080")
        print()
        print("Lưu ý:")
        print("  - Bật 'Sharing via WiFi' trong VLC trên điện thoại")
        print("  - Lấy URL hiển thị trên màn hình VLC")
        sys.exit(1)
    
    video_path = sys.argv[1]
    vlc_url = sys.argv[2].rstrip('/')
    
    success = upload_to_vlc(video_path, vlc_url)
    
    print()
    print("=" * 60)
    if success:
        print("✓ HOÀN THÀNH!")
    else:
        print("✗ THẤT BẠI!")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
