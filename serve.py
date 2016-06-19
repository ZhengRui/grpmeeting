import os
from flask import Flask, render_template, session, request, flash, url_for, redirect, json, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.pagedown import PageDown
from flask.ext.pagedown.fields import PageDownField
from flask.ext.markdown import Markdown
from werkzeug import generate_password_hash, check_password_hash, secure_filename
from flask_wtf import Form
from wtforms import IntegerField, TextField, TextAreaField, DateTimeField, SubmitField, validators, ValidationError, PasswordField
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
pagedown = PageDown(app)
markdown = Markdown(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://zerry:cluster@localhost/grpmeeting'
app.config['SECRET_KEY'] = 'randommeetings'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy()
db.init_app(app)

likes = db.Table('likes', 
        db.Column('uid', db.Integer, db.ForeignKey('users.uid')),
        db.Column('mid', db.Integer, db.ForeignKey('meetings.mid'))
        )

class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    pwdhash = db.Column(db.String(80))
    state = db.Column(db.Boolean)
    meetings = db.relationship('Meeting', backref='speaker', lazy='dynamic')
    likedmeetings = db.relationship('Meeting', secondary=likes, backref='likedusers', lazy='dynamic')

    def __init__(self, name, email, password):
        self.name = name.title()
        self.email = email.lower()
        self.set_password(password)
        self.state = True

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

class Meeting(db.Model):
    __tablename__ = 'meetings'
    mid = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    title = db.Column(db.String(200))
    abstr = db.Column(db.Text)
    mtime = db.Column(db.DateTime)
    mplace = db.Column(db.String(200))
    tags = db.Column(db.String(500))
    likesnum = db.Column(db.SmallInteger)
    downlink = db.Column(db.String(200))
    cmtsnum = db.Column(db.SmallInteger)
    comments = db.relationship('Comment', backref='meeting', lazy='dynamic')

    def __init__(self, uid, title, abstr, mtime, mplace, tags, downlink):
        self.uid = uid
        self.title = title
        self.abstr = abstr
        self.mtime = mtime
        self.mplace = mplace
        self.tags = tags
        self.likesnum = 0
        self.downlink = downlink
        self.cmtsnum = 0

class Comment(db.Model):
    __tablename__ = 'comments'
    cid = db.Column(db.Integer, primary_key = True)
    mid = db.Column(db.Integer, db.ForeignKey('meetings.mid'))
    uid = db.Column(db.Integer)
    cpid = db.Column(db.Integer)
    cmt = db.Column(db.Text)
    ctime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, mid, uid, cpid, cmt):
        self.mid = mid
        self.uid = uid
        self.cpid = cpid
        self.cmt = cmt

class SignupForm(Form):
    name = TextField("Name", [validators.Required("Please enter your name.")])
    email = TextField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Create account")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken")
            return False
        else:
            return True

class SigninForm(Form):
    email = TextField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True 
        else:
            self.email.errors.append("Invalid e-mail or password")
            return False

class MeetingForm(Form):
    uid = IntegerField("Uid", [validators.Required("Please enter your user id.")])
    title = TextField("Title", [validators.Required("Required.")])
    #abstr = TextAreaField("Abstract")
    abstr = PageDownField("Abstract")
    mtime = DateTimeField("Time", [validators.Required("Required. 1990-12-30T00:00")], format='%Y-%m-%dT%H:%M')
    mplace = TextField("Location", [validators.Required("Required.")])
    tags = TextField("Tags")
    downlink = TextField("Slides")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            print self.errors
            return False
        return True


@app.route('/')
@app.route('/index')
def home():
    meetingform = MeetingForm()   # for generating csrf string
    return render_template('index.html', meetingform=meetingform)

@app.route('/#meetingform')
@app.route('/#close')
def refreshhome():
    return redirect(url_for('home'))

@app.route('/project')
def projcet():
    return render_template('project.html')

# test connection to database
#@app.route('/testdb')
#def testdb():
#    if db.session.query("1").from_statement("SELECT 1").all():
#        return 'It Works.'
#    else:
#        return 'Something is broken.'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            newuser = User(form.name.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()
            session['uid'] = newuser.uid    # only after commit(), newuser will get a valid uid value
            session['name'] = newuser.name
            session['signed_in'] = True
            return redirect(url_for('home'))

    elif request.method == 'GET':
        return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signin.html', form=form)
        else:
            user = User.query.filter_by(email = form.email.data).first()
            session['uid'] = user.uid
            session['name'] = user.name
            session['signed_in'] = True
            return redirect(url_for('home'))

    elif request.method == 'GET':
        return render_template('signin.html', form=form)

@app.route('/signout')
def signout():
    if 'name' not in session:
        return redirect(url_for('signin'))

    session.pop('uid', None)
    session.pop('name', None)
    session.pop('signed_in', False)
    return redirect(url_for('home'))

@app.route('/newOReditmeeting', methods=['POST'])
def newOReditmeeting():
    mid = request.form['mid']
    form = MeetingForm()
    if form.validate() == False:
        return json.dumps({'success':'0', 'err':form.errors})
    else:
        downlink = ''
        slides = request.files.getlist('slides')
        for slide in request.files.getlist('slides'):
            filename = secure_filename(slide.filename)
            if filename:
                filename = 'usr' + str(form.uid.data) + '-' + filename;
                slide.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                downlink +=  filename + '; '
        downlink = downlink[:-2]

        if not mid:
            meeting = Meeting(form.uid.data, form.title.data, form.abstr.data, form.mtime.data, form.mplace.data, form.tags.data, downlink)
            db.session.add(meeting)
        else:
            meeting = Meeting.query.filter_by(mid = mid).first()
            if meeting.uid == form.uid.data or session['name'] == "Symlab":
                meeting.mtime = form.mtime.data
                meeting.mplace = form.mplace.data
                meeting.title = form.title.data
                meeting.tags = form.tags.data
                meeting.abstr = form.abstr.data
                if downlink:
                    if meeting.downlink:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], meeting.downlink))
                    meeting.downlink = downlink
        db.session.commit()
        return json.dumps({'success':'1'})

@app.route('/getusrlist')
def getusrlist():
    if session.has_key('name') and session['name'] == "Symlab":
        q = db.session.query(User.name, User.uid).filter_by(state = 1)
        return json.dumps(dict(q))
    else:
        return 'No Privilege !'

@app.route('/batchmeetings')
def batchmeetings():
    #print request.args
    start = request.args.get('start', 0, type=int)
    step = request.args.get('step', 10, type=int)
    #print start, step
    batchmeetings = Meeting.query.order_by(Meeting.mtime.desc(), Meeting.mid.desc()).limit(step).offset(start).all()
    fstlike2u = {}
    for meeting in batchmeetings:
        fstlike2u[meeting.mid] = True
        if session.has_key('uid'):
            user = User.query.filter_by(uid = session['uid']).first()
            if user in meeting.likedusers:
                fstlike2u[meeting.mid] = False
    return json.dumps({'injecthtml':render_template('timeline-item.html', batchmeetings=batchmeetings, upath=app.config['UPLOAD_FOLDER'], fstlike2u=fstlike2u)})

@app.route('/likeameeting')
def likeameeting():
    mid = request.args.get('mid', type=int)
    meeting = Meeting.query.filter_by(mid = mid).first()

    if session.has_key('uid'):
        user = User.query.filter_by(uid = session['uid']).first()
        meeting.likedusers.append(user)
        db.session.commit()

    meeting.likesnum += 1
    db.session.commit()
    return json.dumps({'newlikesnum': meeting.likesnum})

@app.route('/unlikeameeting')
def unlikeameeting():
    mid = request.args.get('mid', type=int)
    meeting = Meeting.query.filter_by(mid = mid).first()

    if session.has_key('uid'):
        user = User.query.filter_by(uid = session['uid']).first()
        meeting.likedusers.remove(user)
        db.session.commit()

    meeting.likesnum -= 1
    db.session.commit()
    return json.dumps({'newlikesnum': meeting.likesnum})

@app.route('/newcomment')
def newcomment():
    mid = request.args.get('mid', type=int)
    cpid = request.args.get('cpid', type=int)
    isfresh = request.args.get('isfresh', type=int)
    cmt = request.args.get('cmt')
    if session.has_key('uid'):
        meeting = Meeting.query.filter_by(mid = mid).first()
        if isfresh:
            comment = Comment(mid, session['uid'], cpid, cmt)
            db.session.add(comment)
            meeting.cmtsnum += 1
        else:
            comment = Comment.query.filter_by(cid = cpid).first()
            comment.cmt = cmt
        db.session.commit()
        return json.dumps({'injecthtml': displaycomments(mid), 'newcmtsnum': meeting.cmtsnum})
    else:
        return 'No Privilege !'


@app.route('/getcomments')
def getcomments():
    mid = request.args.get('mid', type=int)
    return json.dumps({'injecthtml': displaycomments(mid)})

def displaycomments(mid):
    comments = Comment.query.filter_by(mid = mid).order_by(Comment.ctime.asc()).all()
    uidname = dict(db.session.query(User.uid, User.name).all())
    commenters = {}
    for comment in comments:
        if comment.uid in uidname:
            commenters[comment.cid] = uidname[comment.uid]
        else:
            commenters[comment.cid] = 'Someone'

    comments = mktreestructure(comments, mid, 1)
    return render_template('comments-item.html', comments=comments, commenters=commenters)

def mktreestructure(cmts, mid, rootnode):
    treel = [item for item in cmts if item.cpid == (0 if rootnode else mid)]
    cmts = [item for item in cmts if not item.cpid == (0 if rootnode else mid)]
    for item in treel:
        item.childcmts = mktreestructure(cmts, item.cid, 0)
    return treel

@app.route('/getacomment')
def getacomment():
    cid = request.args.get('cid', type=int)
    comment = Comment.query.filter_by(cid = cid).first()
    return json.dumps({'rawcmt': comment.cmt})

@app.route('/getameeting')
def getameeting():
    mid = request.args.get('mid', type=int)
    meeting = Meeting.query.filter_by(mid = mid).first()
    return json.dumps({'title': meeting.title, 'place': meeting.mplace, 'time': meeting.mtime.isoformat(), 'abstract': meeting.abstr, 'tags': meeting.tags, 'downlink': meeting.downlink, 'upath': app.config['UPLOAD_FOLDER']})

@app.template_filter()
def timesince(dt, default="just now"):
    '''
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc
    '''

    now = datetime.now() + timedelta(microseconds=500000)
    diff = now - dt

    periods = (
            (diff.days / 365, "year", "years"),
            (diff.days / 30, "month", "months"),
            (diff.days / 7, "week", "weeks"),
            (diff.days, "day", "days"),
            (diff.seconds / 3600, "hour", "hours"),
            (diff.seconds / 60, "minute", "minutes"),
            (diff.seconds, "second", "seconds"),
            )

    for period, singular, plural in periods:
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default


if __name__ == "__main__":
    app.run(debug=True)

