from mongoengine import *

class BroadcastMessages(Document):
    sender_uid = StringField(required = True)
    sender_name = StringField(required = True)
    message = StringField(required = True)
    timestamp = DateTimeField(required = True)

class StaffUserEntry(Document):
  email = StringField(required = True)
  hashed = StringField(required = True)

  roles = ListField(required = True)

  firstname = StringField(required = True)
  lastname = StringField(required = True)

  def full_name(self):
    return self.firstname + " " + self.lastname

  roles = ListField(required = False)