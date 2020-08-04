FROM python:3.8

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -y cron

COPY cron-d ./.cron-d
RUN crontab .cron-d

COPY project migrations manage.py entrypoint.sh ./

ENTRYPOINT ["sh","/usr/src/app/entrypoint.sh"]
