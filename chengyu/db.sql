CREATE TABLE `chengyu` (
`id`                  int(11) NOT NULL AUTO_INCREMENT COMMENT '主键' ,
`detail_url`          varchar(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '详细地址' ,
`simple_description`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '简单描述' ,
`letter_index`        char(2) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '字符索引' ,
`explain`             text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '释义' ,
PRIMARY KEY (`id`),
UNIQUE INDEX `id` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci AUTO_INCREMENT=1 ROW_FORMAT=DYNAMIC;