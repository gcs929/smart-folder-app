import os
import platform

# --- 文件名常量 ---
APP_NAME = "智能文件夹与客户信息管理 (PyQt6)"
APP_VERSION = "0.1.0"

# 使用新的配置文件名，避免与Tkinter版本冲突
CONFIG_DIR = "config_data"
CONFIG_FILE = os.path.join(CONFIG_DIR, "folder_creator_config_qt.json")
NOTES_FILE = os.path.join(CONFIG_DIR, "folder_notes_qt.json")
MASTER_CUSTOMER_DATA_FILE = os.path.join(CONFIG_DIR, "master_customer_data_qt.json")

TEMP_TRASH_PARENT_DIR_NAME = ".folder_creator_app_data_qt" # 新的临时目录名
TEMP_TRASH_PARENT_DIR = os.path.join(os.path.expanduser("~"), TEMP_TRASH_PARENT_DIR_NAME)
TEMP_TRASH_DIR = os.path.join(TEMP_TRASH_PARENT_DIR, "trash_bin")
NOTES_IMAGES_BASE_DIR = os.path.join(TEMP_TRASH_PARENT_DIR, "notes_images_storage")


# --- 字段标签和映射 (与原Tkinter版一致或根据需要调整) ---
FIELD_LABELS = {
    "日期": "date", "公司名称": "company_name", "税号": "tax_id", # ... 其他字段
}
JSON_TO_INTERNAL_FIELD_MAP = {
    "公司名称": "company_name", "纳税人识别号": "tax_id", # ... 其他字段
}
INSTRUCTION_TEXT = """请你从以下开票信息中提取指定字段...""" # ... (完整指令)

SYSTEM_FOLDER_NAMES = {
    '$recycle.bin', 'system volume information', # ... 其他系统文件夹
}

# --- Excel 导出映射 (与原Tkinter版一致) ---
EXCEL_MAPPINGS = {
    "报价模板": {"company_name": "A6", "tax_id": "B7", # ...
                },
    # ... 其他模板
}

# --- 剪贴板相关 ---
WINDOWS_CLIPBOARD_ENABLED = False
if platform.system() == "Windows":
    try:
        import win32clipboard # pywin32
        import win32con
        from io import BytesIO
        import struct
        WINDOWS_CLIPBOARD_ENABLED = True
        print("Windows系统剪贴板模块 (pywin32) 加载成功。")
    except ImportError:
        print("警告: pywin32 未安装。Windows系统剪贴板文件操作将不可用。")
else:
    print("非Windows平台，系统剪贴板文件操作将使用文本路径（如果实现）。")
SYSTEM_FOLDER_NAMES = {
    '$recycle.bin', 'system volume information', 'config.msi',
    'recovery', '$windows.~bt', '$windows.~ws', 'windowsapps',
    'onedrivetemp',
    '.ds_store',  # macOS
    'thumbs.db',  # Windows
    '.localized', # macOS
    # 确保这个集合被正确定义
}
# 创建必要的应用数据目录
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(TEMP_TRASH_PARENT_DIR, exist_ok=True)
os.makedirs(TEMP_TRASH_DIR, exist_ok=True)
os.makedirs(NOTES_IMAGES_BASE_DIR, exist_ok=True)