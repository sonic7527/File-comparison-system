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
    try:
        # 嘗試獲取雲端資料庫統計
        from core.turso_database import TursoDatabase
        turso_db = TursoDatabase()
        
        if turso_db.is_cloud_mode():
            # 雲端模式：顯示 Turso 資料庫統計
            return get_cloud_storage_stats(turso_db)
        else:
            # 本地模式：顯示本地存儲統計
            return get_local_storage_stats()
    except Exception as e:
        # 如果無法獲取雲端統計，回退到本地統計
        return get_local_storage_stats()

def get_cloud_storage_stats(turso_db):
    """
    獲取雲端資料庫的儲存統計
    """
    try:
        # 獲取比對範本統計
        comparison_templates = turso_db.get_comparison_templates()
        comparison_size = sum(template.get('file_size', 0) for template in comparison_templates)
        comparison_size_mb = round(comparison_size / (1024 * 1024), 2)
        
        # 獲取智能生成範本統計
        template_groups = turso_db.get_all_template_groups_cloud()
        template_files = []
        for group in template_groups:
            files = turso_db.get_template_files_cloud(group['id'])
            template_files.extend(files)
        
        generation_size = sum(file.get('file_size', 0) for file in template_files)
        generation_size_mb = round(generation_size / (1024 * 1024), 2)
        
        # 計算總容量
        total_size = comparison_size + generation_size
        total_size_mb = comparison_size_mb + generation_size_mb
        
        # 假設 Turso 免費版限制為 5GB
        turso_limit_gb = 5
        turso_limit_mb = turso_limit_gb * 1024
        usage_percentage = min(round(total_size_mb / turso_limit_mb * 100, 1), 100)
        
        # 根據使用量決定警告等級
        if usage_percentage > 80:
            warning_level = "danger"
            warning_message = "⚠️ 雲端容量警告：已使用超過80%，建議清理範本"
        elif usage_percentage > 60:
            warning_level = "warning"
            warning_message = "⚠️ 雲端容量提醒：已使用超過60%，請注意範本管理"
        elif usage_percentage > 40:
            warning_level = "info"
            warning_message = "ℹ️ 雲端容量正常：已使用40%+，建議定期清理"
        else:
            warning_level = "success"
            warning_message = "✅ 雲端容量良好：使用量在安全範圍內"
        
        return {
            'is_cloud': True,
            'total_size_mb': total_size_mb,
            'total_size_gb': round(total_size_mb / 1024, 2),
            'usage_percentage': usage_percentage,
            'warning_level': warning_level,
            'warning_message': warning_message,
            'formatted_size': format_file_size(total_size),
            'template_usage': {
                "智能生成範本": {
                    'size_mb': generation_size_mb,
                    'file_count': len(template_files)
                },
                "比對範本": {
                    'size_mb': comparison_size_mb,
                    'file_count': len(comparison_templates)
                }
            },
            'cloud_limit_gb': turso_limit_gb,
            'cloud_limit_mb': turso_limit_mb
        }
    except Exception as e:
        # 如果雲端統計失敗，回退到本地統計
        return get_local_storage_stats()

def get_local_storage_stats():
    """
    獲取本地存儲統計（回退方案）
    """
    usage_data = get_storage_usage()
    template_usage = get_template_storage_usage()
    warning_level, warning_message = get_storage_warning_level(usage_data)
    
    return {
        'is_cloud': False,
        'usage': usage_data,
        'template_usage': template_usage,
        'warning_level': warning_level,
        'warning_message': warning_message,
        'formatted_size': format_file_size(usage_data['total_size']),
        'usage_percentage': min(round(usage_data['total_size_mb'] / 1000 * 100, 1), 100)  # 假設1GB限制
    } 