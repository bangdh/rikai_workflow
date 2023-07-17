from json import dumps, loads
import requests

def sentToMeet(text):
    url = "https://chat.googleapis.com/v1/spaces/AAAAx8uAfg8/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=H-BunJgYVnbebIKZLjotafww2myQ1t8OpPGL5umsQkA%3D"
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    payload = {"text": text}
    result = requests.post(url, data=dumps(payload), headers=headers)

def kintaiBot(text):
    url = "https://chat.googleapis.com/v1/spaces/AAAA1wofQ8o/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=brDbZjxlyttjfR1Nzs5K-BVaqKL6ycap9SC7GtpkuIE%3D"
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    payload = {"text": text}
    result = requests.post(url, data=dumps(payload), headers=headers)

def testBot(text):
    url = "https://chat.googleapis.com/v1/spaces/AAAAwWanyDE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=SzdwfSaBS2yPj_NpfZOY2L2UtEbVs6VDpV8i1jrfv_E%3D"
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    payload = {"text": text}
    result = requests.post(url, data=dumps(payload), headers=headers)

def bomBot(text):
    url = "https://chat.googleapis.com/v1/spaces/AAAANbiWKuk/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=UCJvGLUCGBRW1T6NquklNQBCCBMD5fcCnt7ySHpUoSc%3D"
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    payload = {"text": text}
    result = requests.post(url, data=dumps(payload), headers=headers)

def employeeBot(text):
    url = "https://chat.googleapis.com/v1/spaces/AAAAqKi_0OU/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=gDjDWl45Xz1tSA7W3EKGdCNeCyTptGJl92y58uw5bpI%3D"
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    payload = {"text": text}
    result = requests.post(url, data=dumps(payload), headers=headers)