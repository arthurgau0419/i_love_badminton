FROM python:3.7
ENV TZ Asia/Taipei

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安裝系統library
RUN apt-get update; \
    apt-get install -y --no-install-recommends apt-utils libgdal-dev;

# 安裝工具
RUN apt-get install -y --no-install-recommends netcat vim sudo

# 安裝 tesseract ocr
RUN apt-get install -y --no-install-recommends tesseract-ocr

# 創建必要目錄
RUN mkdir -p /code

# 安裝相依套件
RUN pip install pipenv
COPY ./Pipfile /code
COPY ./Pipfile.lock /code
WORKDIR /code
RUN pipenv install --system --deploy --ignore-pipfile

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . /code

ENTRYPOINT ["scrapy"]
CMD ["--help"]