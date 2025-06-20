import json
import os
from utils.constants import CONFIG_FILE, APP_NAME
from utils.helpers import sanitize_filename # 如果需要

class ConfigManager:
    def __init__(self):
        self.config_path = CONFIG_FILE
        self.config_data = self._load_config()

    def _load_config(self):
        defaults = {
            "last_creation_directory": os.getcwd(),
            "last_selected_folder_left_tree": os.getcwd(),
            "favorite_folders": [],
            "window_geometry": None, # 用于保存窗口大小和位置
            "sash_positions": {},    # 用于保存QSplitter的位置
            # 可以为每个tab保存最后选择的条目等
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 合并默认值，确保新配置项存在
                    for key, value in defaults.items():
                        if key not in data:
                            data[key] = value
                    return data
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置文件 {self.config_path} 失败: {e}. 使用默认配置。")
                return defaults
        return defaults

    def save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"错误: 保存配置文件到 {self.config_path} 失败 - {e}")
            # 可以考虑弹窗提示用户

    def get(self, key, default=None):
        return self.config_data.get(key, default)

    def set(self, key, value):
        self.config_data[key] = value
        # self.save_config() # 可以选择立即保存或在程序退出时统一保存

    # --- 特定于原Tkinter版配置的getter/setter ---
    def get_last_creation_directory(self):
        return self.get("last_creation_directory", os.getcwd())

    def set_last_creation_directory(self, path):
        if path and os.path.isdir(path):
            self.set("last_creation_directory", path)

    def get_favorite_folders(self):
        return self.get("favorite_folders", [])

    def set_favorite_folders(self, favorites_list):
        self.set("favorite_folders", favorites_list)

    def add_favorite_folder(self, name, path):
        norm_path = os.path.normpath(path)
        favorites = self.get_favorite_folders()
        if not any(os.path.normpath(f.get("path", "")) == norm_path for f in favorites):
            favorites.append({"name": name, "path": norm_path})
            self.set_favorite_folders(favorites)
            return True
        return False # 已存在

    def remove_favorite_folder(self, path_to_remove):
        norm_path_to_remove = os.path.normpath(path_to_remove)
        favorites = self.get_favorite_folders()
        updated_favorites = [fav for fav in favorites if os.path.normpath(fav.get("path", "")) != norm_path_to_remove]
        if len(updated_favorites) < len(favorites):
            self.set_favorite_folders(updated_favorites)
            return True
        return False

    # ... 其他配置项的 get/set 方法