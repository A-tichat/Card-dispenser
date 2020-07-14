import requests
import json


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
