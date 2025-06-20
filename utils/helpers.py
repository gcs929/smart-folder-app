# D:\newpro\smart_folder_app\utils\helpers.py
import os
import platform
import re  # <--- 确保导入 re 模块
import subprocess
import string
from utils.constants import SYSTEM_FOLDER_NAMES  # 假设这个已正确设置
import stat


# ... (你已有的 get_available_drives, open_path_externally, _is_normal_directory 函数) ...
def get_available_drives():
    """
    获取系统中可用的驱动器列表。
    对于Windows，返回 "C:\", "D:\", 等。
    对于Linux/macOS，返回用户主目录、根目录，以及macOS下的/Volumes。
    """
    drives = []
    if platform.system() == "Windows":
        # string.ascii_uppercase 是 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        drives.extend([d + "\\" for d in available_drives])  # 保持与原Tkinter版输出一致
    elif platform.system() == "Linux" or platform.system() == "Darwin":  # macOS
        drives.append(os.path.expanduser("~"))  # 用户主目录
        drives.append("/")  # 根目录
        if platform.system() == "Darwin":  # macOS 特有的 /Volumes
            try:
                # 列出 /Volumes 下的目录
                volumes_output = subprocess.check_output(["ls", "/Volumes"], text=True, stderr=subprocess.DEVNULL)
                for vol_name in volumes_output.splitlines():
                    if vol_name and vol_name != "Macintosh HD":  # 排除主卷的常见别名，避免重复
                        vol_path = os.path.join("/Volumes", vol_name)
                        if os.path.isdir(vol_path):
                            drives.append(vol_path)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"获取 /Volumes 列表时出错: {e}")  # 打印错误但继续

    # 去重并按字母顺序排序
    unique_drives = sorted(list(set(drives)))
    return unique_drives
def sanitize_filename(name):
    """
    Cleans a string to be suitable for use as a filename.
    Removes or replaces illegal characters and limits length.
    """
    if not isinstance(name, str):
        return ""  # Or raise an error, or return a default

    # 替换或移除 Windows 和 Unix/Linux 中的非法字符
    # Windows: < > : " / \ | ? *
    # Unix/Linux: / (NUL character is also problematic but harder to type)
    name = re.sub(r'[\\/*?:"<>|]', "_", name)  # 将这些字符替换为下划线
    name = name.replace("\0", "")  # 移除空字符

    # 替换空格 (可选，但通常推荐)
    name = name.replace(" ", "_")

    # 避免以点或空格开头或结尾 (某些系统可能不允许)
    name = name.strip("._ ")

    # 限制文件名长度 (一个合理的值，考虑到完整路径长度限制)
    # 操作系统对文件名和路径有长度限制，例如Windows通常是260个字符总路径
    # 这里只限制文件名本身
    max_len = 100  # 或者根据你的需求调整
    if len(name) > max_len:
        # 可以选择截断或者更智能地处理
        # 如果文件名有扩展名，最好保留扩展名
        base, ext = os.path.splitext(name)
        available_len_for_base = max_len - len(ext)
        if available_len_for_base > 0:
            name = base[:available_len_for_base] + ext
        else:  # 扩展名本身就超长了，罕见，直接截断
            name = name[:max_len]

    # 确保文件名不是空的，或者不是只有点
    if not name or name == "." or name == "..":
        return "sanitized_empty_name"  # 或其他默认名

    return name
def _is_normal_directory(path): # <--- 检查函数名是否完全匹配
    """
    检查是否为普通、非系统、非隐藏文件夹。
    """
    try:
        # 确保路径存在并且确实是一个目录
        if not os.path.exists(path) or not os.path.isdir(path):
            return False # 如果路径不存在或不是目录，则不是普通目录

        base_name = os.path.basename(path).lower()
        if base_name in SYSTEM_FOLDER_NAMES:
            return False

        if platform.system() == "Windows":
            attrs = os.stat(path).st_file_attributes
            if attrs & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM):
                return False
        elif os.path.basename(path).startswith('.'): # 非Windows系统检查点开头
            return False
        return True
    except (OSError, AttributeError) as e:
        # print(f"Warning: Error checking directory attributes for '{path}': {e}")
        return False # 如果检查属性时出错，也认为不是普通目录
# ... (你已有的 clean_tax_id, clean_phone 等函数) ...