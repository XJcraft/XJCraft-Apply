# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum, unique
from webbase import db, ModelMixin


@unique
class ApplyType(Enum):
    QQLevel = 1  # QQ 等级过太阳
    Invite = 2   # 老玩家邀请
    PYJY = 3     # OP Py 交易


@unique
class ApplyStatus(Enum):
    NEW = 1      # 待审核
    ACCEPT = 2   # 已通过
    DENY = 3     # 已拒绝


class ApplyOP(db.Model, ModelMixin):
    __tablename__ = 'apply_op'
    username = db.Column(db.String(16), primary_key=True)
    password = db.Column(db.String(120, collation='NOCASE'), nullable=False)


class ApplyPlayer(db.Model, ModelMixin):
    __tablename__ = 'apply_player'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(16), nullable=False)
    password = db.Column(db.String(120, collation='NOCASE'), nullable=False)
    req_time = db.Column(db.DateTime, nullable=False)
    apply_time = db.Column(db.DateTime)
    apply_op = db.Column(db.String(16))
    status = db.Column(db.Enum(ApplyStatus), nullable=False)
    type = db.Column(db.Enum(ApplyType), nullable=False)
    ip = db.Column(db.String(15), nullable=False)
    qq = db.Column(db.String(11), nullable=False)
    old_player_name = db.Column(db.String(16))
    op_name = db.Column(db.String(16))


def init():
    pass
