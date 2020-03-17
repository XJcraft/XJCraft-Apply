# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import functools

import setting
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from flask.json import JSONEncoder
from contextlib import suppress
from sqlalchemy.inspection import inspect


class ModelMixin:
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self):
        return inspect(self).attrs.keys()


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        with suppress(AttributeError):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.name
        return dict(obj)


app = Flask(setting.APP_NAME)

app.config["SQLALCHEMY_DATABASE_URI"] = setting.SQL_URL
app.config['SQLALCHEMY_ECHO'] = setting.DEBUG
app.config['SQLALCHEMY_POOL_RECYCLE'] = 540
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20

db = SQLAlchemy(app)
transactional_local_data = threading.local()


def init():
    global db, app

    app.secret_key = setting.HTTP_SECRET
    app.json_encoder = MyJSONEncoder
    # TODO 公共异常处理？

    db.create_all()
    app.run(port=setting.HTTP_PORT)  # 注意，阻塞性操作


def transactional(fn):
    """
    事务包装
    """
    @functools.wraps(fn)
    def wrap(*args, **kw):
        if not hasattr(transactional_local_data, 'count') or not transactional_local_data.count:
            transactional_local_data.conn = 0
        transactional_local_data.conn += 1

        try:
            return fn(*args, **kw)
        except Exception:
            db.session.rollback()
            raise
        finally:
            transactional_local_data.conn -= 1
            if not transactional_local_data.conn:
                db.session.commit()
    return wrap
