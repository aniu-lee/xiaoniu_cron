FROM ubuntu:16.04
MAINTAINER aniulee@qq.com
RUN mkdir /home/www
WORKDIR /home/www
COPY requirements.txt /home/www
COPY doc/supervisors.conf /etc/supervisor/conf.d/supervisord.conf
RUN apt-get update && apt-get install -y tzdata libmysqlclient-dev wget software-properties-common gcc supervisor
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.6 python3.6-dev
RUN wget https://bootstrap.pypa.io/get-pip.py  --no-check-certificate
RUN python3.6 get-pip.py
RUN pip3.6 install -i http://pypi.douban.com/simple/  --trusted-host pypi.douban.com -r requirements.txt
#RUN pip3.6 install  -r requirements.txt
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
CMD ["/usr/bin/supervisord"]
EXPOSE 80