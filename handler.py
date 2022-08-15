import requests
import json
import time

URL = 'https://api.telegram.org/bot1824267774:AAGnUpKJ7s2c2Ayc5iafv9twBp0twwmJLek/'
CHAT_ID = '-1001597515035'
offset = 0
status = None


def handle(data):
    global status
    offset = set_offset()
    data = json.loads(data)
    newdata = json.dumps(data)
    send_message(newdata)
    while status == None:
        mess_text, update_id = get_update(offset)
        status = check_status(mess_text)
        time.sleep(0.5)
    return status

def set_offset():
    global offset
    url = URL + 'getUpdates'
    r = requests.get(url)
    r = r.json()
    if (r['result'] != [] ):
        offset = str(r['result'][-1]['update_id']+1)
        return offset
    return "0"


def get_update(offset):
    url = URL + 'getUpdates?offset=' + offset
    r = requests.get(url)
    r = r.json()
    if (r['result'] != [] ):
        mess_text = r['result'][-1]['channel_post']['text']
        update_id = r['result'][-1]['update_id']
        return mess_text, update_id
    return '', ''


def check_status(msg):
    if (msg.startswith('{')):
        data = json.loads(msg)
        if ("validate_status" in data):
            status = data["validate_status"]["status"]
            if status == "OK":
                return json.dumps({"validate_status": { "status": 1}})
            return json.dumps({"validate_status": { "status": 0}})


def send_message(text):
    url = URL + f"sendMessage?chat_id={CHAT_ID}&text={text}"
    requests.get(url)
