from . import CONFIG, app
from . import models
import datetime
import json
from mongoengine.errors import ValidationError
from bson.objectid import ObjectId
from bson.errors import InvalidId
from hashlib import sha1
from flask.sessions import session_json_serializer
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature
import pytz

def utc_to_local(utc_dt):
    local_tz = pytz.timezone("US/Eastern")
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def get_all_broadcasts():
    broadcasts = models.BroadcastMessages.objects()

    json_broadcasts = [
        {
            "id": str(broadcast["id"]),
            "sender_name": choose_sender_name(broadcast["sender_name"]),
            "message": broadcast["message"],
            "timestamp": broadcast["timestamp"].timestamp()
        } for broadcast in broadcasts
    ]

    json_broadcasts = sorted(
        json_broadcasts, 
        key = lambda k: k["timestamp"]
    )
    for j in json_broadcasts:
        j["timestamp"] = parse_timestamp(j["timestamp"])
    return json_broadcasts

def choose_sender_name(name):
    return name if CONFIG["SENDER_PERSONAL_NAME"] else CONFIG["SENDER_NAME"]

def parse_timestamp(timestamp):
    return utc_to_local(
        datetime.datetime.fromtimestamp(
            timestamp
        )
    ).strftime("%-m/%-d/%Y %-I:%M %p")

def deserialize(session):
    for key in CONFIG["DESERIALIZE_KEYS"]:
        try:
            s = URLSafeTimedSerializer(
                key, salt = "cookie-session",
                serializer = session_json_serializer,
                signer_kwargs = {"key_derivation": "hmac", "digest_method": sha1}
            )
            session_data = s.loads(session)
            return session_data
        except BadTimeSignature:
            pass # try the next one
    return None

def is_authorized(uid):
    try:
        uid = ObjectId(uid)
    except InvalidId:
        return False

    user = models.StaffUserEntry.objects(id = uid)
    if len(user) != 1:
        return False
    if "broadcast" in user[0].roles or "admin" in user[0].roles:
        return True
    return False

def get_name_from_uid(uid):
    uid = ObjectId(uid)
    user = models.StaffUserEntry.objects(id = uid)[0]
    return user.full_name()

def save_broadcast(uid, name, message, timestamp):
    broadcast = models.BroadcastMessages(
        sender_uid = uid,
        sender_name = name,
        message = message,
        timestamp = timestamp
    )
    broadcast.save()
    return broadcast.id

def parse_sent(message, uid):
    timestamp = datetime.datetime.now()
    sender_name = get_name_from_uid(uid)
    oid = save_broadcast(uid, sender_name, message, str(timestamp))
    data = {
        "id": str(oid),
        "sender_name": choose_sender_name(sender_name),
        "message": message,
        "timestamp": parse_timestamp(timestamp.timestamp())
    }
    return data