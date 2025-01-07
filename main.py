import sys

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMessageBox

from ui.file_selector import FileSelector
from pdf_util import PdfUtil

class Worker(QThread):
    analysis_progress = pyqtSignal(int, int)
    create_pdf_progress = pyqtSignal(int, int)
    task_completed = pyqtSignal()

    def __init__(self, input_pdf_path: str, output_pdf_path: str, begin_index: int):
        """
        构造函数
        :param input_pdf_path: Input pdf file path
        :param output_pdf_path: Output pdf file path
        :param begin_index: From which page to begin recognizing headings
        """
        super().__init__()
        self.input_pdf_path = input_pdf_path
        self.output_pdf_path = output_pdf_path
        self.begin_index = begin_index

    def run(self):
        print('开始识别标题...')

        # Unicode 码表见
        #   https://symbl.cc/cn/unicode-table/
        #   https://en.wikipedia.org/wiki/List_of_Unicode_characters
        patten = r'^[1-9]{1,2}(\.\d{1,2})*.? *[\w\&\-\u4e00-\u9fa5\u2018-\u201f\u3001\u300a\u300b\u3010\u3011\uff01\uff08\uff09\uff0c\ff1a\ff1f\+ ]+\.?$'

        # 提取标题及其位置信息
        headings = PdfUtil.extract_headings(self.input_pdf_path, patten, self.begin_index, self.analysis_heading_progress)

        # 创建新 PDF 文件并添加书签
        PdfUtil.create_pdf_with_bookmarks(self.input_pdf_path, headings, self.output_pdf_path, self.create_new_pdf_progress)

        print(f"书签已添加到新的 PDF 文件: {self.output_pdf_path}")
        self.task_completed.emit()

    def analysis_heading_progress(self, total: int, current: int):
        self.analysis_progress.emit(total, current)

    def create_new_pdf_progress(self, total: int, current: int):
        self.create_pdf_progress.emit(total, current)

class Main:
    def __init__(self):
        self.worker = None
        app = QApplication(sys.argv)
        self.window = FileSelector(on_file_confirmed=self.on_file_confirmed)
        self.window.setWindowTitle("为 PDF 自动添加书签")
        self.window.show()
        sys.exit(app.exec_())

    def on_file_confirmed(self, input_pdf_path: str, output_pdf_path: str):
        self.worker = Worker(input_pdf_path, output_pdf_path, 3)
        self.worker.analysis_progress.connect(self.analysis_heading_progress)
        self.worker.create_pdf_progress.connect(self.create_new_pdf_progress)
        self.worker.task_completed.connect(self.show_finish_dialog)
        self.worker.start()

    def analysis_heading_progress(self, total: int, current: int):
        self.window.analysis_progress_bar.setMaximum(total)
        self.window.analysis_progress_bar.setValue(current)

    def create_new_pdf_progress(self, total: int, current: int):
        self.window.create_pdf_progress_bar.setMaximum(total)
        self.window.create_pdf_progress_bar.setValue(current)

    def show_finish_dialog(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("提示")
        msg_box.setText("书签已添加完成！")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # 将该消息框置于最前
        msg_box.raise_()
        msg_box.activateWindow()

        msg_box.exec_()
        self.window.analysis_progress_bar.setValue(0)
        self.window.create_pdf_progress_bar.setValue(0)

if __name__ == "__main__":
    Main()