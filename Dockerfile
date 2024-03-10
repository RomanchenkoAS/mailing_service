FROM python:3.10-slim
LABEL authors="RomanchenkoAS"
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN  pip install poetry==1.3.2 \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev \
RUN mkdir -p "/home/var/mailing/emails/" 
COPY . /app/

ENTRYPOINT ["python", "manage.py", "runserver"]