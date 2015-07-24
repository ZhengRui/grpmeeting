This is a demo web based on [Flask](http://flask.pocoo.org/), though it's meant for meeting management and discussion within my lab, with minor changes in css it can also become a CMS like a personal blog. I think the most unique feature is **Everything in Markdown** -- you can post and comment in Markdown syntax with MathJax support.

### Setting up
+ **Database**
```bash
mysql -u root -p                    # logged in as root to create user
```

```sql
-- create user, database if necessary

create user 'testusr'@'localhost' identified by 'testpsd'; -- create 'testusr' with 'testpsd'
create database testdb;                         -- create 'testdb' for this project
grant all on testdb.* to 'testusr'@'localhost'; -- grant privileges
flush privileges;
show grants for 'testusr'@'localhost';          -- check
```

Exit and now logged in as testusr
```bash
mysql -u testusr -p
```

```sql
-- create tables for this project
use testdb;

-- create table: users
CREATE TABLE `users` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `pwdhash` varchar(100) NOT NULL,
  `state` tinyint(1) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

-- create table: meetings
CREATE TABLE `meetings` (
  `mid` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `title` varchar(256) NOT NULL,
  `abstr` text,
  `mtime` datetime NOT NULL,
  `mplace` varchar(256) NOT NULL,
  `tags` varchar(512) DEFAULT NULL,
  `likesnum` smallint(5) unsigned DEFAULT '0',
  `downlink` varchar(256) DEFAULT NULL,
  `cmtsnum` smallint(5) unsigned DEFAULT '0',
  PRIMARY KEY (`mid`),
  KEY `uid` (`uid`),
  CONSTRAINT `meetings_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

-- create table: likes
CREATE TABLE `likes` (
  `uid` int(11) NOT NULL,
  `mid` int(11) NOT NULL,
  PRIMARY KEY (`uid`,`mid`),
  KEY `mid` (`mid`),
  CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`),
  CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`mid`) REFERENCES `meetings` (`mid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- create table: comments
CREATE TABLE `comments` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `mid` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  `cpid` int(11) NOT NULL,
  `cmt` text NOT NULL,
  `ctime` datetime NOT NULL,
  PRIMARY KEY (`cid`),
  KEY `mid` (`mid`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`mid`) REFERENCES `meetings` (`mid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
```

Check serve.py file, near line 18 make sure it connects to the right database using right user with right password
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://testusr:testpsd@localhost/testdb'
```

+ **Flask**
```bash
git clone https://github.com/ZhengRui/grpmeeting.git
cd grpmeeting
virtualenv venv                     # create virutal environment
source venv/bin/activate            # activate virtual environment
pip install -r requirements.txt     # install Flask and relevant extensions inside this virtual envorionment
python serve.py                     # start using the web
```




### Implementation
+ **Markdown / MathJax**

  *References*: [PageDown](https://code.google.com/p/pagedown/wiki/PageDown) is used on Stack Overflow, here is a [PageDown demo](http://pagedown.googlecode.com/hg/demo/browser/demo.html). [Prettify](https://code.google.com/p/google-code-prettify/wiki/GettingStarted) is used to highlight code (e.g. highlight the injected html after client creates new contents). [MathJax](http://docs.mathjax.org/en/latest/start.html) and [MathJax tutorial](http://meta.math.stackexchange.com/questions/5020/mathjax-basic-tutorial-and-quick-reference), for researchers you definitly need it. [Flask-Markdown](https://pythonhosted.org/Flask-Markdown/) is used on the server for the rendering when pages are first requested.

+ **User Log In / Out**

  *References*: [Flask-WTF Validation](http://code.tutsplus.com/tutorials/intro-to-flask-adding-a-contact-page--net-28982), [Sign in and out](http://code.tutsplus.com/tutorials/intro-to-flask-signing-in-and-out--net-29982). Learn how to do form validation on the server through these two nice tutorials.

+ **Styles**

  *References*: I already forgot from where i copied the time-line css codes, but a collection can be found on [Timeline on Codepen](http://codepen.io/tag/timeline/). [40 Beautiful forms](https://www.freshdesignweb.com/css-registration-form-templates/), i choosed [Horizontal Responsive Form](http://blog.templatemonster.com/demos/responsive-css3-horizontal-application-style-form-fields/demo/index.html). [CSS3 Modal PopUp Div Demo 1](http://jsfiddle.net/kumarmuthaliar/GG9Sa/1/), [Demo 2](http://www.script-tutorials.com/demos/222/index.html).

+ **Uploading**

  *References*: [Flask uploading files](http://flask.pocoo.org/docs/0.10/patterns/fileuploads/), [Mini example](http://code.runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-file-to-the-server-in-flask-for-python).

+ **SQLAlchemy**

  *References*: [Flask-SQLAlchemy Declaring Models](https://pythonhosted.org/Flask-SQLAlchemy/models.html), [SQLAlchemy basic relationship patterns](http://docs.sqlalchemy.org/en/rel_1_0/orm/basic_relationships.html), understand what does backref mean and how to define one-one, one-many and many-many relations.


