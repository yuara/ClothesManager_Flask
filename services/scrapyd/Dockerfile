FROM python:3.8

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY scrapyd.sh ./
RUN chmod 0755 /usr/src/app/scrapyd.sh

COPY ./scrapyd.conf ./scraping  ./

ENTRYPOINT ["/usr/src/app/scrapyd.sh"]
