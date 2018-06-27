#!/usr/bin/env python3
import db
import pip
from db import Task
from taskbot import *
from help import Help
from command import Command


def command_handler(message):
    status = ['/todo', '/doing', '/done']
    command_bot = Command()

    if message.command == '/new':
        command_bot.command_new(message.chat, message.msg)

    elif message.command == '/rename':
        command_bot.command_rename(message.msg, message.user_name, message.chat)

    elif message.command == '/duplicate':
        command_bot.command_duplicate(message.msg, message.user_name, message.chat)

    elif message.command == '/delete':
        command_bot.command_delete(message.msg, message.user_name, message.chat)

    elif message.command in status:
        command_bot.command_status(message.msg, message.user_name, message.chat, message.command)

    elif message.command == '/list':
        command_bot.command_list(message.chat)

    elif message.command == '/dependson':
        command_bot.command_dependson(message.msg, message.user_name, message.chat)

    elif message.command == '/priority':
        command_bot.command_priotiry(message.msg, message.user_name, message.chat)

    elif message.command == '/start':
        helper = Help()
        send_message("Welcome! Here is a list of things you can do.", message.chat)
        send_message(helper.get_help(), message.chat)
    elif message.command == '/help':
        helper = Help()
        send_message("Here is a list of things you can do.", message.chat)
        send_message(helper.get_help(), message.chat)
    elif message.command == '/showPriority':
        command_bot.command_show_priority(message.chat)

    else:
        send_message("I'm sorry " + message.user_name + ". I'm afraid I can't do that.", message.chat)
