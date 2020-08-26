import requests
import json
import urllib.request


def postAPI(action, json_data):
    url = "http://kds.nellehliving.com/api/v1/"
    api_key = "44d1836c5185a5c52e5a8f428e603f6e"
    api_params = {'action': action, 'KEY': api_key}
    response = requests.post(
        url, json=json_data, params=api_params)
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


def resetRoom(arr_data):
    res = postAPI('return', arr_data)
    print(res.text)

def sendName(name):
    title = name.index('#')
    name = name[title+1:]
    sur = name.index('##')
    print(title, sur)
    fname = name[:sur]
    lname = name[sur+2:]
    dataRoom = getRoom("fullname", fname)
    if not dataRoom:
        dataRoom = getRoom("fullname", lname)
        print(fname)
    if not dataRoom:
        dataRoom = getRoom("fullname", name.replace('##', ' '))
        print(lname)
    return dataRoom


def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)  # Python 3.x
        return True
    except:
        return False
