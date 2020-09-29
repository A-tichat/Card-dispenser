import requests
import json
import os


def postAPI(action, json_body):
    url = "http://kds.nellehliving.com/api/v1/"
    api_key = "44d1836c5185a5c52e5a8f428e603f6e"
    api_params = {'action': action, 'KEY': api_key}
    response = requests.post(
        url, json=json_body, params=api_params)
    return response.text


def getRoom(mytype, value):
    switcher = {
        "passport": "1",
        "cid": "2",
        "password": "3",
        "fullname": "4"
    }
    json_data = {'type': switcher.get(mytype, '0'), 'value': value}
    return json.loads(postAPI('check', json_data))


def resetRoom(data_type, rooms, data, pathImg=""):
    slots = list()
    for i in rooms:
        slots.append({"slot": i['slot']})
    res = postAPI('return', slots)
    if (data_type == "id_card"):
        postImg(bookNum=rooms[0]["customer_booking"],
                cardId=data, path=pathImg)
    if (data_type == "passport"):
        postImg(bookNum=rooms[0]["customer_booking"],
                passportId=data, path=pathImg)
    # print(res)

# function split customer name


def getRoomFromName(name):
    title = name.index('#')
    name = name[title+1:]
    sur = name.index('##')
    # print(title, sur)
    fname = name[:sur]
    lname = name[sur+2:]
    dataRoom = getRoom("fullname", fname)
    if not dataRoom:
        dataRoom = getRoom("fullname", lname)
        # print(fname)
    if not dataRoom:
        dataRoom = getRoom("fullname", name.replace('##', ' '))
        # print(lname)
    return dataRoom


def postImg(bookNum="", cardId="", passportId="", path=""):
    try:
        if path:
            img_file = open(path, 'rb')
            uploadUrl = "http://kds.nellehliving.com/passport/"
            cus_img = {'img_passport': img_file}
            cus_data = {'booking_number': bookNum,
                        "passport": passportId, 'id_card': cardId}
            response = requests.post(uploadUrl, data=cus_data, files=cus_img)
            # print(response.text)
            os.remove(path)
        else:
            uploadUrl = "http://kds.nellehliving.com/passport/"
            cus_data = {'booking_number': bookNum, 'id_card': cardId}
            response = requests.post(uploadUrl, data=cus_data, files=cus_img)
    except Exception as e:
        if path:
            img_file.close()
        print("fail", e)
