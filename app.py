from flask import Flask, request, jsonify
from crawling_data import getToken, getPushStatus, getPushContents
from radioPush import radioThread
app = Flask(__name__)


t = None
threads = []


@app.route('/')
def index():
    return "home"


@app.route('/post/token', methods=['POST'])
def postToken():
    jsonData = request.get_json()
    isToken = getToken(jsonData["token"])
    if isToken:
        return jsonify({"user": True})


@app.route('/push/start', methods=['POST'])
def startPush():
    global t
    jsonData = request.get_json()
    t = radioThread(jsonData["token"])
    t.start()
    threads.append(t)
    return "start"


@app.route('/push/stop', methods=['POST'])
def stopPush():
    for trd in threads:
        jsonData = request.get_json()
        if (trd.getName() == jsonData["token"]):
            trd.stopRadio()
    return "stop"


@app.route('/push/status', methods=['POST'])
def getStatus():
    jsonData = request.get_json()
    status = getPushStatus(jsonData["token"])
    contents = getPushContents(jsonData["token"])
    return jsonify({"status": status, "contents": contents})


if __name__ == "__main__":
    app.run(use_reloader=False)
