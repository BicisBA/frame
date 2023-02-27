FROM python:3.9

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml /app/
WORKDIR /app
RUN poetry install --no-interaction --no-root

COPY . /app

RUN poetry install --no-interaction
RUN poetry run pip install uvicorn
