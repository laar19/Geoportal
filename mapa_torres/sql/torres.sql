-- Adminer 4.7.6 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP TABLE IF EXISTS `torres`;
CREATE TABLE `torres` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) COLLATE utf8_spanish_ci NOT NULL,
  `region` varchar(20) COLLATE utf8_spanish_ci NOT NULL,
  `latitud` varchar(20) COLLATE utf8_spanish_ci NOT NULL,
  `longitud` varchar(20) COLLATE utf8_spanish_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;

INSERT INTO `torres` (`id`, `nombre`, `region`, `latitud`, `longitud`) VALUES
(1,	'Torre 1',	'Porlamar',	'11.071',	'-63.677'),
(2,	'Torre 2',	'Cumaná',	'10.553',	'-64.138'),
(3,	'Torre 3',	'Caracas',	'10.207',	'-66.863'),
(5,	'Torre 4',	'Valencia',	'10.120',	'-68.445');

-- 2020-02-26 14:55:15
