FROM python:3.11-slim


RUN apt-get update \
    && apt-get install -y --no-install-recommends bash git vim \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install dbt-postgres==1.9.1  

RUN pip install pytz


WORKDIR /usr/app


CMD ["tail","-f","/dev/null"]