# 小牛定时任务管理（xiaoniu_cron）


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

[体验地址](http://cron_demo.aniulee.com/ "体验地址") 密码：123456

大家有什么问题，或者更好的建议可以加群：[730929995](https://jq.qq.com/?_wv=1027&k=6ovCipI9) 交流交流！
或者 [问题反馈](https://support.qq.com/products/284784 "问题反馈")

### 更新记录

#### 2021-11-15

最近有点忙，更新慢。感谢大家的支持！

* 优化上个版本遗留的bug。
* 新增`企业微信通知`，有错误就会及时通知。
* 新增回调接口签名，使API更安全。

#### 2021-02-22

提前祝大家元宵节快乐！！

* 优化分布式，如果有人需要用分布式的话，最好用此版本。
* 增加`上传实时执行记录`，方便用户查看该任务更详细情况。比如定时任务调用的是一个长时间的操作（通常会加异步去处理），这时候就需要上传任务更详细的执行的情况。
* 页面优化。
* 增加数据库更新命令

#### 2020-12-30

提前祝大家新年快乐，元旦快乐！！

* Python环境由原来3.5调整为3.6。
* 服务用supervisor来维护。
* 增加日志系统，存放于datas/logs目录下。

#### 2020-10-28

* 新增回调返回错误关键词自定义(配置可修改)
* 新增WEB管理任务，任务记录批量删除
* 优化定时任务异常报错，增加异常捕获
* docker配置修改，使其更精简

新增开源项目（欢迎star）

[小牛异步队列任务系统](https://github.com/aniu-lee/xiaoniu_tasks "小牛异步队列任务系统")

#### 2020-09-30

祝大家国庆节快乐！！

* 新增API-开启与关闭任务
* 增加定时删除job记录，默认保留1000条记录(配置可修改)
* API增加access_token,使API更健壮。(配置可修改)
* 网页：增加记录删除功能
* README更新


### 一、基本配置(conf.ini 文件)
```ini
[default]
#是否是体验环境 1是 0否
is_dev=0
#是否单机 0 集群 1单机模式
is_single=1
#如果 集群 redis配置必须配置
redis_host=127.0.0.1
redis_pwd=123456
redis_db=1
redis_port=6379
#【存储cron】存储cron定时数据 
#如果是集群模式 数据库得选mysql
#如果是docker 安装 默认 sqlite:////home/www/xiaoniu_cron.sqlite
#mysql url 格式： mysql+pymysql://用户:密码@数据库ip/xiaoniu_cron
cron_db_url=sqlite:////home/www/xiaoniu_cron.sqlite
#存储job_log 如果是集群模式 数据库得选mysql 
#如果是docker 安装 默认 sqlite:////home/www/xiaoniu_db.sqlite
#mysql url 格式：mysql+pymysql://{用户}:{密码}@{数据库ip}/xiaoniu_cron
cron_job_log_db_url=sqlite:////home/www/xiaoniu_db.sqlite
#网页登录密码
login_pwd=12345679
#异常返回关键词，可自定义,不区分大小写(多个请用，隔开)。当请求req_url之后返回如果包含此关键词，则就会报错通知
error_keyword=fail
#每条job记录保存数
job_log_counts = 1000
#api调用的时候用到的，假如没设置，代表不验证
api_access_token = abcdabcd
#回调接口安全key 
# 生成规则  
#参数按 参数按照key=value的格式，并按照参数名ASCII字典序排序拼接后，再拼上api_key，生成xiaoniu_cron_sign
api_key=thisisapikey
#企业微信配置信息
qywechat_corpid=**********
qywechat_corpsecret=***********
qywechat_agentid=*************
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

https://www.aniulee.com/#/details?id=286

### 四、开始使用

> 访问链接 http://{ip}:{docker-compose.yml设置的端口}

### 五、更新数据库命令

`sudo docker exec -it {容器ID} /bin/bash -c 'cd /home/www && python3.6 manage.py db migrate -m "upgrade" && python3.6 manage.py db upgrade'` 

* 添加定时任务

[![1](doc/1.png "添加date定时")]()

[![2](doc/2.png "添加定时")]()

* 通过api调用 

[![4](doc/4.png "添加定时")]()

* 定时任务列表

[![3](doc/3.png "添加date定时")]()

### 五、简单例子

* 每个月20号提醒我还花呗

* 每天凌晨2点清理垃圾

。。。

[更多例子设置参考](https://www.aniulee.com/#/details?id=260 "更多例子")

### 六、问题反馈

[问题反馈](https://support.qq.com/products/284784 "问题反馈")

QQ群：[730929995](https://jq.qq.com/?_wv=1027&k=6ovCipI9)

### 七、关于本人

[aniulee博客](https://www.aniulee.com "aniulee博客")

[小牛异步队列任务系统](https://github.com/aniu-lee/xiaoniu_tasks "小牛异步队列任务系统")

[两分钟内实现实时推送](https://www.aniulee.com/#/wx_push_setting "两分钟内实现实时推送")


#### 如果感觉项目还不错，有帮到您，来颗星，感谢！

#### 开源不易，欢迎大佬赏杯茶。
[![6](doc/6.png "添加date定时")]()
