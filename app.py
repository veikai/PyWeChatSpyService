from flask import Flask, request, jsonify, Response
from PyWeChatSpy import WeChatSpy
from PyWeChatSpy.command import MESSAGE, WECHAT_LOGIN, LOGIN_INFO
from uuid import uuid4
import requests
import base64
import toml
import os


with open("config.toml", "r") as rf:
    CONFIG = toml.load(rf)
SYNC_HOST = CONFIG["system"]["host"]
wechatid2port = dict()
port2wechatid = dict()


def parser(data):
    if data.type == WECHAT_LOGIN:
        spy.get_login_info(port=data.port)
    elif data.type == LOGIN_INFO:
        wechatid2port[data.login_info.wechatid] = data.port
        port2wechatid[data.port] = data.login_info.wechatid
    elif data.type == MESSAGE:
        for message in data.message_list.message:
            if message.type == 1:
                post_data = {
                    "type": 1,
                    "wxid1": message.wxid1,
                    "wxid2": message.wxid2,
                    "content": message.content,
                    "self": message.self,
                    "wechatid": port2wechatid.get(data.port)
                }
                requests.post(f"{SYNC_HOST}?mod=wxrobot", json=post_data)
            elif message.type == 3:
                file_name = "{}.jpg".format(uuid4().__str__().replace("-", ""))
                with open(os.path.join("images", file_name), "wb") as wf:
                    wf.write(base64.b64decode(message.content))
                post_data = {
                    "type": 3,
                    "wxid1": message.wxid1,
                    "wxid2": message.wxid2,
                    "content": file_name,
                    "self": message.self,
                    "wechatid": port2wechatid.get(data.port)
                }
                requests.post(f"{SYNC_HOST}?mod=wxrobot", json=post_data)


app = Flask(__name__)
spy = WeChatSpy(parser=parser)


@app.route("/sendMessage", methods=["POST"])
def send_message():
    if not (message_type := request.json.get("type")):
        return jsonify({"success": 0, "msg": "未找到参数type"})
    elif not (wechatid := request.json.get("wechatid")):
        return jsonify({"success": 0, "msg": "未找到参数wechatid"})
    if not (port := wechatid2port.get(wechatid)):
        return jsonify({"success": 0, "msg": f"根据微信号{wechatid}未找到对应port"})
    if message_type == 1:
        if not (wxid1 := request.json.get("wxid1")):
            return jsonify({"success": 0, "msg": "未找到参数wxid1"})
        elif not (content := request.json.get("content")):
            return jsonify({"success": 0, "msg": "未找到参数content"})
        wxid2 = request.json.get("wxid2") or ""
        spy.send_text(wxid1, content, wxid2, port=port)
    return jsonify({"success": 1, "msg": "消息发送成功"})


@app.route("/img/<img>", methods=["GET"])
def get_image(img):
    file_path = os.path.join("images", img)
    if not os.path.exists(file_path):
        return jsonify({"success": 0, "msg": "图片不存在"})
    with open(file_path, "rb") as ir:
        image = ir.read()
    return Response(image, mimetype="image/jpeg")


if __name__ == '__main__':
    app.run(host="0.0.0.0")

