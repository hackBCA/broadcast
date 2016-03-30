from . import sio
from . import controllers
from flask_socketio import send, emit
from flask import request, session
import datetime
import json

@sio.on("connect")
def connect():
    print("Anotha one connected.")

@sio.on("fetch_all_broadcasts")
def fetch_broadcasts():
    return controllers.get_all_broadcasts()

@sio.on("send_message")
def send_message(message, session_cookie):
    try:
        session = controllers.deserialize(session_cookie)
    except Exception:
        return json.dumps({ "status": "error", "message": "Not authorized." })
    if (session is not None and controllers.is_authorized(session["identity.id"])):
        data = controllers.parse_sent(message, session["identity.id"])
        emit("receive_message", data, broadcast = True)
        return json.dumps({ "status": "success", "message": "Message sent." })
    else:
        return json.dumps({ "status": "error", "message": "Not authorized." })