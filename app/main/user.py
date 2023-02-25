import jwt
import hashlib
from flask import jsonify, request
from flask_cors import cross_origin, CORS
from datetime import timedelta, datetime

from app.main import user
from app import db
from app.model import users, name, admins

SECRET_KEY = "asjcklqencoiwrev45y6"
ALGORITHM = "HS256"
CORS(user, supports_credentials=True)


@user.route('/user', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def register():
    idata = {}
    gj = request.get_json()
    try:
        ch = users.query.filter(users.username == gj.get('username'))[0]
        return jsonify(code=400, message="用户名已存在")
    except:
        a = users(username=gj.get('username'),
                  password=hashlib.sha256(gj.get('password').encode("utf-8")).hexdigest(),
                  name=gj.get('name'),
                  gender=gj.get('gender'),
                  birth=gj.get('birth'),
                  status=gj.get('status'),
                  tel=gj.get('tel'))
        db.session.add(a)
        db.session.commit()
        se = users.query.filter(users.username == gj.get('username'))[0]
        idata.update(id=se.id)
        idata.update(username=gj.get('username'))
        return jsonify(code=200, message="success", data=idata)


@user.route('/user/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    idata = {}
    gj = request.get_json()
    if gj.get("type") == "admin":
        ku = admins
    else:
        ku = users
    username = gj.get("username")
    password = hashlib.sha256(gj.get('password').encode("utf-8")).hexdigest()
    ch = ku.query.filter(ku.username == gj.get('username'))
    try:
        ch = ch[0]
        if ch.password != password:
            return jsonify(code=400, message="密码错误")
        else:
            up = name.query.filter(name.id > 0)
            up.update({"name": username})
            try:
                c = up[0]
            except:
                b = name(name=username)
                db.session.add(b)
            db.session.commit()
            access_token_expires = timedelta(seconds=30)
            expire = datetime.utcnow() + access_token_expires
            payload = {
                "sub": username,
                "exp": expire
            }
            access_token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
            idata.update(username=username)
            se = ku.query.filter(ku.username == gj.get('username'))[0]
            idata.update(id=se.id)
            idata.update(token=access_token)
            return jsonify(code=200, message="success", data=idata)
    except:
        return jsonify(code=400, message="用户名不存在")
