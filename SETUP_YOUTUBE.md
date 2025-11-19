# Hướng dẫn cài đặt YouTube Upload

## Bước 1: Cài đặt thư viện

```cmd
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Bước 2: Tạo Google Cloud Project và OAuth credentials

1. Truy cập: https://console.cloud.google.com/
2. Tạo project mới hoặc chọn project có sẵn
3. Bật YouTube Data API v3:
   - Vào "APIs & Services" > "Library"
   - Tìm "YouTube Data API v3"
   - Click "Enable"

4. Tạo OAuth 2.0 credentials:
   - Vào "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Chọn "Desktop app"
   - Đặt tên (ví dụ: "YouTube Uploader")
   - Click "Create"

5. Tải credentials:
   - Click nút download (biểu tượng mũi tên xuống)
   - Đổi tên file thành `client_secrets.json`
   - Copy file vào thư mục gốc của project (cùng thư mục với main.py)

## Bước 3: Chạy lần đầu

Lần đầu chạy `process.bat`, script sẽ:
1. Mở browser để đăng nhập Google
2. Yêu cầu cấp quyền upload video
3. Lưu token vào file `token.pickle` (dùng cho lần sau)

## Lưu ý

- Video sẽ được upload ở chế độ **private** (riêng tư)
- Để đổi sang public, sửa trong file `main.py`: `private` → `public`
- File `token.pickle` và `client_secrets.json` KHÔNG nên push lên git
- Đã thêm vào `.gitignore`

## Cấu trúc video upload

- **Tiêu đề**: [Tên video gốc] - AIVietSub
- **Mô tả**: Video được Vietsub bởi AI
- **Privacy**: private (mặc định)
