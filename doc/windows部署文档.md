# 小牛定时任务管理 windows简易部署文档

## 首先感谢大家的支持一直以来的支持！！！！

### 1. 安装python3.6.8 和 virtualenv

> 我python用的是python3.6.8版本，如果您用的是其他版本，如果出现库问题，可自行解决

### 2. 下载源码并安装虚拟环境和依赖库

```shell script
git clone https://github.com/aniu-lee/xiaoniu_cron.git
cd xiaoniu_cron
virtualenv env
source env/Scripts/activate
pip install -r requirements.txt
# 拷贝 conf.example.ini 一份 命令 conf.ini 并修改路径等信息 再接着下一步
python manage.py db init
python manage.py  db migrate -m "init"
python manage.py db upgrade
```

### 3. 运行

```shell script
python manage.py runserver -d
```



#### 如果感觉项目还不错，有帮到您，来颗星，感谢！

#### 开源不易，欢迎大佬赏杯茶。

微信扫一扫

[![微信扫一扫](weixin.jpg "微信扫码打赏")]()

支付宝扫一扫

[![支付宝扫一扫](ali.jpg "微信扫码打赏")]()
