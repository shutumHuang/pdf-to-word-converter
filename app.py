from flask import Flask, render_template, request, send_file, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
from pdf2docx import Converter
import uuid
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# 設定上傳檔案配置 - 使用臨時目錄
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
CONVERTED_FOLDER = os.environ.get('CONVERTED_FOLDER', '/tmp/converted')
ALLOWED_EXTENSIONS = {'pdf'}

# 確保目錄存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB 限制

def allowed_file(filename):
    """檢查檔案副檔名是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_filename(filename):
    """清理檔名，移除不合法字元"""
    # 移除或替換不合法字元
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 移除多餘的空格
    filename = ' '.join(filename.split())
    
    return filename

@app.route('/')
def index():
    """首頁"""
    return render_template('pdf_to_word.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """處理檔案上傳和轉換"""
    try:
        # 檢查是否有檔案
        if 'file' not in request.files:
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        file = request.files['file']
        
        # 檢查檔案名稱
        if file.filename == '':
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        # 檢查檔案類型
        if not allowed_file(file.filename):
            return jsonify({'error': '只允許上傳PDF檔案'}), 400
        
        # 生成唯一檔名
        original_filename = secure_filename(file.filename)
        clean_original_name = clean_filename(original_filename)
        file_id = str(uuid.uuid4())
        
        # 儲存上傳的PDF檔案
        pdf_filename = f"{file_id}_{clean_original_name}"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        file.save(pdf_path)
        
        # 準備Word檔案路徑
        word_filename = f"{file_id}_{clean_original_name.rsplit('.', 1)[0]}.docx"
        word_path = os.path.join(app.config['CONVERTED_FOLDER'], word_filename)
        
        # 轉換PDF到Word
        print(f"開始轉換: {pdf_path} -> {word_path}")
        
        # 使用pdf2docx進行轉換
        cv = Converter(pdf_path)
        cv.convert(word_path, start=0, end=None)
        cv.close()
        
        # 檢查轉換結果
        if os.path.exists(word_path) and os.path.getsize(word_path) > 0:
            # 清理PDF檔案
            os.remove(pdf_path)
            
            return jsonify({
                'success': True,
                'message': '檔案轉換成功！',
                'filename': word_filename,
                'original_name': clean_original_name,
                'download_url': f'/download/{word_filename}'
            })
        else:
            # 轉換失敗，清理檔案
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            if os.path.exists(word_path):
                os.remove(word_path)
            
            return jsonify({'error': '檔案轉換失敗，請檢查PDF檔案是否損壞'}), 500
            
    except Exception as e:
        print(f"轉換錯誤: {str(e)}")
        return jsonify({'error': f'轉換過程中發生錯誤: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """下載轉換後的Word檔案"""
    try:
        file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
        
        if os.path.exists(file_path):
            # 設定下載檔名
            original_name = filename.split('_', 1)[1] if '_' in filename else filename
            download_name = original_name.replace('.pdf', '.docx')
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        else:
            return jsonify({'error': '檔案不存在'}), 404
            
    except Exception as e:
        return jsonify({'error': f'下載錯誤: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """清理舊檔案"""
    try:
        current_time = time.time()
        max_age = 3600  # 1小時
        
        # 清理uploads目錄
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                if current_time - os.path.getmtime(file_path) > max_age:
                    os.remove(file_path)
        
        # 清理converted目錄
        for filename in os.listdir(app.config['CONVERTED_FOLDER']):
            file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
            if os.path.isfile(file_path):
                if current_time - os.path.getmtime(file_path) > max_age:
                    os.remove(file_path)
        
        return jsonify({'message': '清理完成'})
        
    except Exception as e:
        return jsonify({'error': f'清理錯誤: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """處理檔案過大的錯誤"""
    return jsonify({'error': '檔案大小超過限制（最大50MB）'}), 413

@app.route('/health')
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 