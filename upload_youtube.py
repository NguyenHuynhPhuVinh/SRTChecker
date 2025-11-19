#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để tự động upload video lên YouTube
Sử dụng Google API
"""

import sys
import os
import pickle
import time
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes cần thiết để upload video
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def log(message):
    """In log với timestamp ra cmd"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_authenticated_service():
    """Xác thực với Google API"""
    log("Bắt đầu xác thực với Google API...")
    credentials = None
    
    # Tìm thư mục gốc của script (nơi có client_secrets.json)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, 'token.pickle')
    client_secrets_path = os.path.join(script_dir, 'client_secrets.json')
    
    # Token file lưu credentials
    if os.path.exists(token_path):
        log("Tìm thấy token đã lưu, đang tải...")
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)
    
    # Nếu không có credentials hợp lệ, yêu cầu đăng nhập
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            log("Token hết hạn, đang refresh...")
            credentials.refresh(Request())
        else:
            if not os.path.exists(client_secrets_path):
                log("ERROR: Không tìm thấy file client_secrets.json!")
                print(f"Vui lòng đặt file vào: {script_dir}")
                print("Hướng dẫn: https://developers.google.com/youtube/v3/guides/uploading_a_video")
                print()
                print("Hoặc xem file SETUP_YOUTUBE.md để biết chi tiết")
                return None
            
            log("Đang mở browser để đăng nhập Google...")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, SCOPES)
            credentials = flow.run_local_server(port=0)
            log("Đăng nhập thành công!")
        
        # Lưu credentials
        log("Đang lưu token...")
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)
    
    log("Xác thực thành công!")
    return build('youtube', 'v3', credentials=credentials)

def upload_video(youtube, video_path, title, description, category='22', privacy='private'):
    """
    Upload video lên YouTube
    
    Args:
        youtube: YouTube API service
        video_path: Đường dẫn file video
        title: Tiêu đề video
        description: Mô tả video
        category: Category ID (22 = People & Blogs)
        privacy: 'public', 'private', hoặc 'unlisted'
    """
    
    log(f"Chuẩn bị upload video: {os.path.basename(video_path)}")
    log(f"Tiêu đề: {title}")
    log(f"Privacy: {privacy}")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Lấy kích thước file
    file_size = os.path.getsize(video_path)
    file_size_mb = file_size / (1024 * 1024)
    
    log(f"Kích thước file: {file_size_mb:.2f} MB")
    print()
    
    # Tạo media upload với chunk size 10MB
    chunk_size = 10 * 1024 * 1024  # 10 MB chunks
    media = MediaFileUpload(video_path, chunksize=chunk_size, resumable=True)
    
    log("Tạo upload request...")
    
    # Tạo request
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    log("Bắt đầu upload video lên YouTube...")
    print()
    
    response = None
    uploaded_mb = 0
    start_time = time.time()
    
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            uploaded_mb = (status.resumable_progress / (1024 * 1024))
            
            # Tính tốc độ upload
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                speed_mbps = uploaded_mb / elapsed_time
            else:
                speed_mbps = 0
            
            # Tính thời gian còn lại
            if speed_mbps > 0:
                remaining_mb = file_size_mb - uploaded_mb
                eta_seconds = remaining_mb / speed_mbps
                eta_minutes = int(eta_seconds / 60)
                eta_seconds = int(eta_seconds % 60)
                eta_str = f"{eta_minutes}:{eta_seconds:02d}"
            else:
                eta_str = "--:--"
            
            # Tạo progress bar
            bar_length = 40
            filled_length = int(bar_length * status.progress())
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Hiển thị realtime
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\r[{timestamp}] [{bar}] {progress}% | {uploaded_mb:.1f}/{file_size_mb:.1f} MB | {speed_mbps:.2f} MB/s | ETA: {eta_str}", end='', flush=True)
    
    print()
    print()
    
    elapsed_time = time.time() - start_time
    log(f"Upload hoàn tất trong {elapsed_time:.1f} giây")
    log(f"Tốc độ trung bình: {file_size_mb/elapsed_time:.2f} MB/s")
    
    return response

def main():
    if len(sys.argv) < 3:
        print("Cách dùng: python upload_youtube.py <video_file> <original_title> [privacy]")
        print()
        print("Privacy: public, private (mặc định), unlisted")
        print()
        print("Ví dụ:")
        print("  python upload_youtube.py video_with_sub.mp4 \"Tên video gốc\"")
        print("  python upload_youtube.py video_with_sub.mp4 \"Tên video gốc\" public")
        sys.exit(1)
    
    video_path = sys.argv[1]
    original_title = sys.argv[2]
    privacy = sys.argv[3] if len(sys.argv) >= 4 else 'private'
    
    print("=" * 60)
    print("YouTube Video Uploader")
    print("=" * 60)
    print()
    
    log("=" * 60)
    log("BẮT ĐẦU QUÁ TRÌNH UPLOAD")
    log("=" * 60)
    
    # Kiểm tra file tồn tại
    log(f"Kiểm tra file: {video_path}")
    if not os.path.exists(video_path):
        log(f"ERROR: File không tồn tại: {video_path}")
        print(f"ERROR: File không tồn tại: {video_path}")
        sys.exit(1)
    
    log("File tồn tại, tiếp tục...")
    
    # Tạo tiêu đề và mô tả
    title = f"{original_title} - AIVietSub"
    description = "Video được Vietsub bởi AI"
    
    print(f"Video: {video_path}")
    print(f"Tiêu đề: {title}")
    print(f"Mô tả: {description}")
    print(f"Privacy: {privacy}")
    print()
    
    # Xác thực
    youtube = get_authenticated_service()
    
    if not youtube:
        log("ERROR: Xác thực thất bại")
        sys.exit(1)
    
    print()
    
    try:
        # Upload video
        response = upload_video(youtube, video_path, title, description, privacy=privacy)
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print()
        print("=" * 60)
        print("✓ UPLOAD THÀNH CÔNG!")
        print(f"✓ Video ID: {video_id}")
        print(f"✓ URL: {video_url}")
        print("=" * 60)
        
        log("=" * 60)
        log("UPLOAD THÀNH CÔNG!")
        log(f"Video ID: {video_id}")
        log(f"URL: {video_url}")
        log("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ LỖI: {str(e)}")
        print("=" * 60)
        
        log("=" * 60)
        log(f"ERROR: {str(e)}")
        log("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
