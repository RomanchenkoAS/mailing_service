FROM python:3.10-slim
LABEL authors="RomanchenkoAS"
WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN pip install poetry==1.3.2 \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

COPY . /app/
COPY .env /app/.env

RUN mkdir -p "/home/var/mailing/emails"
RUN python manage.py collectstatic --noinput
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]