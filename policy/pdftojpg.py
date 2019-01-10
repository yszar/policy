from PIL import Image as Image2
from wand.image import Image
from wand.color import Color
import os


def convert_pdf_to_jpg(filename):
    end_length = len(filename.split('.')[-1]) + 1
    title = filename[0:-end_length]
    title = title.split('/')[-1]

    # resolution為解析度，background為背景顏色
    with Image(filename=filename, resolution=150,
               background=Color('White')) as img:

        # 頁數
        length = len(img.sequence)

        # 如果頁數超過1頁，生成的文件名會依次加上頁碼數
        with img.convert('png') as converted:
            path = '/Users/apple/code/spiders/policy/policy/image/%s.png' % title
            converted.save(filename=path)
    image_list = []
    if length == 1:
        path = '/Users/apple/code/spiders/policy/policy/image/%s.png' % title
        image_list.append(path)
    else:
        for i in range(0, length):
            path = '/Users/apple/code/spiders/policy/policy/image/%s-%d.png' % (title, i)
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
        # name = "%s" % ('static/local_images', name)
        jpg_list.append(name)

    return jpg_list


if __name__ == '__main__':
    convert_pdf_to_jpg('/Users/apple/code/spiders/policy/pdfs/002273_2014-07-31.pdf')