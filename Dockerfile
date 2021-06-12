FROM python:3.8

WORKDIR /app
COPY manage.py requirements.txt .
COPY authentication authentication

RUN pip install -r requirements.txt