FROM python:slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app

RUN python manage.py makemigrations images
RUN python manage.py migrate
RUN python manage.py create_tiers