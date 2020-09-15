import io
import os
from PIL import Image
from passportDecode import passportScan

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types


def imgProcessing(path):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    im = Image.open(path)
    width, height = im.size
    roiImg = im.crop((0, 11*height/16, width, height))
    roiImg.show()
    imgByteArr = io.BytesIO()
    roiImg.save(imgByteArr, format='PNG')
    image = types.Image(content=imgByteArr.getvalue())

    # Performs label detection on the image file
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # print('Texts:')
    # for text in texts:
    #     print(text.description)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    im.close()
    return texts[0].description


def mrzScan(pathImg):
    code = imgProcessing(pathImg)
    p1 = passportScan(code)
    # os.remove(pathImg)

    # if scan pass
    p1.detail()
    # print(p1.__dict__)
    return p1
