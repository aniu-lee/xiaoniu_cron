# 小牛定时任务管理（xiaoniu_cron）
> 定时任务统一管理。提供界面，api方便使用。
>当有报错，及时推送，方便修改。
>

### 特性

* 支持集群

* 可视化界面操作

* 定时任务统一管理

* 支持API动态调用

* 完全兼容Crontab

* 支持秒级定时任务

* 任务可搜索、暂停、编辑、删除

* 支持查看日志

* BUG及时通知

* Docker 一键安装，方便使用

[体验地址](http://cron_demo.aniulee.com/ "体验地址")

### 一、基本配置(conf.ini 文件)
```ini
[default]
#是否单机 0 集群 1单机模式
is_single=1
#如果 集群 redis配置必须配置
redis_host=47.106.102.150
redis_pwd=BUgaosuni666
redis_db=1
redis_port=6379
#【存储cron】存储cron定时数据 
#如果是集群模式 数据库得选mysql
#如果是docker 安装 默认 sqlite:////home/www/xiaoniu_cron.sqlite
#'mysql+pymysql://用户:密码@数据库ip/xiaoniu_cron'
cron_db_url=sqlite:////home/www/xiaoniu_cron.sqlite
#存储job_log 如果是集群模式 数据库得选mysql 
#如果是docker 安装 默认 sqlite:////home/www/xiaoniu_db.sqlite
#mysql url 格式：mysql+pymysql://{用户}:{密码}@{数据库ip}/xiaoniu_db
cron_job_log_db_url=sqlite:////home/www/xiaoniu_db.sqlite
#网页登录密码
login_pwd=12345679
#推送api_key
#https://www.aniulee.com/#/notices 实时推送
error_notice_api_key=
```

### 二、修改docker-compose.yml 文件
1. 项目地址
2. 端口号
[![5](doc/5.png "修改docker-compose.yml文件")]()
### 三、docker 一键安装
```shell script
sudo docker-compose up --build -d
```
具体docker,docker-compose怎么安装，自行谷歌，百度。

### 四、开始使用
> 访问链接 http://{ip}:{docker-compose.yml设置的端口}


* 添加定时任务
[![1](doc/1.png "添加date定时")]()
[![2](doc/2.png "添加定时")]()
* 通过api调用 
[![4](doc/4.png "添加定时")]()
* 定时任务列表
[![3](doc/3.png "添加date定时")]()

### 问题反馈

[问题反馈](https://support.qq.com/products/284784 "问题反馈")

### 关于本人

[aniulee博客](https://www.aniulee.com "aniulee博客")

[两分钟内实现实时推送](https://www.aniulee.com/#/wx_push_setting "两分钟内实现实时推送")


如果感觉项目还不错，有帮到您，给我来颗星，感谢！

开源不易，欢迎大佬赏杯茶。
[![6](doc/6.png "添加date定时")]()
