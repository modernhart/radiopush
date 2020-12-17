import requests
import json
import pyrebase
from datetime import datetime


def noquote(s):
    return s


pyrebase.pyrebase.quote = noquote


with open("./config.json") as f:
   config = json.load(f)


firebase = pyrebase.initialize_app(config["firebase"])
db = firebase.database()


def getToken(token):
    snapshot = db.child("push").order_by_child("token").equal_to(token).get()

    if (len(snapshot.each()) == 0):
        db.child("push").push({
            # "name": name,
            "token": token
        })
    return True


def getGidNum():
    r = config["radio_num"]
    current_hour = datetime.now().hour + 9
    try:
        return r[f"{current_hour}"]
    except Exception as e:
        print(f"config error {e}")


def handleData(token, name, msg, time):
    snapshot = db.child("push").order_by_child("token").equal_to(token).get()
    title = name + " (" + time + ") "
    for s in snapshot.each():
        key = s.key()
        if (len(s.val()) - 2 >= 25):
            for data in s.val():
                if (data != "token" and data != "status"):
                    db.child("push").child(key).child(data).remove()

        snapshotName = db.child("push").child(key).order_by_child("name").equal_to(name).get()
        if (len(snapshotName.each()) == 0):
            # newUser
            db.child("push").child(key).push({
                "name": name,
                "msg": msg,
                "time": time
            })
            pushNotification(token, title, msg)
        else:
            snapshotTime = db.child("push").child(key).order_by_child("time").equal_to(time).get()

            if (len(snapshotTime.each()) == 0):
                # newComment
                db.child("push").child(key).push({
                    "name": name,
                    "msg": msg,
                    "time": time
                })
                pushNotification(token, title, msg)


def setPushStatus(token, status):
    snapshot = db.child("push").order_by_child("token").equal_to(token).get()
    for s in snapshot.each():
        key = s.key()

        db.child("push").child(key).update({
            "status": status
        })


def getPushStatus(token):
    snapshot = db.child("push").order_by_child("token").equal_to(token).get()
    for s in snapshot.each():
        key = s.key()
        data = db.child("push").child(key).child("status").get()
        if(data.val() is None):
            return "off"
        else:
            return data.val()


def requestRadio(token):
    # gid 21 : 오늘아침 9시
    # gid 54 : 골든디스크 11시
    # gid 22 : 정오의 희망곡 12시
    # gid 23 : 두시의 데이트 2시
    # gid 50 : 오후의 발견 4시
    # gid 25 : 음악 캠프 6시
    # gid 26 : 꿈꾸는 라디오 8시
    # gid 27 : 푸른밤 10시

    gid = getGidNum()
    try:
        setPushStatus(token, "on")
        url = f"http://miniunit.imbc.com/List/MiniMsgList?rtype=jsonp&bid=1000584100000100000&gid={gid}&page=1&pagesize=5"
        html = requests.get(url)
        comment = json.loads(html.text)

        for list in comment["msgList"]:
            handleData(token, list["UserNm"], list["Comment"], list["RegDate"])

        print("requestRadio")

    except requests.exceptions.RequestException as error:
        print("Error: ", error)


def requestPerSecond(stop, token):
    import time
    while True:
        if stop():
            setPushStatus(token, "off")
            print("stopped")
            break
        requestRadio(token)
        time.sleep(1)


def getPushContents(token):
    snapshot = db.child("push").order_by_child("token").equal_to(token).get()
    contents = []

    for s in snapshot.each():
        key = s.key()
        snapshotTime = db.child("push").child(key).get()
        for data in snapshotTime.each():
            if (data.key() != "status" and data.key() != "token"):
                contents.append(data.val())
        return contents


def pushNotification(deviceToken, title, message):
    push = config["push_key"]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + push["serverToken"],
    }

    body = {
        'notification': {
            'title': title,
            'body': message
         },
        'to': deviceToken,
        'priority': 'high',
        #   'data': dataPayLoad,
    }
    response = requests.post("https://fcm.googleapis.com/fcm/send", headers = headers, data=json.dumps(body))
    print(response.status_code)
    print(response.json())


# requestPerSecond()
