#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để tự động upload video lên YouTube
Sử dụng Google API
"""

import sys
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes cần thiết để upload video
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """Xác thực với Google API"""
    credentials = None
    
    # Token file lưu credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    
    # Nếu không có credentials hợp lệ, yêu cầu đăng nhập
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                print("ERROR: Không tìm thấy file client_secrets.json!")
                print("Vui lòng tải OAuth 2.0 credentials từ Google Cloud Console")
                print("Hướng dẫn: https://developers.google.com/youtube/v3/guides/uploading_a_video")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Lưu credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    
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
    
    # Tạo media upload
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    # Tạo request
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    print("Đang upload video lên YouTube...")
    print("(Quá trình này có thể mất vài phút)")
    print()
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"Upload: {progress}%", end='\r')
    
    print()
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
    
    # Kiểm tra file tồn tại
    if not os.path.exists(video_path):
        print(f"ERROR: File không tồn tại: {video_path}")
        sys.exit(1)
    
    # Tạo tiêu đề và mô tả
    title = f"{original_title} - AIVietSub"
    description = "Video được Vietsub bởi AI"
    
    print(f"Video: {video_path}")
    print(f"Tiêu đề: {title}")
    print(f"Mô tả: {description}")
    print(f"Privacy: {privacy}")
    print()
    
    # Xác thực
    print("Đang xác thực với Google API...")
    youtube = get_authenticated_service()
    
    if not youtube:
        sys.exit(1)
    
    print("✓ Xác thực thành công!")
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
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ LỖI: {str(e)}")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
