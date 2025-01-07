import re

from PyPDF2.generic import Fit
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTContainer
from PyPDF2 import PdfWriter, PdfReader

class PdfUtil:

    @staticmethod
    def log(msg):
        pass

    @staticmethod
    def get_pdf_page_count(pdf_file_path):
        with open(pdf_file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            page_count = len(pdf_reader.pages)
        return page_count

    @staticmethod
    def extract_text_from_element(element):
        """从给定的元素提取文本。"""
        text = ""
        if isinstance(element, LTTextContainer):
            text += element.get_text()
        elif isinstance(element, LTContainer):
            for child in element:
                text += PdfUtil.extract_text_from_element(child)
        return text

    @staticmethod
    def extract_headings(pdf_path, patten, begin_index=0, progress_callback=None):
        headings = []
        edge_x = 1000
        page_total = PdfUtil.get_pdf_page_count(pdf_path) - begin_index
        for page_number, page_layout in enumerate(extract_pages(pdf_path), start=1):
            if page_number < begin_index:
                continue
            if progress_callback:
                progress_callback(page_total, page_number - begin_index)
            for element in page_layout:
                text = PdfUtil.extract_text_from_element(element).strip()
                if not (text and len(text) >= 4 and re.match(patten, text)):
                    continue
                if element.x0 > edge_x:
                    continue
                edge_x = element.x0 + 1

                heading_level = text.split(' ')[0].count('.') # 书签层级，从 0 开始
                PdfUtil.log(f'[{page_number} - ({element.x0}, {round(element.y0, 2)}) - {heading_level}] [{text}]')
                headings.append(
                    {
                        'text': text,
                        'page': page_number,
                        'x': element.x0,
                        'y': element.y0,
                        'level': heading_level
                    }
                )
        return headings

    @staticmethod
    def find_parent(stack: [], level):
        parent_obj = None
        for j in range(len(stack) - 1, 0, -1):
            if stack[j]['level'] < level:
                parent_obj = stack[j]['obj']
                break
        return parent_obj

    @staticmethod
    def create_pdf_with_bookmarks(original_pdf_path, headings, output_pdf_path, progress_callback=None):
        page_total = PdfUtil.get_pdf_page_count(original_pdf_path)

        writer = PdfWriter()
        reader = PdfReader(original_pdf_path)

        # 遍历标题并添加到 PDF
        stack = [{'level': -1, 'obj': None}]
        j = 0
        for i, heading in enumerate(headings):
            while j < heading['page']:
                writer.add_page(reader.pages[j])
                j += 1
                if progress_callback:
                    progress_callback(page_total, j)

            # 添加书签
            level = heading['level']
            while stack[-1]['level'] >= level:
                stack.pop(-1)

            parent_obj = PdfUtil.find_parent(stack, level)
            obj = writer.add_outline_item(heading['text'], heading['page'] - 1, parent=parent_obj, fit=Fit.xyz(top=heading['y'] + 20))
            stack.append({'level': level, 'obj': obj})

        while j < len(reader.pages):
            writer.add_page(reader.pages[j])
            j += 1
            if progress_callback:
                progress_callback(page_total, j)

        # 保存新的 PDF 文件
        with open(output_pdf_path, "wb") as f:
            writer.write(f)