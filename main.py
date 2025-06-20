# D:\newpro\smart_folder_app\main.py

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QStatusBar
from PyQt6.QtGui import QCloseEvent

from utils import constants
from core.config_manager import ConfigManager
from tabs.folder_creator_tab import FolderCreatorTab # 正确导入 FolderCreatorTab
# from tabs.order_management_tab import OrderManagementTab # 待实现
# ... 其他tab导入

class MainWindow(QMainWindow): # MainWindow 定义在这里
    def __init__(self):
        super().__init__()
        print("MainWindow __init__ started.")
        self.config_manager = ConfigManager()

        self.setWindowTitle(f"{constants.APP_NAME} v{constants.APP_VERSION}")
        self._load_window_settings()


        self.main_tab_widget = QTabWidget() # 主界面用一个 QTabWidget
        self.setCentralWidget(self.main_tab_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # self.status_bar.showMessage("准备就绪。", 3000) # 初始状态由 tab 的 status_updated 设置


        # --- 初始化各个标签页 ---
        try:
            self.folder_creator_tab_instance = FolderCreatorTab(self.config_manager, self)
            self.folder_creator_tab_instance.status_updated.connect(self.update_status_bar)  # <--- 连接信号
            self.main_tab_widget.addTab(self.folder_creator_tab_instance, "智能文件夹创建")
            print(f"Number of tabs in main_tab_widget: {self.main_tab_widget.count()}")
            print("FolderCreatorTab added to MainWindow.")
        except Exception as e:
            print(f"Error initializing or adding FolderCreatorTab: {e}")
            import traceback
            traceback.print_exc()

        # 其他标签页 (待实现)
        # self.order_management_tab = OrderManagementTab(self.config_manager, self)
        # self.main_tab_widget.addTab(self.order_management_tab, "订单管理")

        self.update_status_bar("准备就绪。", False, 3000) # 初始化状态栏信息
        print("MainWindow __init__ finished.")

        print("FolderCreatorTab UI initialized and layout set.")

    def update_status_bar(self, message, is_error=False, duration=5000): # 确保参数匹配信号
        if is_error:
            self.status_bar.setStyleSheet("color: red;")
        else:
            self.status_bar.setStyleSheet("")
        self.status_bar.showMessage(message, duration)
        print(f"Status bar updated: {message}")


    def _load_window_settings(self):
        print("Loading window settings...")
        geometry = self.config_manager.get("window_geometry")
        if geometry and isinstance(geometry, list) and len(geometry) == 4:
            try:
                self.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
                print(f"Window geometry set from config: {geometry}")
            except Exception as e:
                print(f"加载窗口几何位置错误: {e}. Using default.")
                self.setGeometry(150, 150, 1450, 950) # 稍大一点的默认值
        else:
            print("No valid window geometry in config or invalid format. Using default.")
            self.setGeometry(150, 150, 1450, 950)

        # 恢复主 QTabWidget 的 QSplitter 状态 (如果MainWindow直接包含它们)
        # 但通常 splitter 在各自的 tab 内部，所以应由 tab 自己恢复
        # 如果 tab 恢复 splitter 状态，确保在 tab 的 UI 完全构建和显示后进行


    def _save_window_settings(self):
        geom = self.geometry()
        self.config_manager.set("window_geometry", [geom.x(), geom.y(), geom.width(), geom.height()])
        print(f"Window geometry saved: {[geom.x(), geom.y(), geom.width(), geom.height()]}")


    def closeEvent(self, event: QCloseEvent):
        print("MainWindow closeEvent triggered.")
        # 通知所有 tab 保存它们的状态
        if hasattr(self, 'folder_creator_tab_instance') and hasattr(self.folder_creator_tab_instance, 'before_close'):
            self.folder_creator_tab_instance.before_close()
        # if hasattr(self, 'order_management_tab') and hasattr(self.order_management_tab, 'before_close'):
        #     self.order_management_tab.before_close()

        self._save_window_settings()
        self.config_manager.save_config() # 确保所有配置都已写入
        print("Configuration saved.")
        event.accept()


if __name__ == '__main__': # 这个只应该在 main.py 中
    print("Application starting...")
    app = QApplication(sys.argv)
    print("QApplication instantiated.")

    try:
        main_win = MainWindow()
        print("MainWindow instantiated.")
        main_win.show()
        print("main_win.show() called.")
    except Exception as e:
        print(f"Error during MainWindow creation or show: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("Starting app.exec()...")
    exit_code = app.exec()
    print(f"Application finished with exit code: {exit_code}")
    sys.exit(exit_code)