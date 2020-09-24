from flask import Flask, request, jsonify
from PyWeChatSpy import WeChatSpy
from PyWeChatSpy.command import MESSAGE, WECHAT_LOGIN
import requests
import toml


with open("config.toml", "r") as rf:
    CONFIG = toml.load(rf)
SYNC_HOST = CONFIG["system"]["host"]


def parser(data):
    if data.type == WECHAT_LOGIN:
        post_data = {
            "nickname": data.login_info.nickname,
            "wechatid": data.login_info.wechatid,
            "wxid": data.login_info.wxid,
            "port": data.port
        }
        requests.post(f"{SYNC_HOST}?mod=wxrobot&ac=userport", json=post_data)
    elif data.type == MESSAGE:
        for message in data.message_list.message:
            if message.type == 1:
                post_data = {
                    "type": 1,
                    "wxid1": message.wxid1,
                    "wxid2": message.wxid2,
                    "content": message.content,
                    "self": message.self,
                    "port": data.port
                }
                requests.post(f"{SYNC_HOST}?mod=wxrobot", json=post_data)


app = Flask(__name__)
spy = WeChatSpy(parser=parser)


@app.route("/sendMessage", methods=["POST"])
def send_message():
    if not (message_type := request.json.get("type")):
        return jsonify({"success": 0, "msg": "未找到参数type"})
    elif not (port := request.json.get("port")):
        return jsonify({"success": 0, "msg": "未找到参数port"})
    if message_type == 1:
        if not (wxid1 := request.json.get("wxid1")):
            return jsonify({"success": 0, "msg": "未找到参数wxid1"})
        elif not (content := request.json.get("content")):
            return jsonify({"success": 0, "msg": "未找到参数content"})
        wxid2 = request.json.get("wxid2") or ""
        spy.send_text(wxid1, content, wxid2, port=port)
    return jsonify({"success": 1, "msg": "消息发送成功"})


if __name__ == '__main__':
    app.run(host="0.0.0.0")

