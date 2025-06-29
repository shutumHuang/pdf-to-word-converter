# PDF轉Word工具 - Render部署版

這是一個專門為Render雲端平台設計的PDF轉Word轉換工具。

## 功能特色

- 📄 支援PDF檔案轉換為Word文件
- 🎨 保留原始格式和圖片
- 📱 響應式設計，支援手機和電腦
- ⚡ 快速轉換，最大支援50MB檔案
- 🧹 自動清理舊檔案

## 部署到Render

### 1. 準備GitHub倉庫

1. 將此專案上傳到GitHub
2. 確保包含以下檔案：
   - `app.py` - 主應用程式
   - `requirements.txt` - Python依賴
   - `build.sh` - 建置腳本
   - `templates/pdf_to_word.html` - 網頁模板

### 2. 在Render建立新服務

1. 登入 [Render](https://render.com)
2. 點擊 "New +" → "Web Service"
3. 連接您的GitHub倉庫
4. 設定服務名稱（例如：pdf-to-word-converter）

### 3. 配置設定

- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn app:app`
- **Environment Variables**:
  - `SECRET_KEY`: 設定一個隨機字串（可選）
  - `UPLOAD_FOLDER`: `/tmp/uploads`（預設）
  - `CONVERTED_FOLDER`: `/tmp/converted`（預設）

### 4. 部署

點擊 "Create Web Service" 開始部署。部署完成後，您會獲得一個公開的URL。

## 本地測試

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行應用程式
python app.py
```

訪問 http://localhost:5000 即可使用。

## 技術架構

- **後端**: Flask + pdf2docx
- **前端**: HTML5 + CSS3 + JavaScript
- **部署**: Render + Gunicorn
- **檔案處理**: 臨時目錄儲存

## 注意事項

1. Render的免費方案有檔案大小限制
2. 檔案會在1小時後自動清理
3. 建議使用付費方案處理大型檔案

## 支援

如有問題，請檢查Render的日誌或聯繫開發者。 