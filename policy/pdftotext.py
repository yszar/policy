# -*- coding: utf-8 -*-
import shutil
import os
import re
# import pandas as pd
import csv
import itertools
# import xlrd
# import pyocr
# import pyocr.builders
# import io
# import operator
# import datetime
# import multiprocessing
from policy.param import *
from subprocess import call
# from multiprocessing import Pool
# from functools import cmp_to_key
# from wand.image import Image
# from PIL import Image as PI
from qqai.vision.ocr import GeneralOCR
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFSyntaxError, PDFEncryptionError, PSEOF
from PIL import Image as Image2
from wand.image import Image
from wand.color import Color


def splitdate(s):
    return s.split('.')[0]


def imgtotxt(imglist):
    robot = GeneralOCR('2111235463', 'qQax0hnp02Z43OCY')

    # 识别图片URL
    # result = robot.run(
    #     'https://yyb.gtimg.com/aiplat/ai/assets/ai-demo/express-6.jpg')
    # print(result)
    # {'ret': 0, 'msg': 'ok', 'data': {'text': '一位男士在海边骑自行车的照片'}}

    # 识别打开的本地图片
    ocrstr = ''
    for img in imglist:
        with open(img, 'rb') as image_file:
            ret = 1
            while ret != 0:
                try:
                    result = robot.run(image_file)
                except ConnectionError:
                    ret = 1
                else:
                    ret = result['ret']
            for item in result['data']['item_list']:
                itemstring = item['itemstring']
                ocrstr.join(itemstring)
    return ocrstr
    # {'ret': 0, 'msg': 'ok', 'data': {'text': '一艘飞船'}}


def convert_pdf_to_jpg(filename):
    path = os.path.join('pdfs', filename)
    try:
        shutil.rmtree(os.path.join(os.getcwd(), 'policy', 'image'))
        os.mkdir(os.path.join(os.getcwd(), 'policy', 'image'))
    except FileNotFoundError:
        os.mkdir(os.path.join(os.getcwd(), 'policy', 'image'))
    else:
        imgpath = os.path.join(os.getcwd(), 'policy', 'image')
        end_length = len(filename.split('.')[-1]) + 1
        title = filename[0:-end_length]
        title = title.split('/')[-1]

        # resolution為解析度，background為背景顏色
        with Image(filename=path, resolution=150,
                   background=Color('White')) as img:

            # 頁數
            length = len(img.sequence)

            # 如果頁數超過1頁，生成的文件名會依次加上頁碼數
            with img.convert('jpg') as converted:
                path = os.path.join(imgpath, '%s.jpg') % title
                converted.save(filename=path)
        image_list = []
        if length == 1:
            path = os.path.join(imgpath, '%s.jpg') % title
            image_list.append(path)
        else:
            for i in range(0, length):
                path = os.path.join(imgpath, '%s-%d.jpg') % (
                    title, i)
                image_list.append(path)
        jpg_list = []
        for img in image_list:
            image = Image2.open(img)
            x, y = image.size
            background = Image2.new('RGBA', image.size, (255, 255, 255))

            try:
                background.paste(image, (0, 0, x, y), image)
                image = background.convert('RGB')
            except:
                image = image.convert('RGBA')
                background.paste(image, (0, 0, x, y), image)
                image = background.convert('RGB')

            title = img.split('.')[0]
            name = title + '.jpg'
            image.save(name)
            os.remove(img)
            # name = "%s/%s" % ('static/local_images', name)
            jpg_list.append(name)

        return jpg_list


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


def parse(filename):
    path = os.path.join('pdfs', filename)
    # try:
    fp = open(path, 'rb')  # 以二进制读模式打开
    # 用文件对象来创建一个pdf文档分析器
    praser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    praser.set_document(doc)
    try:
        doc.set_parser(praser)
    except PDFSyntaxError:
        shutil.move(path, os.path.join(os.getcwd(), 'nopdfs', filename))
        return
    # except:
    #     print(filename)
    # 提供初始化密码
    # 如果没有密码 就创建一个空的字符串
    try:
        doc.initialize()
    except PDFEncryptionError:
        newp = path.split('.')[0] + '-t' + '.pdf'
        os.rename(path, newp)
        call('qpdf --password=%s --decrypt %s %s' % (
            '', newp, path), shell=True)
        os.remove(newp)
    try:
        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed
    except (PDFTextExtractionNotAllowed, AttributeError):
        shutil.move(path, os.path.join(os.getcwd(), 'nopdfs', filename))
        return
    else:
        # try:
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # except:
        #     print(fp.name + 'Do not provide txt conversion',
        #           'change to Tencent ocr identification')
        #     print('Start converting', fp.name, 'to image')
        #     txt = imgtotxt(convert_pdf_to_jpg(filename))
        # # except Warning:
        # #     print(fp.name, '捕获到警告', '改用腾讯ocr识别')
        # #     print('开始将', fp.name, '转换为图片')
        # #     txt = imgtotxt(convert_pdf_to_jpg(fp.name))
        #
        # #     os.remove(path)
        # #     return
        # # except AttributeError:
        # #     os.remove(path)
        # # else:
        # try:
        # 创建PDf 资源管理器 来管理共享资源
        # except PDFSyntaxError:
        #     shutil.move(path, os.path.join(os.getcwd(), 'nopdfs', filename))
        #     return
        # try:
        #     os.remove(r'./pdfs/' + codename + '/' + filename.replace(
        #         'pdf', 'txt'))
        # except FileNotFoundError:
        #     pass
        # 循环遍历列表，每次处理一个page的内容
    # except AttributeError:
    #     print(filename + 'Do not provide txt conversion',
    #           'change to Tencent ocr identification')
    #     print('Start converting', filename, 'to image')
    #     txt = imgtotxt(convert_pdf_to_jpg(filename))
    txt = ""
    try:
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
                    # with open(r'./pdfs/test.txt', 'a') as f:
                    results = x.get_text()
                    #     # print(results)
                    #     f.write(results + '\n')
                    txt += results
    except (Warning, PSEOF, PDFSyntaxError, KeyError):
        shutil.move(path, os.path.join(os.getcwd(), 'nopdfs', filename))
        return
            # for x in layout:
            #     if isinstance(x, LTTextBoxHorizontal):
            #         with open(r'./pdfs/' + codename + '/' + filename.replace(
            #                 'pdf', 'txt'), 'a') as f:
            #             results = x.get_text()
            #             # print(results)
            #             f.write(results + '\n')
        # print('转换完成:', f.name)
    # except Warning:
    #     print(filename + 'Do not provide txt conversion',
    #           'change to Tencent ocr identification')
    #     print('Start converting', filename, 'to image')
    #     txt = imgtotxt(convert_pdf_to_jpg(filename))

    CVnum = SBnum = TLnum = SLnum = QEnum = AMnum = GPnum = 0
    # CVindex = SBindex = TLindex = SLindex = QEindex = AMindex = GPindex = 0
    SB_list = list(itertools.product(SB[0], SB[1], SB[2], SB[3]))
    TL_list = list(itertools.product(TL[0], TL[1], TL[2], TL[3], TL[4]))
    SL_list = list(itertools.product(SL[0], SL[1], SL[2], SL[3], SL[4]))
    AM_list = list(itertools.product(AM[0], AM[1], AM[2], AM[3]))
    GP_list = list(itertools.product(GP[0], GP[1]))

    # file_str = open(f.name).read()
    term_non = txt.replace('\n', '')
    terms_list = re.split(u'第\w+条', term_non)
    for term in terms_list:
        if CV[0] in term or CV[1] in term:
            CVnum = 1
            # CVindex = terms_list.index(term)
        for sbw in SB_list:
            if sbw[0] in term and sbw[1] in term and sbw[2] in term and sbw[
                3] in term and SB[-1][0] not in term and SB[-1][
                1] not in term and \
                    SB[-1][
                        2] not in term:
                SBnum = 1
                break
                # SBindex = terms_list.index(term)
        for tlw in TL_list:
            if tlw[0] in term and tlw[1] in term and tlw[2] in term and tlw[
                3] in term and (
                    TL[-1][0] not in term and TL[-1][1] not in term and TL[-1][
                2] not in term):
                TLnum = 1
                break
                # TLindex = terms_list.index(term)
        for slw in SL_list:
            if slw[0] in term and slw[1] in term and slw[
                2] in term and slw[3] in term and slw[4] in term and SL[-1][
                0] not in term:
                SLnum = 1
                break
                # SLindex = terms_list.index(term)
        if QE in term:
            QEnum = 1
            # QEindex = terms_list.index(term)
        for amw in AM_list:
            if amw[0] in term and amw[1] in term and amw[
                2] in term and amw[3] in term:
                AMnum = 1
                break
                # AMindex = terms_list.index(term)
        for gpw in GP_list:
            if gpw[0] in term and gpw[1] in term and GP[-1][0] not in term:
                GPnum = 1
                break
                # GPindex = terms_list.index(term)
    print(filename, 'analysis completed')
    shutil.move(path, os.path.join(os.getcwd(), 'goodpdfs', filename))
    return filename.split('.')[0].split('_')[0], \
           filename.split('.')[0].split('_')[
               1], CVnum, SBnum, TLnum, SLnum, QEnum, AMnum, GPnum


def delpdf():
    pdfs = os.listdir('pdfs')
    codes = [code[:6] for code in pdfs if code[-3:] == 'pdf']
    # getfile = xlrd.open_workbook(XLSX)
    # table = getfile.sheet_by_index(0)
    # rows = table.nrows
    # for i in range(1, rows):
    #     cell_vlaues = table.cell_value(i, 0)
    for cn in set(codes):
        code_list = sorted([x for c, x in enumerate(pdfs) if x.find(cn) != -1])
        for i in range(len(code_list) - 1):
            if code_list[i][7:11] == code_list[i + 1][7:11]:
                min_year = min(code_list[i], code_list[i + 1])
                os.remove(os.path.join('pdfs', min_year))
                print('Multiple regulations in the same year, delete:',
                      min_year)
            # year_list = 1


# def run1():
#     dir_files = os.listdir('pdfs')
#     try:
#         os.remove(r'res.csv')
#     except:
#         pass
#     # with open("res.csv", "a") as csvfile:
#     #     writer = csv.writer(csvfile)
#     #     # 先写入columns_name
#     #     writer.writerow(
#     #         ["code", "date", "CV", "SB", 'TL', 'SL', 'QE', 'AM', 'GP'])
#     for path, dir_list, file_list in dir_files:
#         # print(path, dir_list, file_list)
#         if dir_list:
#             continue
#         else:
#             L = []
#             for file_pdf in file_list:
#                 if os.path.splitext(file_pdf)[1] == ".pdf":
#                     L.append(file_pdf)
#             codename = path.split('/')[1]
#             date_list = list(map(splitdate, L))
#             date_str = str(date_list)
#             if date_list.__len__() >= 2:
#                 new_list = []
#                 for d in date_list:
#                     if d[:4] not in str(new_list):
#                         new_list.append(d)
#                     else:
#                         test = [c for c, x in enumerate(new_list) if
#                                 x.find(d[:4]) != -1]
#                         os.remove('./pdfs/' + codename + '/' + min(
#                             [d, new_list[test[0]]]) + '.pdf')
#                         file_list.remove(min(
#                             [d, new_list[test[0]]]) + '.pdf')
#                         print('删除: ', './pdfs/' + codename + '/' + min(
#                             [d, new_list[test[0]]]) + '.pdf')
#
#             csv_ros = []
#             for filename in file_list:
#                 if filename.split('.')[1] == 'pdf':
#                     # print(codename,filename)
#                     pdf_res = parse(codename, filename)
#                     if pdf_res is not None:
#                         csv_ros.append(pdf_res)
#                         print(path + '/' + filename + ' 转换完成')
#                 else:
#                     continue
#             if csv_ros.__len__() >= 2:
#                 # csv_ros.sort(lambda x, y: cmp_to_key(x[1], y[1]))
#                 new_ros = add_ros = sorted(csv_ros, key=lambda x: x[1])
#                 for n in range(0, new_ros.__len__() - 1):
#                     diff = int(new_ros[n + 1][1][:4]) - int(
#                         new_ros[n][1][:4])
#                     if diff != 1:
#                         for d in range(diff - 1):
#                             add_ros.insert(n + d + 1, add_ros[n])
#                             add_ros[n + d + 1] = list(add_ros[n + 1])
#                             add_ros[n + d + 1][1] = str(
#                                 int(add_ros[n + d + 1][1][:4]) + 1)
#                             tuple(add_ros[n + d + 1])
#                 # writer.writerows(add_ros)
#                 # newyear_t = datetime.datetime.strptime(csv_ros[n+1][1], "%Y-%m-%d")
#                 # newyear = newyear_t + datetime.timedelta(year)
#                 # 写入多行用writerows
#                 writer.writerows(add_ros)
#             else:
#                 writer.writerow(csv_ros)
#             print(codename + ' 文件夹pdf转换txt结束')
#     print('All pdf analysis is complete!')
# 18164
def run():
    # import random  # test
    # pdf文件名
    # with open("res.csv", "w") as csvfile:
    #     writer = csv.writer(csvfile)
    #     # 先写入columns_name
    #     writer.writerow(
    #         ["code", "date", "CV", "SB", 'TL', 'SL', 'QE', 'AM', 'GP'])

    pdfs = os.listdir('pdfs')
    # pdfs = pdfs[:10]
    # pdfs = random.sample(pdfs, 20)
    # 去重后的code列表
    codes = set([code[:6] for code in pdfs if code[-3:] == 'pdf'])
    res = []
    # pdfs = ['000001_2011-01-01.pdf']
    print('Start analysis')
    for pdfname in pdfs:
        if pdfname[-3:] == 'pdf':
            # res.append(parse(pdfname))
            print('start', pdfname)
            row = parse(pdfname)
            if row is not None:
                with open("res.csv", "a") as csvfile:
                    writer = csv.writer(csvfile)
                    # 先写入columns_name
                    writer.writerow(row)
                    # writer.writerow(
                    #     ["code", "date", "CV", "SB", 'TL', 'SL', 'QE', 'AM', 'GP'])
            else:
                continue
        else:
            continue
    # # 降序
    # # res_sort = sorted(res, key=lambda x: x[1])
    # res_good = []
    # for cn in codes:
    #     code_good = code_list = sorted(
    #         [x for c, x in enumerate(res) if x[0].find(cn) != -1])
    #     if len(code_list) >= 2:
    #         for n in range(len(code_list) - 1):
    #             diff = int(code_list[n + 1][1][:4]) - int(
    #                 code_list[n][1][:4])
    #             if diff > 1:
    #                 for d in range(diff - 1):
    #                     code_good.insert(n + d + 1, code_good[n + d])
    #                     code_good[n + d + 1] = list(code_good[n + d + 1])
    #                     code_good[n + d + 1][1] = str(
    #                         int(code_good[n + d + 1][1][:4]) + 1)
    #                     tuple(code_good[n + d + 1])
    #     for r in code_good:
    #         res_good.append(r)
    # print('All pdf analysis is complete!')
    #
    # # try:
    # #     os.remove(r'res.csv')
    # # except:
    # #     pass
    # print('Start writing to res.csv')
    # with open("res.csv", "w") as csvfile:
    #     writer = csv.writer(csvfile)
    #     # 先写入columns_name
    #     writer.writerow(
    #         ["code", "date", "CV", "SB", 'TL', 'SL', 'QE', 'AM', 'GP'])
    #     writer.writerows(res_good)
    # print('Write completion')


def runall():
    delpdf()
    run()


if __name__ == '__main__':
    # pdfocr()
    # delpdf()
    runall()
