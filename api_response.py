import requests
import json


def postAPI(action, json_data):
    try:
        url = "http://kds.nellehliving.com/api/v1/"
        api_key = "44d1836c5185a5c52e5a8f428e603f6e"
        api_params = {'action': action, 'KEY': api_key}
        response = requests.post(
            url, json=json_data, params=api_params, timeout=10)
        return response.text
    except requests.Timeout:
        return 'timeout'
    except requests.ConnectionError:
        return 'connectionError'


def getRoom(mytype, value):
    switcher = {
        "passport": "1",
        "cid": "2",
        "password": "3",
        "fullname": "4"
    }
    json_data = {'type': switcher.get(mytype, '0'), 'value': value}
    res = postAPI('check', json_data)
    if (res == 'timeout' or res == 'connectionError'):
        return json.loads("")
    else:
        return json.loads(res)


def resetRoom(arr_data):
    res = postAPI('return', arr_data)
    print(res.text)
