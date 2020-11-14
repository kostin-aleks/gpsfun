CREATE TABLE `geothing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site_id` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  `code` varchar(32) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `created_date` datetime DEFAULT NULL,
  `author` varchar(128) DEFAULT NULL,
  `cach_type` varchar(128) DEFAULT NULL,
  `country_code` varchar(2) DEFAULT NULL,
  `admin_code` varchar(6) DEFAULT NULL,
  `country_name` varchar(64) DEFAULT NULL,
  `oblast_name` varchar(128) DEFAULT NULL,
  `type_code` varchar(2) DEFAULT NULL,
  `location_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pid` (`pid`),
  KEY `country_code` (`country_code`),
  KEY `admin_code` (`admin_code`),
  KEY `site` (`site_id`),
  KEY `location` (`location_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


CREATE TABLE `geosite` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(16) NOT NULL,
  `name` varchar(128) DEFAULT NULL,
  `url` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `code` (`code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `location` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `NS_degree` int(11) DEFAULT NULL,
  `EW_degree` int(11) DEFAULT NULL,
  `NS_minute` double DEFAULT NULL,
  `EW_minute` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;





