import base64
import os
from flask import jsonify, request
from flask_cors import CORS

from app import db
from app.main import view
from app.main.util import check_token
from app.model import project, users, message, myshare

CORS(view, supports_credentials=True)


@view.route('/information', methods=['GET', 'OPTIONS'])
@check_token
def information():
    all_data = []
    search = users.query.filter(users.id == request.get_json().get("id")).first()
    idata = {}
    idata.update(name=search.name,
                 gender=search.gender,
                 birth=search.birth,
                 status=search.status,
                 tel=search.tel)
    all_data.append(idata)
    return jsonify(code=200, message="success", data=all_data)


@view.route('/newproject', methods=['POST', 'OPTIONS'])
@check_token
def newproject():
    f = request.files['file']
    f.save(os.path.join('./upload', f.filename))
    projectname = request.form['projectname']
    content = request.form['content']
    user_id = request.form['user_id']
    a = project(projectname=projectname,
                content=content,
                image='./upload/' + f.filename,
                user_id=user_id)
    db.session.add(a)
    db.session.commit()
    return jsonify(code=200, message="success")


@view.route('/myproject', methods=['GET', 'OPTIONS'])
@check_token
def myproject():
    all_data = []
    get_json = request.get_json()
    iid = get_json.get('id')
    page = request.get_json().get("page")
    offset = (page - 1) * 5
    search = users.query.filter(users.id == iid)[0].project[offset: offset + 5]
    for each in search:
        idata = {}
        idata.update(id=each.id,
                     projectname=each.projectname,
                     content=each.content,
                     fund=each.fund,
                     status=each.status)
        with open(each.image, 'rb') as f:
            stream = f.read()
            idata.update(image=base64.b64encode(stream).decode())
        all_data.append(idata)
    return jsonify(code=200, message="success", data=all_data)


@view.route('/search', methods=['GET', 'OPTIONS'])
@check_token
def search_project():
    all_data = []
    get_json = request.get_json()
    kw = get_json.get('kw')
    page = request.get_json().get("page")
    offset = (page - 1) * 5
    search = project.query.filter(project.status == "已通过").offset(offset).limit(5)
    for each in search:
        if kw in each.projectname or kw in each.content:
            idata = {}
            idata.update(id=each.id,
                         projectname=each.projectname,
                         content=each.content,
                         fund=each.fund,
                         status=each.status)
            with open(each.image, 'rb') as f:
                stream = f.read()
                idata.update(image=base64.b64encode(stream).decode())
            all_data.append(idata)
    return jsonify(code=200, message="success", data=all_data)


@view.route('/all', methods=['GET', 'OPTIONS'])
@check_token
def all_project():
    all_data = []
    page = request.get_json().get("page")
    offset = (page - 1) * 5
    search = project.query.filter(project.status == "已通过").offset(offset).limit(5)
    for each in search:
        idata = {}
        idata.update(id=each.id,
                     projectname=each.projectname,
                     content=each.content,
                     fund=each.fund,
                     status=each.status)
        with open(each.image, 'rb') as f:
            stream = f.read()
            idata.update(image=base64.b64encode(stream).decode())
        all_data.append(idata)
    return jsonify(code=200, message="success", data=all_data)


@view.route('/verify', methods=['GET', 'OPTIONS'])
@check_token
def verify_project():
    all_data = []
    page = request.get_json().get("page")
    offset = (page - 1) * 5
    search = project.query.filter(project.status == "待审核").offset(offset).limit(5)
    for each in search:
        idata = {}
        idata.update(id=each.id,
                     projectname=each.projectname,
                     content=each.content,
                     status=each.status)
        with open(each.image, 'rb') as f:
            stream = f.read()
            idata.update(image=base64.b64encode(stream).decode())
        all_data.append(idata)
    return jsonify(code=200, message="success", data=all_data)


@view.route('/verifying', methods=['PUT', 'DELETE', 'OPTIONS'])
@check_token
def verifying_project():
    pro = project.query.filter(project.id == request.get_json().get("id"))
    if request.method == 'PUT':
        pro.update({"status": "已通过"})
        a = message(projectname=pro.first().projectname,
                    message="项目已通过审核",
                    user_id=pro.first().user_id)
        db.session.add(a)
        db.session.commit()
        return jsonify(code=200, message="success")
    else:
        a = message(projectname=pro.first().projectname,
                    message="项目未通过审核",
                    user_id=pro.first().user_id)
        pro.delete()
        db.session.add(a)
        db.session.commit()
        return jsonify(code=200, message="success")


@view.route('/donating', methods=['PUT', 'OPTIONS'])
@check_token
def donate_project():
    get_json = request.get_json()
    pro = project.query.filter(project.id == get_json.get("id"))
    if get_json.get("share") > 0:
        pro.update({"fund": pro.first().fund + get_json.get("share")})
        a = message(projectname=pro.first().projectname,
                    message=f"已出资{get_json.get('share')}元",
                    user_id=get_json.get("user_id"))
        db.session.add(a)
        db.session.commit()
        search = myshare.query.filter(myshare.project_id == get_json.get("id")).filter(
            myshare.user_id == get_json.get("user_id"))
        k = search.first()
        if k is not None:
            search.update({"my_share": k.my_share + get_json.get("share")})
            db.session.commit()
        else:
            b = myshare(project_id=get_json.get("id"),
                        my_share=get_json.get("share"),
                        user_id=get_json.get("user_id"))
            db.session.add(b)
            db.session.commit()
        return jsonify(code=200, message="success")
    else:
        return jsonify(code=400, message="出资金额应为正数")


@view.route('/myshare', methods=['GET', 'OPTIONS'])
@check_token
def my_share():
    all_data = []
    page = request.get_json().get("page")
    offset = (page - 1) * 5
    pro = myshare.query.filter(myshare.user_id == request.get_json().get("id")).offset(offset).limit(5)
    for each in pro:
        idata = {}
        idata.update(projectname=project.query.filter(project.id == each.project_id).first().projectname,
                     my_share=each.my_share)
        all_data.append(idata)
    return jsonify(code=200, message="success", data=all_data)


@view.route('/message', methods=['GET', 'OPTIONS'])
@check_token
def my_message():
    all_data = []
    page = request.get_json().get("page")
    offset = (page - 1) * 5
    pro = message.query.filter(message.user_id == request.get_json().get("id")).offset(offset).limit(5)
    for each in pro:
        idata = {}
        idata.update(projectname=each.projectname,
                     myessage=each.message)
        all_data.append(idata)
    return jsonify(code=200, message="success", data=all_data)
