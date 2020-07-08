FROM python:3


RUN apt-get update
RUN	mkdir /app /data
RUN	pip install flask pymongo xmltodict

COPY install.sh /app

RUN chmod +x /app/install.sh

ENTRYPOINT ["./app/install.sh"]