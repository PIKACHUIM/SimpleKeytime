-- noinspection SqlNoDataSourceInspectionForFile


CREATE TABLE Users
(
    mail TEXT NOT NULL PRIMARY KEY UNIQUE,
    -- 用户状态 0-未激活，1-正常，2-已禁用
    flag TEXT (1) DEFAULT (0) NOT NULL,
    -- 其他信息 --------------------------
    code TEXT (8), -- 邮箱验证码
    keys TEXT,     -- ACME账号的密钥
    pass TEXT,     -- 登录密码SHA256
    apis TEXT,     -- 证书下载鉴权码
    time INTEGER   -- 邮件验证时间
);


CREATE TABLE Apply
(

);




