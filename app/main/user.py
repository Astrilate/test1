import hashlib
from flask import jsonify, request
from flask_cors import CORS

from app.main import user
from app import db
from app.main.util import create_token
from app.model import users, name, admins


CORS(user, supports_credentials=True)


@user.route('/user', methods=['POST', 'OPTIONS'])
def register():
    idata = {}
    get_json = request.get_json()
    ch = users.query.filter(users.username == get_json.get('username')).first()
    if ch is not None:
        return jsonify(code=400, message="用户名已存在")
    else:
        a = users(username=get_json.get('username'),
                  password=hashlib.sha256(get_json.get('password').encode("utf-8")).hexdigest(),
                  name=get_json.get('name'),
                  gender=get_json.get('gender'),
                  birth=get_json.get('birth'),
                  status=get_json.get('status'),
                  tel=get_json.get('tel'))
        db.session.add(a)
        db.session.commit()
        search = users.query.filter(users.username == get_json.get('username')).first()
        idata.update(id=search.id)
        idata.update(username=get_json.get('username'))
        return jsonify(code=200, message="success", data=idata)


@user.route('/login', methods=['POST', 'OPTIONS'])
def login():
    idata = {}
    get_json = request.get_json()
    if get_json.get("type") == "admin":
        ku = admins
    else:
        ku = users
    username = get_json.get("username")
    password = hashlib.sha256(get_json.get('password').encode("utf-8")).hexdigest()
    ch = ku.query.filter(ku.username == get_json.get('username')).first()
    if ch is not None:
        if ch.password != password:
            return jsonify(code=400, message="密码错误")
        else:
            up = name.query.filter(name.id > 0)
            c = up.first()
            if c is not None:
                up.update({"name": username})
            else:
                b = name(name=username)
                db.session.add(b)
            db.session.commit()
            access_token = create_token(username)
            idata.update(username=username)
            search = ku.query.filter(ku.username == get_json.get('username'))[0]
            idata.update(id=search.id)
            idata.update(token=access_token)
            return jsonify(code=200, message="success", data=idata)
    else:
        return jsonify(code=400, message="用户名不存在")
