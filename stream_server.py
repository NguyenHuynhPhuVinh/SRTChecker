#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP Server để stream video từ PC sang mobile
Không cần upload, chỉ cần mở link là xem ngay
"""

import os
import sys
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote

class VideoStreamHandler(SimpleHTTPRequestHandler):
    """Custom handler để stream video"""
    
    def __init__(self, *args, video_dir=None, **kwargs):
        self.video_dir = video_dir
        super().__init__(*args, directory=video_dir, **kwargs)
    
    def end_headers(self):
        # Thêm headers để hỗ trợ streaming
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def do_GET(self):
        """Xử lý GET request"""
        if self.path == '/':
            # Hiển thị danh sách video
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Video Stream Server</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 20px auto;
                        padding: 20px;
                        background: #f5f5f5;
                    }
                    h1 {
                        color: #333;
                        text-align: center;
                    }
                    .video-list {
                        background: white;
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .video-item {
                        padding: 15px;
                        margin: 10px 0;
                        background: #f9f9f9;
                        border-radius: 4px;
                        border-left: 4px solid #4CAF50;
                    }
                    .video-item a {
                        color: #2196F3;
                        text-decoration: none;
                        font-size: 16px;
                        word-break: break-all;
                    }
                    .video-item a:hover {
                        text-decoration: underline;
                    }
                    .info {
                        background: #e3f2fd;
                        padding: 15px;
                        border-radius: 4px;
                        margin-bottom: 20px;
                        border-left: 4px solid #2196F3;
                    }
                </style>
            </head>
            <body>
                <h1>📺 Video Stream Server</h1>
                <div class="info">
                    <strong>Hướng dẫn:</strong> Click vào video để xem ngay trên điện thoại
                </div>
                <div class="video-list">
            """
            
            # Liệt kê các thư mục video
            video_items = []
            
            # Duyệt qua các thư mục
            for folder in os.listdir(self.video_dir):
                folder_path = os.path.join(self.video_dir, folder)
                if os.path.isdir(folder_path):
                    # Tìm file video trong thư mục
                    for file in os.listdir(folder_path):
                        if file.endswith(('.mp4', '.mkv', '.avi', '.webm')):
                            # Lưu: (tên thư mục, đường dẫn file)
                            video_path = f"{folder}/{file}"
                            video_items.append((folder, video_path))
                            break  # Chỉ lấy 1 video đầu tiên trong thư mục
            
            if video_items:
                for folder_name, video_path in sorted(video_items):
                    # Hiển thị tên thư mục, link tới file video
                    display_name = folder_name.replace('COMPLETE_', '')  # Bỏ prefix COMPLETE
                    html += f'<div class="video-item"><a href="/{video_path}">🎬 {display_name}</a></div>'
            else:
                html += '<p>Không có video nào</p>'
            
            html += """
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
        else:
            # Stream video file
            super().do_GET()

def get_local_ip():
    """Lấy địa chỉ IP local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def start_server(video_dir, port=8000):
    """Khởi động HTTP server"""
    
    # Kiểm tra thư mục tồn tại
    if not os.path.exists(video_dir):
        print(f"ERROR: Thư mục không tồn tại: {video_dir}")
        return
    
    # Lấy IP
    local_ip = get_local_ip()
    
    # Tạo handler với video directory
    handler = lambda *args, **kwargs: VideoStreamHandler(*args, video_dir=video_dir, **kwargs)
    
    # Khởi động server
    server = HTTPServer(('0.0.0.0', port), handler)
    
    print("=" * 60)
    print("📺 Video Stream Server")
    print("=" * 60)
    print(f"Thư mục: {video_dir}")
    print(f"Port: {port}")
    print()
    print("Mở trên điện thoại:")
    print(f"  http://{local_ip}:{port}")
    print()
    print("Hoặc mở trên máy tính:")
    print(f"  http://localhost:{port}")
    print()
    print("=" * 60)
    print("Server đang chạy... (Ctrl+C để dừng)")
    print("=" * 60)
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nĐang dừng server...")
        server.shutdown()
        print("✓ Đã dừng server")

def main():
    if len(sys.argv) < 2:
        print("Cách dùng: python stream_server.py <video_directory> [port]")
        print()
        print("Ví dụ:")
        print("  python stream_server.py .")
        print("  python stream_server.py video/")
        print("  python stream_server.py . 8080")
        sys.exit(1)
    
    video_dir = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) >= 3 else 8000
    
    start_server(video_dir, port)

if __name__ == "__main__":
    main()
