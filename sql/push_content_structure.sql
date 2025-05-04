SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `push_content`;
CREATE TABLE `push_content` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `type` varchar(255) NOT NULL COMMENT '类型',
  `person` varchar(255) DEFAULT NULL COMMENT '有关的人',
  `day` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '实际日期',
  `desc` varchar(255) DEFAULT NULL COMMENT '描述',
  `identity` varchar(255) DEFAULT NULL COMMENT '身份',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  `is_deleted` int(11) NOT NULL DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=190 DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
