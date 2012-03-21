#!/usr/bin/env python
# manage.py
# -*- encoding:utf-8 -*-

from flaskext.actions import Manager
from channels.app import app

manager = Manager(app)

if __name__ == "__main__":
    manager.run()
