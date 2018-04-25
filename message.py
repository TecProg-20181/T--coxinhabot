#!/usr/bin/env python3

import db
from db import Task

class Message:

    def __init__(self, message_raw):
        self.command = message_raw["text"].split(" ", 1)[0]

        if len(message_raw["text"].split(" ", 1)) > 1:
            self.msg = message_raw["text"].split(" ", 1)[1].strip()
        else:
            self.msg = ''

        self.chat = message_raw["chat"]["id"]
        self.user_name = message_raw["chat"]["first_name"]

        if message_raw != None:
            self.not_none = True
        else:
            self.not_none = False
