import os
import re
import pandas as pd
import csv
import itertools
import pyocr
import pyocr.builders
import io
import operator
import datetime
# import multiprocessing
from policy.param import *
from subprocess import call
from multiprocessing import Pool
from functools import cmp_to_key
from wand.image import Image
from PIL import Image as PI
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed


def splitdate(s):
    return s.split('.')[0]


# def pdfocr():
#     # pyocr支持两种OCR库，由于我只安装了tesseract，只会获得tesseract
#     tool = pyocr.get_available_tools()[0]
#
#     # 选择要使用的语言，使用print tool.get_available_languages()列表
#     lang = tool.get_available_languages()[2]
#
#     # 用来保存图像和对应的文字
#     req_image = []
#     final_text = []
#
#     # 打开pdf文件，并转为图像，替换./test.pdf
#     image_pdf = Image(filename='./pdfs/000938/2004-04-17.pdf', resolution=300)
#     image_jpeg = image_pdf.convert('jpeg')
#
#     # 把图片放到req_image中
#     for img in image_jpeg.sequence:
#         img_page = Image(image=img)
#         req_image.append(img_page.make_blob('jpeg'))
#
#     # 为每个图像运行OCR，识别图像中的文本
#     for img in req_image:
#         txt = tool.image_to_string(
#             PI.open(io.BytesIO(img)),
#             lang=lang,
#             builder=pyocr.builders.TextBuilder()
#         )
#         final_text.append(txt)

'''
 解析pdf 文本，保存到txt文件中
'''


def parse(codename, filename):
    path = r'./pdfs/' + codename + '/' + filename
    fp = open(path, 'rb')  # 以二进制读模式打开
    # 用文件对象来创建一个pdf文档分析器
    praser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    praser.set_document(doc)
    doc.set_parser(praser)

    # 提供初始化密码
    # 如果没有密码 就创建一个空的字符串
    try:
        doc.initialize()
    except:
        call('qpdf --password=%s --decrypt %s %s' % (
            '', path, path), shell=True)
    try:
        if not doc.is_extractable:
            # print(fp.name + ' 不提供提供txt转换')
            # raise PDFTextExtractionNotAllowed
            os.remove(path)
            return
    except AttributeError:
        os.remove(path)
    else:
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        try:
            os.remove(r'./pdfs/' + codename + '/' + filename.replace(
                'pdf', 'txt'))
        except FileNotFoundError:
            pass
        # 循环遍历列表，每次处理一个page的内容
        for page in doc.get_pages():  # doc.get_pages() 获取page列表
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            """ 
            这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, 
            LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性
            """
            for x in layout:
                if isinstance(x, LTTextBoxHorizontal):
                    with open(r'./pdfs/' + codename + '/' + filename.replace(
                            'pdf', 'txt'), 'a') as f:
                        results = x.get_text()
                        # print(results)
                        f.write(results + '\n')
        # print('转换完成:', f.name)
        CVnum = SBnum = TLnum = SLnum = QEnum = AMnum = GPnum = 0
        # CVindex = SBindex = TLindex = SLindex = QEindex = AMindex = GPindex = 0
        SB_list = itertools.product(SB[0], SB[1], SB[2])
        TL_list = itertools.product(TL[0], TL[1], TL[2], TL[3], TL[4])
        SL_list = itertools.product(SL[0], SL[1], SL[2], SL[3], SL[4])
        AM_list = itertools.product(AM[0], AM[1], AM[2], AM[3])
        GP_list = itertools.product(GP[0], GP[1])

        file_str = open(f.name).read()
        terms_list = re.split(u'第.*条\s', file_str)
        for term in terms_list[1:]:
            term_non = term.replace('\n', '')
            if CV[0] in term_non or CV[1] in term_non:
                CVnum = 1
                # CVindex = terms_list.index(term)
            for words in SB_list:
                if (words[0] in term_non and words[1] in term_non and words[
                    2] in term_non and SB[-1][0] not in term_non):
                    SBnum = 1
                    # SBindex = terms_list.index(term)
            for words in TL_list:
                if (words[0] in term_non and words[1] in term_non and words[
                    2] in term_non and words[3] in term_non and words[
                    4] in term_non):
                    TLnum = 1
                    # TLindex = terms_list.index(term)
            for words in SL_list:
                if (words[0] in term_non and words[1] in term_non and words[
                    2] in term_non and words[3] in term_non and words[
                    4] in term_non):
                    SLnum = 1
                    # SLindex = terms_list.index(term)
            if QE in term_non:
                QEnum = 1
                # QEindex = terms_list.index(term)
            for words in AM_list:
                if (words[0] in term_non and words[1] in term_non and words[
                    2] in term_non and words[3] in term_non):
                    AMnum = 1
                    # AMindex = terms_list.index(term)
            for words in GP_list:
                if (words[0] in term_non and words[1] in term_non and GP[-1][
                    0] not in term_non and GP[-1][1] not in term_non):
                    GPnum = 1
                    # GPindex = terms_list.index(term)
        return codename, filename.split('.')[
            0], CVnum, SBnum, TLnum, SLnum, QEnum, AMnum, GPnum


def run():
    dir_files = os.walk('pdfs')
    try:
        os.remove(r'res.csv')
    except:
        pass
    with open("res.csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        # 先写入columns_name
        writer.writerow(
            ["code", "date", "CV", "SB", 'TL', 'SL', 'QE', 'AM', 'GP'])
        for path, dir_list, file_list in dir_files:
            # print(path, dir_list, file_list)
            if dir_list:
                continue
            else:
                L = []
                for file_pdf in file_list:
                    if os.path.splitext(file_pdf)[1] == ".pdf":
                        L.append(file_pdf)
                codename = path.split('/')[1]
                date_list = list(map(splitdate, L))
                date_str = str(date_list)
                if date_list.__len__() >= 2:
                    new_list = []
                    for d in date_list:
                        if d[:4] not in str(new_list):
                            new_list.append(d)
                        else:
                            test = [c for c, x in enumerate(new_list) if
                                    x.find(d[:4]) != -1]
                            os.remove('./pdfs/' + codename + '/' + min(
                                [d, new_list[test[0]]]) + '.pdf')
                            file_list.remove(min(
                                [d, new_list[test[0]]]) + '.pdf')
                            print('删除: ', './pdfs/' + codename + '/' + min(
                                [d, new_list[test[0]]]) + '.pdf')

                csv_ros = []
                for filename in file_list:
                    if filename.split('.')[1] == 'pdf':
                        # print(codename,filename)
                        pdf_res = parse(codename, filename)
                        if pdf_res is not None:
                            csv_ros.append(pdf_res)
                            print(path + '/' + filename + ' 转换完成')
                    else:
                        continue
                if csv_ros.__len__() >= 2:
                    # csv_ros.sort(lambda x, y: cmp_to_key(x[1], y[1]))
                    new_ros = add_ros = sorted(csv_ros, key=lambda x: x[1])
                    for n in range(0, new_ros.__len__() - 1):
                        diff = int(new_ros[n + 1][1][:4]) - int(
                            new_ros[n][1][:4])
                        if diff != 1:
                            for d in range(diff-1):
                                add_ros.insert(n + d + 1, add_ros[n])
                                add_ros[n + d + 1] = list(add_ros[n + 1])
                                add_ros[n + d + 1][1] = str(
                                    int(add_ros[n + d + 1][1][:4]) + 1)
                                tuple(add_ros[n + d + 1])
                    # writer.writerows(add_ros)
                    # newyear_t = datetime.datetime.strptime(csv_ros[n+1][1], "%Y-%m-%d")
                    # newyear = newyear_t + datetime.timedelta(year)
                    # 写入多行用writerows
                    writer.writerows(add_ros)
                else:
                    writer.writerow(csv_ros)
                print(codename + ' 文件夹pdf转换txt结束')
        print('所有文件夹pdf转txt结束')


if __name__ == '__main__':
    # pdfocr()
    run()
