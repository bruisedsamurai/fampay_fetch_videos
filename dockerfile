FROM python:3.11.1-alpine

ENV APP_HOME=/app/
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev
    
RUN python -m pip install --upgrade pip \
    && python -m pip install poetry

COPY . /app/

RUN poetry config virtualenvs.create false 

RUN poetry install --no-interaction --no-ansi
