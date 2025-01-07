import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QProgressBar

from ui.drag_file_button import DragFileButton

class FileSelector(QWidget):
    def __init__(self, on_file_confirmed=None):
        super().__init__()

        self.setGeometry(100, 100, 1000, 400)

        self.on_file_confirmed = on_file_confirmed
        self.input_pdf_path = None
        self.output_pdf_path = None

        # Input file path
        self.line_edit_a = DragFileButton(self,
                                          on_file_path_changed=self.on_file_path_changed,
                                          file_filter='PDF 文件 (*.pdf)')
        self.line_edit_a.setFixedHeight(60)

        # Output file path
        self.line_edit_b = QLineEdit(self)
        self.line_edit_b.setReadOnly(True)
        self.line_edit_b.setPlaceholderText("Output path")
        self.line_edit_b.setFixedHeight(40)
        self.line_edit_b.setStyleSheet("QLineEdit { padding: 4px 15px; }")

        self.analysis_progress_bar = QProgressBar(self)
        self.analysis_progress_bar.setFixedHeight(30)
        self.analysis_progress_bar.setAlignment(Qt.AlignCenter)

        self.create_pdf_progress_bar = QProgressBar(self)
        self.create_pdf_progress_bar.setFixedHeight(30)
        self.create_pdf_progress_bar.setAlignment(Qt.AlignCenter)

        # Confirm button
        btn_confirm = QPushButton('确认', self)
        btn_confirm.setFixedHeight(40)
        btn_confirm.setFixedWidth(100)
        btn_confirm.clicked.connect(self.confirm)

        # Exit
        btn_exit = QPushButton('退出', self)
        btn_exit.setFixedHeight(40)
        btn_exit.setFixedWidth(100)
        btn_exit.clicked.connect(self.close)

        # Layout
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.line_edit_a)
        v_layout.addWidget(self.line_edit_b)
        v_layout.addWidget(self.analysis_progress_bar)
        v_layout.addWidget(self.create_pdf_progress_bar)

        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(btn_confirm)
        h_layout.addWidget(btn_exit)
        h_layout.addStretch()

        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

    def on_file_path_changed(self, input_pdf_path):
        if not os.path.isfile(input_pdf_path) or not input_pdf_path.endswith('.pdf'):
            return

        self.input_pdf_path = input_pdf_path
        self.output_pdf_path = input_pdf_path[0:-4] + '_bookmark.pdf'
        self.line_edit_b.setText(self.output_pdf_path)

    def confirm(self):
        if self.on_file_confirmed:
            self.on_file_confirmed(self.input_pdf_path, self.output_pdf_path)