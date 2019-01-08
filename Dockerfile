FROM python:3.6-slim
ADD . /code
WORKDIR /code
#COPY ./sc /etc/scrapyd/
#COPY run.sh /usr/bin/run.sh
#EXPOSE 6800
RUN apt-get update && apt-get -y install gcc \
    && pip --no-cache-dir install --upgrade setuptools \
    && python -m pip --no-cache-dir install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    #-i https://mirrors.ali    yun.com/pypi/simple/ \
    && rm -rf ~/.cache/pip
 #ENTRYPOINT /usr/bin/run.sh
CMD ["scrapy", "crawl", "baixing"]
