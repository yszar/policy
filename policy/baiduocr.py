# coding=utf-8
from __future__ import division

from io import StringIO
from io import BytesIO
import math
from wand.image import Image
# 这里我起了个别名
from PIL import Image as PImage

# 百度OCR最大长度
bai_du_ocr_max = 4096


# 主要方法
def convert(file_name, target_width=1500):
    buf = StringIO()
    try:
        with Image(filename=file_name) as img:
            image_page_num = len(img.sequence)

            # PDF里面只有一张图片
            if image_page_num == 1:
                # 获取最终图片宽高
                target_width, target_height = _get_one_info(target_width,
                                                            img.width,
                                                            img.height)

                # 缩放，文档上说比resize速度快
                img.sample(target_width, target_height)

                # 如果最终高度大于百度最大高度，则crop
                if target_height > bai_du_ocr_max:
                    img.crop(0, 0, target_width, bai_du_ocr_max)

                # img.save(filename='%s.jpg' % (str(int(time.time())) + '_' + str(img.width)))
                result = img.make_blob('png')

                # 下面是准备二值化，发现总体速度还不如直接传给百度
                # paste_image = PImage.open(StringIO.StringIO(img.make_blob('jpg')))
                # paste_image = paste_image.convert("L")
                # paste_image.show()
                # d = StringIO.StringIO()
                # paste_image.save(d, 'JPEG')
                # result = d.getvalue()

            # PDF里面有一张以上图片
            else:
                # 多张时，获取最终宽高、拼接页数
                target_width, target_height, page_num = _get_more_info(
                    target_width, img.width, img.height, image_page_num
                )

                # 生成粘贴的背景图 (测试多次，发现L比RGB快)
                paste_image = PImage.new('L', (target_width, target_height))

                # 拼接图片
                for i in range(0, page_num):
                    image = Image(image=img.sequence[i])
                    # 计算一张图的高度
                    one_img_height = int(target_height / page_num)
                    # 缩放
                    image.sample(target_width, one_img_height)
                    # 将wand库文件转成PIL库文件
                    pasted_image = PImage.open(
                        BytesIO(image.make_blob('png')))
                    # 将图片粘贴到背景图
                    paste_image.paste(pasted_image, (0, one_img_height * i))

                # 如果最终高度大于百度最大高度，则crop
                if target_height > bai_du_ocr_max:
                    paste_image = paste_image.crop(
                        (0, 0, target_width, bai_du_ocr_max))

                # 从内存中读取文件
                d = BytesIO()
                # 这里是JPEG不是JPG
                paste_image.save(d, 'png')
                result = d.getvalue()
                # paste_image.save('%s.jpg' % (str(int(time.time())) + '_' + str(img.width)))
                # 测试的时候可以打开
                # paste_image.show()
    except Exception as e:
        result = False
    return result


# 一张时获取宽高,如果图片宽度大于我们想要的宽度，则等比缩放图片高度
def _get_one_info(target_width, img_width, img_height):
    if img_width > target_width:
        ratio = target_width / img_width
        target_height = int(ratio * img_height)
    else:
        target_width = img_width
        target_height = img_height
    return target_width, target_height


# 多张时获取宽高和拼接页数
def _get_more_info(target_width, img_width, img_height, image_page_num):
    one_width, one_height = _get_one_info(target_width, img_width, img_height)
    if one_height < bai_du_ocr_max:
        # 百度最大高度除以每张图高度，向上取整，即拼接图片的数量
        num = int(math.ceil(bai_du_ocr_max / one_height))
        # 取拼接数和总页数的最小值
        page_num = min(num, image_page_num)
        return one_width, one_height * page_num, page_num
    else:
        return one_width, one_height, 1  # 1页


# 调试时候用
def _ocr(content):
    # '{"refresh_token":"25.e2d16cfec7af44e90b265a22ab9f1abe.315360000.1862389683.282335-15384744","expires_in":2592000,"session_key":"9mzdDFQd\/bhxTQ16HQKkj0dT+82aKHFSNXliS26qicasXm8CDEeXgrBwqxv8PzTYtssirSsnc33D8wVguBrCyTUCi2Sf7g==","access_token":"24.7a72e40b85a0b1a66ac91e5eb6458a0e.2592000.1549621683.282335-15384744","scope":"public vis-ocr_ocr brain_ocr_scope brain_ocr_general brain_ocr_general_basic brain_ocr_general_enhanced vis-ocr_business_license brain_ocr_webimage brain_all_scope brain_ocr_idcard brain_ocr_driving_license brain_ocr_vehicle_license vis-ocr_plate_number brain_solution brain_ocr_plate_number brain_ocr_accurate brain_ocr_accurate_basic brain_ocr_receipt brain_ocr_business_license brain_solution_iocr brain_ocr_handwriting brain_ocr_vat_invoice brain_numbers brain_ocr_train_ticket brain_ocr_taxi_receipt wise_adapt lebo_resource_base lightservice_public hetu_basic lightcms_map_poi kaidian_kaidian ApsMisTest_Test\u6743\u9650 vis-classify_flower lpq_\u5f00\u653e cop_helloScope ApsMis_fangdi_permission smartapp_snsapi_base iop_autocar oauth_tp_app smartapp_smart_game_openapi oauth_sessionkey smartapp_swanid_verify smartapp_opensource_openapi","session_secret":"8d032eecf2caf4382472c30339e54757"}'
    url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token=25.e2d16cfec7af44e90b265a22ab9f1abe.315360000.1862389683.282335-15384744'
    img = base64.b64encode(content)
    params = {"image": img}
    params = urllib.urlencode(params)

    request = urllib.Request(url, params)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    response = urllib.urlopen(request)
    content = response.read()
    # print content
    dict_content = json.loads(content)
    text = "\n".join(map(lambda x: x["words"], dict_content["words_result"]))
    return text


# 调试时候用
def _write_file(path, data, type="w"):
    try:
        f = open(path, '%sb' % type)
    except:
        f = open(path.encode("utf-8"), '%sb' % type)
    f.write(data)
    f.close()


# 调试时候用
if __name__ == '__main__':
    import sys
    import base64
    import json
    import urllib
    # import urllib3
    import time

    start = time.time()
    # source_file = sys.argv[1]
    ret = convert('/Users/apple/code/spiders/policy/pdfs/002241_2017-08-18.pdf', 1500)
    end = time.time()
    # 这里我统一保存下文件，方便打开观察
    _write_file(str(end) + '.png', ret)
    if ret:
        text = _ocr(ret)
    end_parse = time.time()
    print('____________________________________________')
    print(end - start)
    print(end_parse - end)
    print('+++++++++++++++++++++++++++++++++++++++++++++')
    print(text)
