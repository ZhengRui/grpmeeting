-- Create tables for this db.
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

commit;
