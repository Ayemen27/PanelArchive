BEGIN TRANSACTION;
CREATE TABLE `backup` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `type` INTEGER,
  `name` TEXT,
  `pid` INTEGER,
  `filename` TEXT,
  `size` INTEGER,
  `addtime` TEXT
, ps STRING DEFAULT 'No');
CREATE TABLE `binding` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `domain` TEXT,
  `path` TEXT,
  `port` INTEGER,
  `addtime` TEXT
);
CREATE TABLE `black_white` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `ip` VARCHAR(45),
  `ps` VARCHAR(40),
  `add_type` VARCHAR(20),
  `add_time` TEXT,
  `timeout` INTEGER,
  `black_reason` INTEGER
);
CREATE TABLE `config` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `webserver` TEXT,
  `backup_path` TEXT,
  `sites_path` TEXT,
  `status` INTEGER,
  `mysql_root` TEXT
);
INSERT INTO "config" VALUES(1,'nginx','/www/backup','/www/wwwroot',1,'admin');
CREATE TABLE `crontab` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `type` TEXT,
  `where1` TEXT,
  `where_hour` INTEGER,
  `where_minute` INTEGER,
  `echo` TEXT,
  `addtime` TEXT
, 'status' INTEGER DEFAULT 1, 'save' INTEGER DEFAULT 3, 'backupTo' TEXT DEFAULT off, 'sName' TEXT, 'sBody' TEXT, 'sType' TEXT, 'urladdress' TEXT, 'save_local' INTEGER DEFAULT 0, 'notice' INTEGER DEFAULT 0, 'notice_channel' TEXT DEFAULT '');
CREATE TABLE `database_servers` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`db_host` REAL,
`db_port` REAL,
`db_user` INTEGER,
`db_password` INTEGER,
`ps` REAL,
`addtime` INTEGER
, db_type REAL DEFAULT 'mysql');
CREATE TABLE `databases` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `name` TEXT,
  `username` TEXT,
  `password` TEXT,
  `accept` TEXT,
  `ps` TEXT,
  `addtime` TEXT
, db_type integer DEFAULT '0', conn_config STRING DEFAULT '{}', sid integer DEFAULT 0, type TEXT DEFAULT MySQL);
CREATE TABLE `domain` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `name` TEXT,
  `port` INTEGER,
  `addtime` TEXT
);
CREATE TABLE `download_token` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`token` REAL,
`filename` REAL,
`total` INTEGER DEFAULT 0,
`expire` INTEGER,
`password` REAL,
`ps` REAL,
`addtime` INTEGER
);
CREATE TABLE `firewall` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `port` TEXT,
  `ps` TEXT,
  `addtime` TEXT
);
INSERT INTO "firewall" VALUES(2,'80','Website default port','0000-00-00 00:00:00');
INSERT INTO "firewall" VALUES(3,'7800','Panel port','0000-00-00 00:00:00');
INSERT INTO "firewall" VALUES(4,'21','FTP port','0000-00-00 00:00:00');
INSERT INTO "firewall" VALUES(5,'22','SSH Port','0000-00-00 00:00:00');
CREATE TABLE `ftps` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `name` TEXT,
  `password` TEXT,
  `path` TEXT,
  `status` TEXT,
  `ps` TEXT,
  `addtime` TEXT
);
CREATE TABLE `logs` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `type` TEXT,
  `log` TEXT,
  `addtime` TEXT
, uid integer DEFAULT '1', username TEXT DEFAULT 'system');
CREATE TABLE `messages` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`level` TEXT,
`msg` TEXT,
`state` INTEGER DEFAULT 0,
`expire` INTEGER,
`addtime` INTEGER
, send integer DEFAULT 0, retry_num integer DEFAULT 0);
CREATE TABLE `security` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `type` TEXT,
    `log` TEXT,
    `addtime` INTEGER DEFAULT 0
    );
CREATE TABLE `site_types` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`name` REAL,
`ps` REAL
);
CREATE TABLE `sites` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `path` TEXT,
  `status` TEXT,
  `index` TEXT,
  `ps` TEXT,
  `addtime` TEXT
, type_id integer DEFAULT 0, edate integer DEFAULT '0000-00-00', project_type STRING DEFAULT 'PHP', project_config STRING DEFAULT '{}');
CREATE TABLE `task_list` (
  `id`              INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` 			TEXT,
  `type`			TEXT,
  `status` 			INTEGER,
  `shell` 			TEXT,
  `other`           TEXT,
  `exectime` 	  	INTEGER,
  `endtime` 	  	INTEGER,
  `addtime`			INTEGER
);
CREATE TABLE `tasks` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` 			TEXT,
  `type`			TEXT,
  `status` 		TEXT,
  `addtime` 	TEXT,
  `start` 	  INTEGER,
  `end` 	    INTEGER,
  `execstr` 	TEXT
);
CREATE TABLE `temp_login` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`token` REAL,
`salt` REAL,
`state` INTEGER,
`login_time` INTEGER,
`login_addr` REAL,
`logout_time` INTEGER,
`expire` INTEGER,
`addtime` INTEGER
);
CREATE TABLE `users` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `username` TEXT,
  `password` TEXT,
  `login_ip` TEXT,
  `login_time` TEXT,
  `phone` TEXT,
  `email` TEXT
, 'salt' TEXT);
INSERT INTO "users" VALUES(1,'bgzftuo8','abaaffd76d5211bd517d8c607c86c103','192.168.0.10','2016-12-10 15:12:56','0','test@message.com','xM1i6KEXYrGj');
CREATE TABLE `wp_site_types` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`name` TEXT,
`ps` TEXT
);
INSERT INTO "wp_site_types" VALUES(1,'Default category','Default site type');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('config',1);
INSERT INTO "sqlite_sequence" VALUES('firewall',5);
INSERT INTO "sqlite_sequence" VALUES('users',1);
INSERT INTO "sqlite_sequence" VALUES('wp_site_types',1);
COMMIT;
