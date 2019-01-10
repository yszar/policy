from wand.image import Image
from wand.color import Color
from PIL import Image as PI
import pyocr
import pyocr.builders
import io

def convert_pdf_to_jpg(filename):
    with Image(filename=filename, resolution=300, background=Color('White')) as img :
        print('pages = ', len(img.sequence))

        with img.convert('png') as converted:
            converted.save(filename='/Users/apple/code/spiders/policy/policy/image/page.png')


# # pyocr支持两种OCR库，由于我只安装了tesseract，只会获得tesseract
# tool = pyocr.get_available_tools()[0]
#
# # 选择要使用的语言，使用print tool.get_available_languages()列表
# lang = tool.get_available_languages()[2]
#
# # 用来保存图像和对应的文字
# req_image = []
# final_text = []
#
# # 打开pdf文件，并转为图像，替换./test.pdf
# image_pdf = Image(filename="/Users/apple/code/spiders/policy/pdfs/002241_2017-08-18.pdf", resolution=300)
# image_jpeg = image_pdf.convert('jpeg')
#
# # 把图片放到req_image中
# for img in image_jpeg.sequence:
#     img_page = Image(image=img)
#     req_image.append(img_page.make_blob('jpeg'))
#
# # 为每个图像运行OCR，识别图像中的文本
# for img in req_image:
#     txt = tool.image_to_string(
#         PI.open(io.BytesIO(img)),
#         lang=lang,
#         builder=pyocr.builders.TextBuilder()
#     )
#     final_text.append(txt)

if __name__ == '__main__':
    convert_pdf_to_jpg("/Users/apple/code/spiders/policy/pdfs/002241_2017-08-18.pdf")
