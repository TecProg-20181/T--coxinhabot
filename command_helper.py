#!/usr/bin/env python3

import db
from db import Task

from taskbot import *
from help import Help

def command_handler(message):
    status = ['/todo', '/doing', '/done']

    if message.command == '/new':
        command_new(message.chat, message.msg)

    elif message.command == '/rename':
        command_rename(message.msg, message.user_name, message.chat)

    elif message.command == '/duplicate':
        command_duplicate(message.msg, message.user_name, message.chat)

    elif message.command == '/delete':
        command_delete(message.msg, message.user_name, message.chat)

    elif message.command in status:
        command_status(message.msg, message.user_name, message.chat, message.command)

    elif message.command == '/list':
        command_list(message.chat)

    elif message.command == '/dependson':
        command_dependson(message.msg, message.user_name, message.chat)

    elif message.command == '/priority':
        command_priotiry(message.msg, message.user_name, message.chat)

    elif message.command == '/start':
        helper = Help();
        send_message("Welcome! Here is a list of things you can do.", message.chat)
        send_message(helper.get_help(), message.chat)
    elif message.command == '/help':
        helper = Help();
        send_message("Here is a list of things you can do.", message.chat)
        send_message(helper.get_help(), message.chat)
    elif message.command == '/showPriority':
        command_show_priority(message.chat)    
    else:
        send_message("I'm sorry " + message.user_name + ". I'm afraid I can't do that.", message.chat)


def command_new(chat, msg):
    task = Task(chat=chat, name=msg, status='TODO', dependencies='', parents='', priority='')
    db.session.add(task)
    db.session.commit()
    send_message("New task *TODO* [[{}]] {}".format(task.id, task.name), chat)

def command_rename(msg, user_name, chat):
    text = ''
    if msg != '':
        if len(msg.split(' ', 1)) > 1:
            text = msg.split(' ', 1)[1]
        msg = msg.split(' ', 1)[0]

    if not msg.isdigit():
        send_message("Hey " + user_name + ", you must inform the task id", chat)
    else:
        task_id = int(msg)
        query = db.session.query(Task).filter_by(id=task_id, chat=chat)
        try:
            task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            send_message("_404_ Task {} not found x.x".format(task_id), chat)
            return

        if text == '':
            send_message("You want to modify task {}, but you didn't provide any new text".format(task_id), chat)
            return

        old_text = task.name
        task.name = text
        db.session.commit()
        send_message("Task {} redefined from {} to {}".format(task_id, old_text, text), chat)

def command_list(chat):
    a = ''

    a += '\U0001F4CB Task List\n'
    query = db.session.query(Task).filter_by(parents='', chat=chat).order_by(Task.id)
    for task in query.all():
        icon = '\U0001F195'
        if task.status == 'DOING':
            icon = '\U000023FA'
        elif task.status == 'DONE':
            icon = '\U00002611'

        a += '[[{}]] {} {}\n'.format(task.id, icon, task.name)
        a += deps_text(task, chat)

    send_message(a, chat)
    a = ''

    a += '\U0001F4DD _Status_\n'
    query = db.session.query(Task).filter_by(status='TODO', chat=chat).order_by(Task.id)
    a += '\n\U0001F195 *TODO*\n'
    for task in query.all():
        a += '[[{}]] {}\n'.format(task.id, task.name)
    query = db.session.query(Task).filter_by(status='DOING', chat=chat).order_by(Task.id)
    a += '\n\U000023FA *DOING*\n'
    for task in query.all():
        a += '[[{}]] {}\n'.format(task.id, task.name)
    query = db.session.query(Task).filter_by(status='DONE', chat=chat).order_by(Task.id)
    a += '\n\U00002611 *DONE*\n'
    for task in query.all():
        a += '[[{}]] {}\n'.format(task.id, task.name)

    send_message(a, chat)

def command_duplicate(msg, user_name, chat):
    if not msg.isdigit():
        send_message("Hey " + user_name + ", you must inform the task id", chat)
    else:
        task_id = int(msg)
        query = db.session.query(Task).filter_by(id=task_id, chat=chat)
        try:
            task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            send_message("_404_ Task {} not found x.x".format(task_id), chat)
            return

        dtask = Task(chat=task.chat, name=task.name, status=task.status, dependencies=task.dependencies,
                     parents=task.parents, priority=task.priority, duedate=task.duedate)
        db.session.add(dtask)

        for t in task.dependencies.split(',')[:-1]:
            qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
            t = qy.one()
            t.parents += '{},'.format(dtask.id)

        db.session.commit()
        send_message("New task *TODO* [[{}]] {}".format(dtask.id, dtask.name), chat)

def command_delete(msg, user_name, chat):
    if not msg.isdigit():
        send_message("Hey " + user_name + ", you must inform the task id", chat)
    else:
        task_id = int(msg)
        query = db.session.query(Task).filter_by(id=task_id, chat=chat)
        try:
            task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            send_message("_404_ Task {} not found x.x".format(task_id), chat)
            return
        for t in task.dependencies.split(',')[:-1]:
            qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
            t = qy.one()
            t.parents = t.parents.replace('{},'.format(task.id), '')
        db.session.delete(task)
        db.session.commit()
        send_message("Task [[{}]] deleted".format(task_id), chat)

def command_status(msg, user_name, chat, command):
    if not msg.isdigit():
        send_message("Hey " + user_name + ", you must inform the task id", chat)
    else:
        task_id = int(msg)
        query = db.session.query(Task).filter_by(id=task_id, chat=chat)
        try:
            task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            send_message("_404_ Task {} not found x.x".format(task_id), chat)
            return
        if command == '/todo':
            status = 'TODO'
        elif command == '/doing':
            status = 'DOING'
        elif command == '/done':
            status = 'DONE'
        task.status = status
        db.session.commit()
        send_message("*" + status + "* task [[{}]] {}".format(task.id, task.name), chat)

def command_dependson(msg, user_name, chat):
    text = ''
    if msg != '':
        if len(msg.split(' ', 1)) > 1:
            text = msg.split(' ', 1)[1]
        msg = msg.split(' ', 1)[0]

    if not msg.isdigit():
        send_message("Hey " + user_name + ", you must inform the task id", chat)
    else:
        task_id = int(msg)
        query = db.session.query(Task).filter_by(id=task_id, chat=chat)
        try:
            task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            send_message("_404_ Task {} not found x.x".format(task_id), chat)
            return

        if text == '':
            for i in task.dependencies.split(',')[:-1]:
                i = int(i)
                q = db.session.query(Task).filter_by(id=i, chat=chat)
                t = q.one()
                t.parents = t.parents.replace('{},'.format(task.id), '')

            task.dependencies = ''
            send_message("Dependencies removed from task {}".format(task_id), chat)
        else:
            for depid in text.split(' '):
                if not depid.isdigit():
                    send_message("All dependencies ids must be numeric, and not {}".format(depid), chat)
                else:
                    depid = int(depid)
                    query = db.session.query(Task).filter_by(id=depid, chat=chat)
                    try:
                        taskdep = query.one()
                        taskdep.parents += str(task.id) + ','
                    except sqlalchemy.orm.exc.NoResultFound:
                        send_message("_404_ Task {} not found x.x".format(depid), chat)
                        continue

                    deplist = task.dependencies.split(',')
                    if str(depid) not in deplist:
                        task.dependencies += str(depid) + ','

        db.session.commit()
        send_message("Task {} dependencies up to date".format(task_id), chat)

def command_priotiry(msg, user_name, chat):
    text = ''
    if msg != '':
        if len(msg.split(' ', 1)) > 1:
            text = msg.split(' ', 1)[1]
        msg = msg.split(' ', 1)[0]

    if not msg.isdigit():
        send_message("Hey " + user_name + ", you must inform the task id", chat)
    else:
        task_id = int(msg)
        query = db.session.query(Task).filter_by(id=task_id, chat=chat)
        try:
            task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            send_message("_404_ Task {} not found x.x".format(task_id), chat)
            return

        if text == '':
            task.priority = ''
            send_message("_Cleared_ all priorities from task {}".format(task_id), chat)
        else:
            if text.lower() not in ['high', 'medium', 'low']:
                send_message("The priority *must be* one of the following: high, medium, low", chat)
            else:
                task.priority = text.lower()
                send_message("*Task {}* priority has priority *{}*".format(task_id, text.lower()), chat)
        db.session.commit()

def command_show_priority(chat):
    a = ''

    a += '\U0001F4DD _Status_\n'
    query = db.session.query(Task).filter_by(priority='low', chat=chat).order_by(Task.id)
    a += '\n\U0001F195 *low*\n'
    for task in query.all():
        a += '[[{}]] {}\n'.format(task.id, task.name)
    query = db.session.query(Task).filter_by(priority='medium', chat=chat).order_by(Task.id)
    a += '\n\U000023FA *medium*\n'
    for task in query.all():
        a += '[[{}]] {}\n'.format(task.id, task.name)
    query = db.session.query(Task).filter_by(priority='high', chat=chat).order_by(Task.id)
    a += '\n\U00002611 *high*\n'
    for task in query.all():
        a += '[[{}]] {}\n'.format(task.id, task.name)

    send_message(a, chat)