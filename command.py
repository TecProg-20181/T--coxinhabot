import db
from db import Task 
import json
import requests
import keepLoginGithub
from taskbot import *
from datetime import datetime
from contracts import contract, new_contract


class Command(object):

    new_contract('validate_msg', lambda msg: isinstance(msg, str) and len(msg)>=2)
    @contract(chat='int, > 1', msg='validate_msg')
    def command_new(self, chat, msg):

        duedate = self.get_duedate(msg)

        if isinstance(duedate, str):
            task = Task(chat=chat, name=msg, status='TODO', dependencies='', parents='', priority='')
            self.create_issues_in_github(msg, chat)
        else:
            task = Task(chat=chat, name=msg[:-10], status='TODO', dependencies='', parents='', priority='', duedate=duedate)
            self.create_issues_in_github(msg[:-10], chat)

        db.session.add(task)
        db.session.commit()
        send_message("New task *TODO* [[{}]] {}, data de entrega {}".format(task.id, task.name, task.duedate), chat)

    
    new_contract('validate_user_name', lambda user_name: isinstance(user_name, str) and len(user_name)>=2)
    @contract(chat='int, > 1', msg='validate_msg', user_name='validate_user_name')    
    def command_rename(self, msg, user_name, chat):
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

            duedate = self.get_duedate(text)
            if isinstance(duedate, str):
                task.name = text
            else:
                task.name = text[:-10]
                task.duedate = duedate
            print(isinstance(chat, int))    
            db.session.commit()
            send_message("Task {} redefined from {} to {}, data entrega {}".format(task_id, old_text, task.name, task.duedate), chat)

    @contract(chat='int, > 1')        
    def command_list(self, chat):
        a = ''

        a += '\U0001F4CB Task List\n'
        query = db.session.query(Task).filter_by(parents='', chat=chat).order_by(Task.id)
        for task in query.all():
            icon = '\U0001F195'
            if task.status == 'DOING':
                icon = '\U000023FA'
            elif task.status == 'DONE':
                icon = '\U00002611'

            a += '[[{}]] {} {}, data entrega {}\n'.format(task.id, icon, task.name, task.duedate)
            a += deps_text(task, chat)

        send_message(a, chat)
        a = ''

        a += '\U0001F4DD _Status_\n'
        query = db.session.query(Task).filter_by(status='TODO', chat=chat).order_by(Task.id)
        a += '\n\U0001F195 *TODO*\n'
        for task in query.all():
            a += '[[{}]] {}, data entrega {}\n'.format(task.id, task.name, task.duedate)
        query = db.session.query(Task).filter_by(status='DOING', chat=chat).order_by(Task.id)
        a += '\n\U000023FA *DOING*\n'
        for task in query.all():
            a += '[[{}]] {}, data entrega {}\n'.format(task.id, task.name, task.duedate)
        query = db.session.query(Task).filter_by(status='DONE', chat=chat).order_by(Task.id)
        a += '\n\U00002611 *DONE*\n'
        for task in query.all():
            a += '[[{}]] {}, entregue na data {}\n'.format(task.id, task.name, task.duedate)

        send_message(a, chat)

    @contract(chat='int, > 1', msg='validate_msg', user_name='validate_user_name')    
    def command_duplicate(self, msg, user_name, chat):
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

    @contract(chat='int, > 1', msg='validate_msg', user_name='validate_user_name')
    def command_delete(self, msg, user_name, chat):
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

    new_contract('validate_command', lambda command: isinstance(command, str) and len(command) >= 4)
    @contract(chat='int, > 1', msg='validate_msg', user_name='validate_user_name', command='validate_command')
    def command_status(self, msg, user_name, chat, command):
        list_id = msg.split(" ")
        if not msg[0].isdigit():
            send_message("Hey " + user_name + ", you must inform the task id", chat)
        else:
            for id in list_id:
                task_id = int(id)
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

    @contract(chat='int, > 1', msg='validate_msg', user_name='validate_user_name')
    def command_dependson(self, msg, user_name, chat):
        text = ''
        if msg != '':
            if len(msg.split(' ', 1)) > 1:
                text = msg.split(' ', 1)[1]
            msg = msg.split(' ', 1)[0]

        if not msg.isdigit():
            send_message("Hey " + user_name + ", you must inform the task id", chat)
        else:
            updated_task = True
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

                            if self.check_parent(task, taskdep.id, chat):
                                taskdep.parents += str(task.id) + ','
                                updated_task = True
                                deplist = task.dependencies.split(',')
                                if str(depid) not in deplist:
                                    task.dependencies += str(depid) + ','
                            else:
                                send_message("Sorry " + user_name + ", this task already depends on another task.", chat)
                                updated_task = False

                        except sqlalchemy.orm.exc.NoResultFound:
                            send_message("_404_ Task {} not found x.x".format(depid), chat)
                            updated_task = False
                            continue

            db.session.commit()
            if updated_task:
                send_message("Task {} dependencies up to date".format(task_id), chat)

    @contract(chat='int, > 1', msg='validate_msg', user_name='validate_user_name')
    def command_priotiry(self, msg, user_name, chat):
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
                    Message.send_message("The priority *must be* one of the following: high, medium, low", chat)
                else:
                    task.priority = text.lower()
                    send_message("*Task {}* priority has priority *{}*".format(task_id, text.lower()), chat)
            db.session.commit()

    @contract(chat='int, > 1')
    def command_show_priority(self, chat):
        a = ''

        a += '\U0001F4DD _Status_\n'
        query = db.session.query(Task).filter_by(priority='low', chat=chat).order_by(Task.id)
        a += '\n *low*\n'
        for task in query.all():
            a += '[[{}]] {}\n'.format(task.id, task.name)
        query = db.session.query(Task).filter_by(priority='medium', chat=chat).order_by(Task.id)
        a += '\n *medium*\n'
        for task in query.all():
            a += '[[{}]] {}\n'.format(task.id, task.name)
        query = db.session.query(Task).filter_by(priority='high', chat=chat).order_by(Task.id)
        a += '\n *high*\n'
        for task in query.all():
            a += '[[{}]] {}\n'.format(task.id, task.name)

        send_message(a, chat)

    def check_parent(self, task, to_check, chat):
        if not task.parents == '':
            parent_id = task.parents.split(',')
            parent_id.pop()

            index = [int(id) for id in parent_id]

            if to_check in index:
                return False
            else:
                parent = db.session.query(Task).filter_by(id=index[0], chat=chat)
                parent = parent.one()
                return self.check_parent(parent, to_check, chat)

        return True

    @contract(msg='validate_msg')
    def get_duedate(self, msg):

        duedate = ''

        if len(msg) > 10:
            date = msg[-10::]
            try:
                duedate = datetime.strptime(date, "%d/%m/%Y").date()
            except ValueError:
                pass

        return duedate         

    new_contract('validate_title', lambda title: isinstance(title, str) and len(title)>=2)
    @contract(chat='int, > 1', title='validate_title')
    def create_issues_in_github(self, title, chat):
        url='https://api.github.com/repos/TecProg-20181/T--Coxinhabot/issues'
        session = requests.Session()
        login = keepLoginGithub.getLogin()
        session.auth = (login[0], login[1])
        issue = {'title':title}
        postIssue = session.post(url, json.dumps(issue))
        if postIssue.status_code == 201:
            send_message('Successfully created issue {0:s}'.format(title), chat)
        else:
            send_message('Could not create issue {0:s}'.format(title), chat)