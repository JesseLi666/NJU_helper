#!/usr/bin/env python
import os
from app import create_app, db, make_celery
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# app = create_app('production')
manager = Manager(app)
migrate = Migrate(app, db)

celery = make_celery(app)
from tasks import *


def make_shell_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
