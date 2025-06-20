# D:\newpro\smart_folder_app\tabs\folder_creator_tab.py
import os
import platform

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSplitter, QListWidget, QTreeWidget, QTextEdit, QComboBox, QRadioButton,
    QScrollArea, QFrame, QSizePolicy, QToolBar, QTabWidget, QTreeWidgetItem,
    QListWidgetItem,
    QApplication,  # <--- 添加 QApplication
    QStyle         # <--- 添加 QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

from utils import constants, helpers


# config_manager 会作为参数传入

class FolderCreatorTab(QWidget):
    status_updated = pyqtSignal(str, bool, int)  # message, is_error, duration
    # 信号，用于请求导航到左侧树的某个路径
    request_left_tree_navigation = pyqtSignal(str)

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_hyperlink_path = None  # 用于存储当前超链接的路径
        self._notes_modified_flag = False  # 用于跟踪笔记是否被修改

        self._init_ui()
        self._load_initial_data()
        self._connect_signals()
        print("FolderCreatorTab initialized.")

    def _init_ui(self):
        # ... (大部分UI代码不变，确保 self.folder_hyperlink_label 设置如下) ...
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # 1. 最左侧：常用文件夹
        favorites_frame = QFrame()
        favorites_frame_layout = QVBoxLayout(favorites_frame)
        favorites_frame.setMinimumWidth(180);
        favorites_frame.setMaximumWidth(300)
        fav_toolbar = QToolBar()
        self.fav_up_action = QAction("↑", self);
        fav_toolbar.addAction(self.fav_up_action)
        self.fav_down_action = QAction("↓", self);
        fav_toolbar.addAction(self.fav_down_action)
        favorites_frame_layout.addWidget(QLabel("常用文件夹:"))
        favorites_frame_layout.addWidget(fav_toolbar)
        self.favorites_list_widget = QListWidget()
        favorites_frame_layout.addWidget(self.favorites_list_widget)

        # 2. 中间和右侧区域
        center_right_splitter = QSplitter(Qt.Orientation.Horizontal)
        center_right_splitter.setObjectName("fct_center_right_splitter")

        # 2.1 中间面板
        center_panel = QFrame()
        center_panel_layout = QVBoxLayout(center_panel)
        center_panel.setMinimumWidth(350)
        tree_customer_splitter = QSplitter(Qt.Orientation.Vertical)
        tree_customer_splitter.setObjectName("fct_tree_customer_splitter")

        drive_tree_frame = QFrame()
        drive_tree_layout = QVBoxLayout(drive_tree_frame)
        drive_select_layout = QHBoxLayout()
        drive_select_layout.addWidget(QLabel("驱动器:"))
        self.drive_combo = QComboBox()
        drive_select_layout.addWidget(self.drive_combo)
        drive_tree_layout.addLayout(drive_select_layout)
        self.left_tree_widget = QTreeWidget()
        self.left_tree_widget.setHeaderLabel("文件夹结构")
        drive_tree_layout.addWidget(self.left_tree_widget)
        drive_tree_frame.setLayout(drive_tree_layout)
        tree_customer_splitter.addWidget(drive_tree_frame)

        customer_list_frame = QFrame()  # 客户列表UI占位
        # ... (customer_list_frame 的内容暂时省略) ...
        tree_customer_splitter.addWidget(customer_list_frame)
        center_panel_layout.addWidget(tree_customer_splitter)

        creation_controls_frame = QFrame()
        creation_controls_layout = QVBoxLayout(creation_controls_frame)
        self.creation_dir_edit = QLineEdit()
        browse_button = QPushButton("浏览...")
        # browse_button.clicked.connect(self.select_creation_directory_slot)
        copy_path_button = QPushButton("复制路径")
        # copy_path_button.clicked.connect(self.copy_creation_directory_slot)
        self.create_folder_button = QPushButton("创建文件夹")
        self.folder_hyperlink_label = QLabel("当前路径: 未选择")
        self.folder_hyperlink_label.setTextFormat(Qt.TextFormat.RichText)
        self.folder_hyperlink_label.setOpenExternalLinks(False)  # 重要：自己处理点击

        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("创建位置:"))
        path_layout.addWidget(self.creation_dir_edit)
        path_layout.addWidget(browse_button)
        path_layout.addWidget(copy_path_button)
        creation_controls_layout.addLayout(path_layout)
        creation_controls_layout.addWidget(self.create_folder_button)
        creation_controls_layout.addWidget(self.folder_hyperlink_label)
        center_panel_layout.addWidget(creation_controls_frame)
        center_panel.setLayout(center_panel_layout)
        center_right_splitter.addWidget(center_panel)

        # 2.2 右侧面板 (暂时只创建框架)
        right_panel = QFrame()
        # ... (right_panel 的内容暂时简化或省略) ...
        center_right_splitter.addWidget(right_panel)

        main_layout.addWidget(favorites_frame)
        main_layout.addWidget(center_right_splitter)

    def _load_initial_data(self):
        # 常用文件夹
        favs = self.config_manager.get_favorite_folders()
        self.favorites_list_widget.clear()
        for fav_item in favs:
            name = fav_item.get("name", "未命名")
            path = fav_item.get("path")
            list_item = QListWidgetItem(name)
            if path:
                list_item.setData(Qt.ItemDataRole.UserRole, path)  # 存储路径
                list_item.setToolTip(path)  # 鼠标悬停显示路径
            self.favorites_list_widget.addItem(list_item)
        print(f"Loaded {len(favs)} favorite(s).")

        # 驱动器
        drives = helpers.get_available_drives()
        self.drive_combo.clear()  # 清空以防重复添加
        self.drive_combo.addItems(drives)
        last_drive = self.config_manager.get("last_selected_drive")
        if last_drive and last_drive in drives:
            self.drive_combo.setCurrentText(last_drive)
        elif drives:
            self.drive_combo.setCurrentIndex(0)
        print(f"Drives loaded. Current: {self.drive_combo.currentText()}")

        # 上次创建目录
        last_creation_dir = self.config_manager.get_last_creation_directory()
        self.creation_dir_edit.setText(last_creation_dir)
        self.update_folder_hyperlink_label(last_creation_dir)  # 初始更新超链接

        # 初始加载左侧树 (如果驱动器已选)
        current_drive_text = self.drive_combo.currentText()
        if current_drive_text:
            self.populate_left_tree_from_drive(current_drive_text)
        else:
            print("No drive selected initially for tree population.")

    def _connect_signals(self):
        self.favorites_list_widget.itemClicked.connect(self.on_favorite_folder_selected)
        # self.fav_up_action.triggered.connect(self.move_favorite_up) # 稍后实现
        self.drive_combo.currentTextChanged.connect(self.populate_left_tree_from_drive)
        self.left_tree_widget.itemClicked.connect(self.on_left_tree_item_selected)
        self.folder_hyperlink_label.linkActivated.connect(self.open_hyperlink_from_label_slot)  # 连接信号
        # self.create_folder_button.clicked.connect(self.create_folder_slot) # 稍后实现

        # self.favorites_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self.favorites_list_widget.customContextMenuRequested.connect(self.show_favorites_context_menu)

    def populate_left_tree_from_drive(self, drive_path):
        self.left_tree_widget.clear()
        if not drive_path or not os.path.isdir(drive_path):
            self.status_updated.emit(f"驱动器路径无效: {drive_path}", True, 3000)
            return

        self.config_manager.set("last_selected_drive", drive_path)
        self.status_updated.emit(f"加载驱动器: {drive_path}...", False, 1000)

        # 修正：确保drive_path本身是有效的目录
        actual_drive_path = os.path.normpath(drive_path)
        if not os.path.isdir(actual_drive_path):
            self.status_updated.emit(f"无法访问驱动器: {actual_drive_path}", True, 3000)
            return

        # 获取驱动器的显示名称
        drive_display_name = os.path.basename(actual_drive_path)
        if not drive_display_name and (platform.system() == "Windows" and actual_drive_path.endswith("\\")):
            drive_display_name = actual_drive_path.rstrip("\\")  # C:\ -> C:
        elif not drive_display_name:
            drive_display_name = actual_drive_path  # 对于 / 或 ~

        root_item = QTreeWidgetItem(self.left_tree_widget, [drive_display_name])
        root_item.setData(0, Qt.ItemDataRole.UserRole, actual_drive_path)
        root_item.setIcon(0, QApplication.style().standardIcon(
            QStyle.StandardPixmap.SP_DriveHDIcon if platform.system() == "Windows" else QStyle.StandardPixmap.SP_FolderIcon))  # 给驱动器一个图标
        self._populate_children_qt(root_item, actual_drive_path)
        root_item.setExpanded(True)  # 默认展开驱动器根目录

        # 尝试导航到该驱动器下上次选择的文件夹
        last_selected_path = self.config_manager.get("last_selected_folder_left_tree")
        if last_selected_path and os.path.normpath(last_selected_path).startswith(os.path.normpath(actual_drive_path)):
            self.try_navigate_left_tree_to_path(last_selected_path)  # 先占位
        else:  # 如果没有上次选择或不匹配当前驱动器，则默认选择驱动器本身
            self.left_tree_widget.setCurrentItem(root_item)
            self.on_left_tree_item_selected(root_item, 0)  # 手动触发一次，以更新UI

    def _populate_children_qt(self, parent_qtreeitem, parent_path):
        if not os.path.isdir(parent_path):
            return
        try:
            entries = sorted(os.listdir(parent_path))
        except OSError as e:
            self.status_updated.emit(f"无法读取 '{os.path.basename(parent_path)}': {e}", True, 4000)
            return

        for entry_name in entries:
            full_path = os.path.join(parent_path, entry_name)
            if os.path.isdir(full_path) and helpers._is_normal_directory(full_path):
                child_item = QTreeWidgetItem(parent_qtreeitem, [entry_name])
                child_item.setData(0, Qt.ItemDataRole.UserRole, full_path)
                child_item.setIcon(0, QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))

                # 初步的懒加载指示器：如果它还有子目录，就让它可以展开
                try:
                    if any(os.path.isdir(os.path.join(full_path, sub)) and helpers._is_normal_directory(
                            os.path.join(full_path, sub)) for sub in os.listdir(full_path)):
                        child_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.Showレクトリ)
                        # 或者添加一个dummy子节点以便后续在itemExpanded时加载
                        # QTreeWidgetItem(child_item, ["加载中..."])
                except OSError:
                    pass  # 忽略下一级目录的访问错误

    def on_left_tree_item_selected(self, item, column):
        if item is None: return  # 防止item为空时出错
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path and os.path.isdir(path):
            if not self.check_unsaved_notes():  # 检查笔记
                # 如果用户取消，可能需要恢复之前的选择，或者阻止导航
                # 暂时简单处理：如果取消，就不更新
                previous_path = self.config_manager.get("last_selected_folder_left_tree")
                if previous_path:
                    # 尝试找到并重新选中之前的项 (这里简化，实际可能需要遍历)
                    if self.left_tree_widget.currentItem() and self.left_tree_widget.currentItem().data(0,
                                                                                                        Qt.ItemDataRole.UserRole) != previous_path:
                        pass  # 用户取消了，选择未改变
                return

            self.creation_dir_edit.setText(path)
            self.update_folder_hyperlink_label(path)
            self.config_manager.set("last_selected_folder_left_tree", path)
            self.status_updated.emit(f"已选择: {path}", False, 2000)

            # 更新右侧面板的占位符
            print(f"TODO: Populate right tree for: {path}")
            # self.populate_right_tree(path)
            print(f"TODO: Display notes for: {path}")
            # self.display_folder_note(path)
            print(f"TODO: Load images for: {path}")
            # self.load_images_for_folder(path)

            # 懒加载实现：当节点被点击（或展开）时加载子节点
            # 如果是点击展开的，itemExpanded信号更合适
            if item.childCount() > 0 and item.child(0).text(0) == "加载中...":
                item.takeChild(0)  # 移除"加载中..."
                self._populate_children_qt(item, path)

        elif path:  # 是文件或其他无效路径
            self.status_updated.emit(f"所选非目录: {path}", True, 3000)
        # else: item 可能没有 UserRole 数据，例如 "加载中..." 节点

    def update_folder_hyperlink_label(self, folder_path):
        if folder_path and os.path.isdir(folder_path):
            self.current_hyperlink_path = folder_path
            display_path = folder_path
            if len(display_path) > 70:  # 根据标签宽度调整
                display_path = "..." + display_path[-67:]
            # 使用 file:/// 协议，但QDesktopServices.openUrl 更可靠
            # QLabel的linkActivated信号会传递href的值
            self.folder_hyperlink_label.setText(f"当前: <a href='{folder_path}'>{display_path}</a>")
            self.folder_hyperlink_label.setToolTip(folder_path)
        else:
            self.current_hyperlink_path = None
            self.folder_hyperlink_label.setText("当前路径: 未选择")
            self.folder_hyperlink_label.setToolTip("")

    def open_hyperlink_from_label_slot(self, link_url_str):
        # link_url_str 就是 href 的值
        if link_url_str and os.path.isdir(link_url_str):
            helpers.open_path_externally(link_url_str)
        else:
            self.status_updated.emit(f"无法打开链接路径: {link_url_str}", True, 3000)

    def on_favorite_folder_selected(self, item_widget: QListWidgetItem):
        path_to_nav = item_widget.data(Qt.ItemDataRole.UserRole)
        if path_to_nav and os.path.isdir(path_to_nav):
            if not self.check_unsaved_notes():
                # 用户取消，取消列表中的选择（如果需要）
                self.favorites_list_widget.setCurrentItem(None)
                return

            self.status_updated.emit(f"导航到常用: {path_to_nav}", False, 1000)
            self.try_navigate_left_tree_to_path(path_to_nav)  # 占位
        elif path_to_nav:
            self.status_updated.emit(f"常用文件夹路径 '{path_to_nav}' 无效。", True, 3000)

    def try_navigate_left_tree_to_path(self, path_to_find_str):
        """
        尝试在左侧树中找到并选中指定的路径。
        这是一个复杂的方法，需要递归查找和展开。
        初步实现：触发 request_left_tree_navigation 信号，让 MainWindow 或更上层的组件处理导航逻辑，
        因为它可能需要改变驱动器组合框并重新填充整个树。
        或者，如果路径在当前驱动器下，则尝试在此 Tab 内部处理。
        """
        self.status_updated.emit(f"TODO: 导航到左侧树路径: {path_to_find_str}", False, 1000)
        # 简化版：如果路径在当前驱动器下，尝试直接查找
        current_drive = self.drive_combo.currentText()
        norm_path_to_find = os.path.normpath(path_to_find_str)
        norm_current_drive = os.path.normpath(current_drive)

        if current_drive and norm_path_to_find.startswith(norm_current_drive):
            # 路径在当前驱动器下
            path_components = os.path.relpath(norm_path_to_find, norm_current_drive).split(os.sep)
            if path_components == ['.']:  # 就是驱动器根目录
                if self.left_tree_widget.topLevelItemCount() > 0:
                    self.left_tree_widget.setCurrentItem(self.left_tree_widget.topLevelItem(0))
                    self.on_left_tree_item_selected(self.left_tree_widget.topLevelItem(0), 0)
            return

            current_item = None
            if self.left_tree_widget.topLevelItemCount() > 0:
                current_item = self.left_tree_widget.topLevelItem(0)  # 从驱动器根节点开始

            for component in path_components:
                if not current_item: break
                found_child = None
                # 如果有 "加载中..." 子节点，先加载
                if current_item.childCount() > 0 and current_item.child(0).text(0) == "加载中...":
                    current_item.takeChild(0)
                    self._populate_children_qt(current_item, current_item.data(0, Qt.ItemDataRole.UserRole))

                for i in range(current_item.childCount()):
                    child = current_item.child(i)
                    if child.text(0).lower() == component.lower():  # 不区分大小写匹配
                        found_child = child
                        break
                if found_child:
                    current_item.setExpanded(True)
                    current_item = found_child
                else:
                    current_item = None  # 未找到路径
                    break

            if current_item:
                self.left_tree_widget.setCurrentItem(current_item)
                self.left_tree_widget.scrollToItem(current_item)
                self.on_left_tree_item_selected(current_item, 0)  # 触发选择更新
            else:
                self.status_updated.emit(f"路径 '{path_to_find_str}' 在当前树中未找到。", True, 3000)
        else:
            # 路径不在当前驱动器，需要切换驱动器
            # 发射信号让 MainWindow 处理，或者直接调用切换驱动器的逻辑
            self.status_updated.emit(f"需要切换驱动器以导航到: {path_to_find_str}", False, 2000)
            # 查找路径属于哪个驱动器
            target_drive = None
            for drive_opt in [self.drive_combo.itemText(i) for i in range(self.drive_combo.count())]:
                if norm_path_to_find.startswith(os.path.normpath(drive_opt)):
                    target_drive = drive_opt
                    break
            if target_drive and target_drive != current_drive:
                self.drive_combo.setCurrentText(target_drive)  # 这会触发 populate_left_tree_from_drive
                # populate_left_tree_from_drive 应该在其末尾调用 try_navigate (如果路径匹配新驱动器)
            elif target_drive == current_drive:  # 驱动器相同但路径未找到，可能树未完全加载
                pass  # 已在上面的逻辑中处理
            else:
                self.status_updated.emit(f"无法为路径 '{path_to_find_str}' 确定驱动器。", True, 3000)

    def check_unsaved_notes(self):
        """检查是否有未保存的笔记，并询问用户。返回True表示可以继续，False表示用户取消。"""
        if self._notes_modified_flag:
            # TODO: 替换为 QMessageBox
            # response = messagebox.askyesnocancel("未保存的笔记", "当前文件夹的笔记已被修改，是否保存？", parent=self)
            # if response is True:
            #     self.save_current_folder_note_slot() # 假设有这个槽
            #     return not self._notes_modified_flag # 如果保存失败，则仍为True
            # elif response is False: # 不保存
            #     self._notes_modified_flag = False
            #     # self.notes_text_edit.document().setModified(False) # 清除修改状态
            #     return True
            # else: # Cancel
            #     return False
            print("TODO: Check unsaved notes - returning True for now")
            return True  # 暂时允许继续
        return True

    # --- 其他占位符槽函数 ---
    def move_favorite_up(self):
        self.status_updated.emit("TODO: 上移常用项", False, 1000)

    def create_folder_slot(self):
        self.status_updated.emit("TODO: 创建文件夹逻辑", False, 1000)

    def show_favorites_context_menu(self, position):
        self.status_updated.emit(f"TODO: 右键菜单: {position}", False, 1000)