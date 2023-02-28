from app import db


class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(200), nullable=False)
    password = db.Column(db.VARCHAR(200), nullable=False)
    name = db.Column(db.VARCHAR(200), nullable=False)
    gender = db.Column(db.Enum("男", "女"), nullable=False)
    birth = db.Column(db.VARCHAR(200), nullable=True)
    status = db.Column(db.VARCHAR(200), nullable=False)
    tel = db.Column(db.VARCHAR(12), nullable=False)
    project = db.relationship('project', backref='users')
    myshare = db.relationship('myshare', backref='users')
    message = db.relationship('message', backref='users')


class admins(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(200), nullable=False)
    password = db.Column(db.VARCHAR(200), nullable=False)


class project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    projectname = db.Column(db.VARCHAR(200), nullable=False)
    content = db.Column(db.VARCHAR(200), nullable=False)
    fund = db.Column(db.Float, default=0, nullable=False)
    status = db.Column(db.Enum("已通过", "待审核"), default="待审核", nullable=False)
    image = db.Column(db.VARCHAR(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class myshare(db.Model):
    __tablename__ = 'myshare'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, nullable=False)
    my_share = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    projectname = db.Column(db.VARCHAR(200), nullable=False)
    message = db.Column(db.VARCHAR(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class name(db.Model):
    __tablename__ = 'name'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(200), nullable=False)
