import os
import shutil
from datetime import datetime

def get_storage_usage():
    """
    計算專案儲存空間使用量
    排除虛擬環境和暫存檔案
    """
    total_size = 0
    file_count = 0
    
    # 只計算實際專案檔案
    project_dirs = ["data", "uploads", "core", "views", "utils"]
    exclude_patterns = ["__pycache__", ".git", "venv", "node_modules"]
    
    for dir_name in project_dirs:
        if os.path.exists(dir_name):
            for root, dirs, files in os.walk(dir_name):
                # 排除不需要的目錄
                dirs[:] = [d for d in dirs if d not in exclude_patterns]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        file_count += 1
                    except (OSError, FileNotFoundError):
                        continue
    
    return {
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'file_count': file_count
    }

def get_template_storage_usage():
    """
    計算範本相關的儲存使用量
    """
    # 在雲端部署時使用臨時目錄
    if os.environ.get('STREAMLIT_SERVER_RUN_ON_HEADLESS', False):
        import tempfile
        comparison_dir = os.path.join(tempfile.gettempdir(), "comparison_templates")
        uploads_dir = os.path.join(tempfile.gettempdir(), "uploads/templates")
    else:
        comparison_dir = "data/comparison_templates"
        uploads_dir = "uploads/templates"
    
    template_dirs = {
        "智能生成範本": [uploads_dir],  # 只計算用戶上傳的智能生成範本
        "比對範本": [comparison_dir]  # 修復：使用正確的比對範本目錄
    }
    
    usage_by_type = {}
    
    for template_type, dirs in template_dirs.items():
        total_size = 0
        file_count = 0
        
        for dir_path in dirs:
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            total_size += file_size
                            file_count += 1
                        except (OSError, FileNotFoundError):
                            continue
        
        usage_by_type[template_type] = {
            'size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count
        }
    
    return usage_by_type

def get_storage_warning_level(usage_data):
    """
    根據使用量返回警告等級
    """
    total_mb = usage_data['total_size_mb']
    
    if total_mb > 800:  # 超過800MB
        return "danger", "⚠️ 容量警告：已使用超過800MB，建議清理範本"
    elif total_mb > 600:  # 超過600MB
        return "warning", "⚠️ 容量提醒：已使用超過600MB，請注意範本管理"
    elif total_mb > 400:  # 超過400MB
        return "info", "ℹ️ 容量正常：已使用400MB+，建議定期清理"
    else:
        return "success", "✅ 容量良好：使用量在安全範圍內"

def format_file_size(size_bytes):
    """
    格式化檔案大小顯示
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_storage_stats():
    """
    獲取完整的儲存統計資訊
    """
    usage_data = get_storage_usage()
    template_usage = get_template_storage_usage()
    warning_level, warning_message = get_storage_warning_level(usage_data)
    
    return {
        'usage': usage_data,
        'template_usage': template_usage,
        'warning_level': warning_level,
        'warning_message': warning_message,
        'formatted_size': format_file_size(usage_data['total_size']),
        'usage_percentage': min(round(usage_data['total_size_mb'] / 1000 * 100, 1), 100)  # 假設1GB限制
    } 