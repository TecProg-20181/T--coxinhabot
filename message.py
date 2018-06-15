#!/usr/bin/env python3

import db
from db import Task

class Message:

    def __init__(self, message_raw):
        type = ''

        try:
            temp = message_raw["text"]
            type = 'text'
        except KeyError:
            pass
        try:
            temp = message_raw["voice"]
            type = 'voice'
        except KeyError:
            pass
        try:
            temp = message_raw["location"]
            type = 'location'
        except KeyError:
            pass
        try:
            temp = message_raw["image"]
            type = 'image'
        except KeyError:
            pass
        try:
            temp = message_raw["contact"]
            type = 'contact'
        except KeyError:
            pass

        if type == 'text':
            self.command = message_raw["text"].split(" ", 1)[0]

            if len(message_raw["text"].split(" ", 1)) > 1:
                self.msg = message_raw["text"].split(" ", 1)[1].strip()
            else:
                self.msg = ''
        else:
            self.command = 'other'
            self.msg = 'none'

        self.chat = message_raw["chat"]["id"]
        self.user_name = message_raw["chat"]["first_name"]

        if message_raw != None:
            self.not_none = True
        else:
            self.not_none = False
