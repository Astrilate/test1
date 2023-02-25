import base64
import jwt
from flask import jsonify, request
from flask_cors import cross_origin

from app import db
from app.main import view
from app.model import name, project, users, message, myshare

SECRET_KEY = "asjcklqencoiwrev45y6"
ALGORITHM = "HS256"



def check_token():
    token = request.headers.get("Authorization")
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        gall = name.query.filter(name.id == 1)[0].name
        if username == gall:
            return jsonify(code=200, message="success")
        else:
            return jsonify(code=401, message="token无权限")
    except jwt.ExpiredSignatureError:
        return jsonify(code=401, message="token已过期")
    except jwt.PyJWTError:
        return jsonify(code=401, message="无法检验token")


@view.route('/information', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def information():
    result = check_token()
    if result.get_json().get("code") == 401:
        a_data = []
        se = users.query.filter(users.id == request.get_json().get("id"))[0]
        idata = {}
        idata.update(name=se.name)
        idata.update(gender=se.gender)
        idata.update(birth=se.birth)
        idata.update(status=se.status)
        idata.update(tel=se.tel)
        a_data.append(idata)
        return jsonify(code=200, message="success", data=a_data)
    else:
        return result


@view.route('/newproject', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def newproject():
    result = check_token()
    if result.get_json().get("code") == 401:
        image = request.files['file'].read()
        projectname = request.form['projectname']
        content = request.form['content']
        u_id = request.form['u_id']
        a = project(projectname=projectname,
                    content=content,
                    image=image,
                    u_id=u_id)
        db.session.add(a)
        db.session.commit()
        return jsonify(code=200, message="success")
    else:
        return result


@view.route('/myproject', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def myproject():
    result = check_token()
    if result.get_json().get("code") == 401:
        a_data = []
        gj = request.get_json()
        iid = gj.get('id')
        page = request.get_json().get("page")
        offset = (page - 1) * 5
        se = users.query.filter(users.id == iid)[0].project.offset(offset).limit(5)
        for i in se:
            idata = {}
            idata.update(id=i.id)
            idata.update(projectname=i.projectname)
            idata.update(content=i.content)
            idata.update(fund=i.fund)
            idata.update(status=i.status)
            image = i.image
            image = base64.b64encode(image).decode()
            idata.update(image=image)
            a_data.append(idata)
        return jsonify(code=200, message="success", data=a_data)
    else:
        return result


@view.route('/search/project', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def search_project():
    result = check_token()
    if result.get_json().get("code") == 401:
        a_data = []
        gj = request.get_json()
        kw = gj.get('kw')
        page = request.get_json().get("page")
        offset = (page - 1) * 5
        se = project.query.filter(project.status == "已通过").offset(offset).limit(5)
        for i in se:
            if kw in i.projectname or kw in i.content:
                idata = {}
                idata.update(id=i.id)
                idata.update(projectname=i.projectname)
                idata.update(content=i.content)
                idata.update(fund=i.fund)
                idata.update(status=i.status)
                image = i.image
                image = base64.b64encode(image).decode()
                idata.update(image=image)
                a_data.append(idata)
        return jsonify(code=200, message="success", data=a_data)
    else:
        return result


@view.route('/all/project', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def all_project():
    result = check_token()
    if result.get_json().get("code") == 401:
        a_data = []
        page = request.get_json().get("page")
        offset = (page - 1) * 5
        se = project.query.filter(project.status == "已通过").offset(offset).limit(5)
        for i in se:
            idata = {}
            idata.update(id=i.id)
            idata.update(projectname=i.projectname)
            idata.update(content=i.content)
            idata.update(fund=i.fund)
            idata.update(status=i.status)
            image = i.image
            image = base64.b64encode(image).decode()
            idata.update(image=image)
            a_data.append(idata)
        return jsonify(code=200, message="success", data=a_data)
    else:
        return result


@view.route('/verify/project', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def verify_project():
    result = check_token()
    if result.get_json().get("code") == 401:
        a_data = []
        page = request.get_json().get("page")
        offset = (page - 1) * 5
        se = project.query.filter(project.status == "待审核").offset(offset).limit(5)
        for i in se:
            idata = {}
            idata.update(id=i.id)
            idata.update(projectname=i.projectname)
            idata.update(content=i.content)
            idata.update(status=i.status)
            image = i.image
            image = base64.b64encode(image).decode()
            idata.update(image=image)
            a_data.append(idata)
        return jsonify(code=200, message="success", data=a_data)
    else:
        return result


@view.route('/verifying/project', methods=['PUT', 'DELETE', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def verifying_project():
    result = check_token()
    if result.get_json().get("code") == 401:
        pro = project.query.filter(project.id == request.get_json().get("id"))
        if request.method == 'PUT':
            pro.update({"status": "已通过"})
            a = message(projectname=pro[0].projectname,
                        message="项目已通过审核",
                        u_id=pro[0].u_id)
            db.session.add(a)
            db.session.commit()
            return jsonify(code=200, message="success")
        else:
            a = message(projectname=pro[0].projectname,
                        message="项目未通过审核",
                        u_id=pro[0].u_id)
            pro.delete()
            db.session.add(a)
            db.session.commit()
            return jsonify(code=200, message="success")
    else:
        return result


@view.route('/donate/project', methods=['PUT', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def donate_project():
    result = check_token()
    if result.get_json().get("code") == 401:
        gj = request.get_json()
        pro = project.query.filter(project.id == gj.get("id"))
        if gj.get("share") > 0:
            pro.update({"fund": pro[0].fund + gj.get("share")})
            a = message(projectname=pro[0].projectname,
                        message=f"已出资{gj.get('share')}元",
                        u_id=gj.get("u_id"))
            db.session.add(a)
            db.session.commit()
            se = myshare.query.filter(myshare.project_id == gj.get("id")).filter(myshare.u_id == gj.get("u_id"))
            try:
                se.update({"my_share": se[0].my_share + gj.get("share")})
                db.session.commit()
            except:
                b = myshare(project_id=gj.get("id"),
                            my_share=gj.get("share"),
                            u_id=gj.get("u_id"))
                db.session.add(b)
                db.session.commit()
            return jsonify(code=200, message="success")
        else:
            return jsonify(code=400, message="出资金额应为正数")
    else:
        return result


@view.route('/myshare', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def my_share():
    result = check_token()
    if result.get_json().get("code") == 401:
        a_data = []
        page = request.get_json().get("page")
        offset = (page - 1) * 5
        pro = myshare.query.filter(myshare.u_id == request.get_json().get("id")).offset(offset).limit(5)
        for i in pro:
            idata = {}
            idata.update(projectname=project.query.filter(project.id == i.project_id)[0].projectname)
            idata.update(my_share=i.my_share)
            a_data.append(idata)
        return jsonify(code=200, message="success", data=a_data)
    else:
        return result


@view.route('/message', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def my_message():
    result = check_token()
    if result.get_json().get("code") == 401:
        a_data = []
        page = request.get_json().get("page")
        offset = (page - 1) * 5
        pro = message.query.filter(message.u_id == request.get_json().get("id")).offset(offset).limit(5)
        for i in pro:
            idata = {}
            idata.update(projectname=i.projectname)
            idata.update(myessage=i.message)
            a_data.append(idata)
        return jsonify(code=200, message="success", data=a_data)
    else:
        return result
