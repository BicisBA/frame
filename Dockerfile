FROM python:3.10-bullseye
RUN apt-get update && apt-get install -y postgresql-client
RUN pip install poetry
COPY . /app
WORKDIR /app
ENV POETRY_VIRTUALENVS_IN_PROJECT true
RUN poetry run pip install uvicorn
RUN poetry install
