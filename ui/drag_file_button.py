from PyQt5.QtWidgets import QLineEdit, QFileDialog
from PyQt5.QtCore import Qt


class DragFileButton(QLineEdit):
    """
    Drag or click to select file
    """
    def __init__(self, *args, **kwargs):
        on_file_path_changed = kwargs.pop('on_file_path_changed', None)
        if on_file_path_changed:
            self.on_file_path_changed = on_file_path_changed
        self.file_filter = kwargs.pop('file_filter', 'All Files (*)')

        super().__init__(*args, **kwargs)

        self.setPlaceholderText("Attach PDF file by dropping it here or selecting it")
        self.setReadOnly(True)
        self.setStyleSheet(self.build_style('gray'))
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # event.accept()
            self.setStyleSheet(self.build_style('lightgray', '#f0f0f0'))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # event.accept()
            self.setStyleSheet(self.build_style('gray'))
            self.open_file_dialog()
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.highlight_input_area(True)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.highlight_input_area(False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self.highlight_input_area(False)
        if event.mimeData().hasUrls():
            file_url = event.mimeData().urls()[0]
            file_path = file_url.toLocalFile()
            self.file_path_changed(file_path)
        super().dropEvent(event)

    def highlight_input_area(self, highlight):
        if highlight:
            self.setStyleSheet(self.build_style('yellow'))
        else:
            self.setStyleSheet(self.build_style('gray'))  # 恢复默认样式

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", self.file_filter, options=options)
        if file_name:
            self.file_path_changed(file_name)  # 调用回调函数

    def file_path_changed(self, file_name):
        if not file_name:
            return
        self.setText(file_name)
        if self.on_file_path_changed:  # 检查回调是否被定义
            self.on_file_path_changed(file_name)  # 调用回调函数

    @staticmethod
    def build_style(border_color, bg_color=None):
        common = "QLineEdit { padding: 4px 15px; text-align: center; border: 2px dashed " + border_color
        if bg_color is None:
            return common + "; }"
        return common + "; background-color: " + bg_color + "; }"