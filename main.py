import os.path
import re

from PyPDF2.generic import Fit
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTContainer
from PyPDF2 import PdfWriter, PdfReader

def log(msg):
    pass
    # print(msg)

def extract_text_from_element(element):
    """从给定的元素提取文本。"""
    text = ""
    if isinstance(element, LTTextContainer):
        text += element.get_text()
    elif isinstance(element, LTContainer):
        # 递归遍历子元素
        for child in element:
            text += extract_text_from_element(child)
    return text

def extract_headings(pdf_path, patten, begin_index=0):
    headings = []
    edge_x = 1000
    for page_number, page_layout in enumerate(extract_pages(pdf_path), start=1):
        if page_number < begin_index:
            continue
        for element in page_layout:
            text = extract_text_from_element(element).strip()
            if text and len(text) >= 4:
                if re.match(patten, text):
                    if element.x0 > edge_x:
                        continue
                    edge_x = element.x0 + 1

                    heading_level = text.split(' ')[0].count('.') # 书签层级，从 0 开始
                    log(f'[{page_number} - ({element.x0}, {round(element.y0, 2)}) - {heading_level}] [{text}]')
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

def find_parent(stack: [], level):
    parent_obj = None
    for j in range(len(stack) - 1, 0, -1):
        if stack[j]['level'] < level:
            parent_obj = stack[j]['obj']
            break
    return parent_obj

def create_pdf_with_bookmarks(original_pdf_path, headings, output_pdf_path):
    writer = PdfWriter()
    reader = PdfReader(original_pdf_path)

    # 遍历标题并添加到 PDF
    stack = [{'level': -1, 'obj': None}]
    j = 0
    for i, heading in enumerate(headings):
        while j < heading['page']:
            writer.add_page(reader.pages[j])
            j += 1

        # 添加书签
        level = heading['level']
        while stack[-1]['level'] >= level:
            stack.pop(-1)

        parent_obj = find_parent(stack, level)
        obj = writer.add_outline_item(heading['text'], heading['page'] - 1, parent=parent_obj, fit=Fit.xyz(top=heading['y'] + 20))
        stack.append({'level': level, 'obj': obj})

    while j < len(reader.pages):
        writer.add_page(reader.pages[j])
        j += 1

    # 保存新的 PDF 文件
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

def __main__():
    # Unicode 码表见
    #   https://symbl.cc/cn/unicode-table/
    #   https://en.wikipedia.org/wiki/List_of_Unicode_characters
    patten = r'^[1-9]{1,2}(\.\d{1,2})*.? *[\w\&\-\u4e00-\u9fa5\u2018-\u201f\u3001\u300a\u300b\u3010\u3011\uff01\uff08\uff09\uff0c\ff1a\ff1f\+ ]+\.?$'

    input_pdf_path = input('请输入 PDF 文件路径：')
    while not os.path.isfile(input_pdf_path) or not input_pdf_path.endswith('.pdf'):
        input_pdf_path = input('文件不存在，请重新输入 PDF 文件路径：')

    # output_pdf_path = 'output_with_bookmarks.pdf'
    output_pdf_path = input_pdf_path[0:-4] + '_bookmark.pdf'

    print()
    begin_index_str = input('从第几页开始识别标题？(默认 0)：')

    begin_index = 0 if begin_index_str == '' else int(begin_index_str)

    print()
    print('开始识别标题...')

    # 提取标题及其位置信息
    headings = extract_headings(input_pdf_path, patten, begin_index)

    # 创建新 PDF 文件并添加书签
    create_pdf_with_bookmarks(input_pdf_path, headings, output_pdf_path)

    print(f"书签已添加到新的 PDF 文件: {output_pdf_path}")

__main__()