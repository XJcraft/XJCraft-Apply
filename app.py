# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
from datetime import datetime
from webbase import app, db, transactional
from model import ApplyOP, ApplyPlayer, ApplyStatus, ApplyType, CrazyLoginAccount
from util import valid_json, valid_not_blank, valid_regexp, get_ip, auth, success, fail, pager_data
from flask import session, request
from sqlalchemy import func


@app.route("/api/login/login", methods=["POST"])
@valid_json("username", [valid_not_blank, valid_regexp(r"[a-zA-Z0-9_]{3,16}")])
@valid_json("password", [valid_not_blank, valid_regexp(r"[a-zA-Z0-9]{6,50}")])
def login() -> dict:
    """
    OP 登录
    """
    json_data = request.get_json()

    op: ApplyOP = ApplyOP.query \
        .filter_by(username=json_data["username"]) \
        .first()

    if op and op.password == json_data["password"]:
        session["username"] = op.username
        return success()
    else:
        return fail("用户名或密码错误")


@auth
@app.route("/api/login/logout", methods=["GET"])
def logout() -> dict:
    """
    OP 退出登录
    """
    session.pop("username", None)
    return success()


@auth
@app.route("/api/user/info", methods=["GET"])
def user_info() -> dict:
    """
    OP 查询用户信息
    """
    return success(session["username"])


@auth
@app.route("/api/req/list", methods=["GET"])
def req_list() -> dict:
    """
    查询玩家申请列表
    """
    page: int = int(request.args["page"])
    page_size: int = int(request.args["pageSize"] if request.args["pageSize"] else "10")

    count: int = db.session.query(func.count(ApplyPlayer.id)).scalar()
    page: int = max(1, min(page, math.ceil(count / page_size)))

    apply_players: list = ApplyPlayer.query \
        .order_by(ApplyPlayer.req_time.desc()) \
        .limit(page_size) \
        .offset((page - 1) * page_size) \
        .all()

    for player in apply_players:
        player.password = None

    return success(pager_data(page, count, apply_players, page_size))


@auth
@app.route("/api/req/apply", methods=["POST"])
@valid_json("player_name", [valid_not_blank, valid_regexp(r"[a-zA-Z0-9_]{3,16}")])
@transactional
def apply() -> dict:
    """
    OP 处理玩家申请
    """
    json_data = request.get_json()
    player_name = json_data["player_name"]
    result = ApplyStatus.__members__[json_data["result"]]

    if not result or result is ApplyStatus.NEW:
        return fail("状态错误")

    # 查出玩家
    player: ApplyPlayer = ApplyPlayer.query \
        .filter_by(player_name=player_name) \
        .first()

    if not player:
        return fail("未找到此玩家")
    elif player.status != ApplyStatus.NEW:
        return fail("此玩家已审核过")

    if result is ApplyStatus.ACCEPT:
        account: CrazyLoginAccount = CrazyLoginAccount.query \
            .filter(func.lower(CrazyLoginAccount.name) == player.player_name.lower()) \
            .first()
        if account:
            return fail("玩家名已存在")  # TODO 未来允许 OP 帮助改名

    # 更新结果
    player.status = result.name
    player.apply_time = datetime.now()
    player.apply_op = session["username"]
    db.session.add(player)

    # 自动创建账号
    if result is ApplyStatus.ACCEPT:
        account: CrazyLoginAccount = CrazyLoginAccount(
            name=player.player_name,
            password=player.password,
            ips="",
            lastAction=datetime.now(),
            loginFails=0,
            passwordExpired=False
        )
        db.session.add(account)

    return success()


@app.route("/api/req/req", methods=["POST"])
@valid_json("player_name", [valid_not_blank, valid_regexp(r"[a-zA-Z0-9_]{3,16}")])
@valid_json("password", [valid_not_blank, valid_regexp(r"[a-zA-Z0-9]{6,50}")])
@valid_json("type", [valid_not_blank])
@valid_json("qq", [valid_not_blank, valid_regexp(r"[0-9]{5,11}")])
@transactional
def req() -> dict:
    """
    玩家申请注册
    """
    json_data = request.get_json()

    # 玩家名查重
    player: ApplyPlayer = ApplyPlayer.query \
        .filter_by(player_name=json_data["player_name"]) \
        .first()
    if player:
        return fail("玩家名已存在")
    account: CrazyLoginAccount = CrazyLoginAccount.query \
        .filter(func.lower(CrazyLoginAccount.name) == player.player_name.lower()) \
        .first()
    if account:
        return fail("玩家名已存在")

    # QQ 查重
    player: ApplyPlayer = ApplyPlayer.query \
        .filter_by(qq=json_data["qq"]) \
        .first()
    if player:
        return fail("QQ 号已存在")

    # 校验参数
    req_type: str = json_data["type"]
    op_name = None
    if req_type == ApplyType.QQLevel.name:
        pass
    elif req_type == ApplyType.Invite.name:
        if not valid_not_blank(json_data, "old_player_name"):
            return fail("未填写邀请人玩家名")
    elif req_type == ApplyType.PYJY.name:
        if not valid_not_blank(json_data, "op_name"):
            return fail("未填写 OP 名")
        else:
            op_name = json_data["op_name"]
            if op_name.upper().endswith("_OP"):
                op_name = op_name[:-3]

    ip = get_ip()
    if ip != '127.0.0.11':
        ip_count = db.session.query(func.count(ApplyPlayer.id)) \
            .filter_by(ip=ip, status=ApplyStatus.NEW) \
            .count()
        if ip_count > 3:
            return fail("同一个 IP 最多只能有三个申请")

        last_time = db.session.query(ApplyPlayer.req_time) \
            .filter_by(ip=ip, status=ApplyStatus.NEW) \
            .order_by(ApplyPlayer.req_time.desc()) \
            .limit(1) \
            .first()
        if last_time and (datetime.now() - last_time[0]).seconds < 3600:
            return fail("同一个 IP 每小时只能申请一次")

    # 插 DB
    player = ApplyPlayer(
        player_name=json_data["player_name"],
        password=json_data["password"],
        req_time=datetime.now(),
        status=ApplyStatus.NEW,
        type=ApplyType.__members__[req_type],
        ip=ip,
        qq=json_data["qq"],
        old_player_name=json_data["old_player_name"],
        op_name=op_name
    )
    db.session.add(player)

    return success()


def init():
    pass
