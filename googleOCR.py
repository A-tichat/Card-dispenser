import io
from time import sleep
from PIL import Image


# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types


def imgProcessing():
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    im = Image.open("./Pictures/a.jpg")
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
    # print(len())
    # for text in texts:
    #     print(text.description)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    im.close()
    return texts


print(imgProcessing()[0].description)
