#!/usr/bin/env python3

import db
from db import Task


class Message:

    def __init__(self, message_raw):

        if 'text' in message_raw:
            message_type = message_raw["text"]
            type = 'text'

        elif 'voice' in message_raw:
            message_type = message_raw["voice"]
            type = 'voice'

        elif 'location' in message_raw:
            message_type = message_raw["location"]
            type = 'location'

        elif 'image' in message_raw:
            message_type = message_raw["image"]
            type = 'image'

        elif 'photo' in message_raw:
            message_type = message_raw["photo"]
            type = 'photo'

        elif 'contact' in message_raw:
            message_type = message_raw["contact"]
            type = 'contact'

        elif 'document' in message_raw:
            message_type = message_raw["document"]
            type = 'document'

        elif 'sticker' in message_raw:
            message_type = message_raw["sticker"]
            type = 'sticker'

        else:
            pass

        if type == 'text':
            self.command = message_type.split(" ", 1)[0]

            if len(message_type.split(" ", 1)) > 1:
                self.msg = message_type.split(" ", 1)[1].strip()
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
