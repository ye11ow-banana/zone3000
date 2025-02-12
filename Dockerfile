FROM python:3.11-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv
RUN pipenv install --system --deploy

COPY . /app/

RUN python manage.py collectstatic --noinput