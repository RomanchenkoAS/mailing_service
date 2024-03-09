FROM python:3.10-slim
LABEL authors="RomanchenkoAS"
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN  pip install poetry==1.3.2 \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev
COPY . /app/

ENTRYPOINT ["python", "manage.py", "runserver"]