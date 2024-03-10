# Installation

## Prerequisites

- Git
- Python 3.10+
- pip
- Poetry
- Docker
- Docker Compose

## Steps

First, clone this repository:

```bash
git clone https://github.com/RomanchenkoAS/mailing_service.git
cd mailing_service
```

- Ensure you have Python 3.10+ and pip installed, then install Poetry:

```bash
pip install poetry==1.3.2
```

- Inside the project directory, install dependencies using Poetry:

```bash
poetry install 
```

# Deploy in production

- Ensure Docker and Docker Compose are installed. To deploy the application stack in production:

```bash
docker compose up --build -d
```

# Deploy for developement

- Create or ensure dev_env.sh in the project root contains the necessary environment variables for development. Example:

```text
# dev_env.sh
export DEBUG=1
export DB_NAME=dev_db
...
```

- Source the environment variables:

```bash
source dev_env.sh 
```

- Start the database service:

```bash
docker compose up db -d
```

- Run migrations and then start the Django development server:

```bash
python3 manage.py migrate
python3 manage.py runserver
```

# Тестовое задание

на вакансию Бэкенд разработчик Python/Django с базовым знанием ReactJS

## Задание

- Необходимо разработать сервис управления рассылками с возможностью создания, удаления, редактирования, запуска и
  остановки рассылки А также модуль, который будет осуществлять рассылку при запуске с отображением простой статистики.
- Необходимо реализовать модели и методы создания новой рассылки, просмотра, редактирования и получения статистики по
  выполненным или выполняющимся рассылкам.
- Реализовать сам сервис отправки уведомлений. Физическую отправку сообщений выполнять не нужно, достаточно
  перенаправить события отправки в лог файл или в базу данных.
- Реализовать простую статистику по рассылкам
    - Общее количество пользователей в рассылке
    - Какому количеству пользователей уже было отправлено сообщение
- Реализовать интерфейс управление рассылками, допускается использование Django Admin
    - Запуск
    - Остановка
    - Редактирование
    - Удаление
- С помощью ReactJS организовать публично доступную страницу (фронтенд), которая отображает список всех рассылок со
  статистикой по каждой рассылке и обновлением этой статистики в реальном времени с помощью технологий AJAX или
  WebSockets
- Подготовить Docker Compose файл для быстрого запуска проекта со всеми зависимостями

## Критерии приемки

- Выполненное задание необходимо разместить в публичном репозитории на github.com
- Понятная документация по запуску проекта со всеми его зависимостями
- Проект запускается без ошибок и его функционал соответствует заданию
- Docker Compose файл присутствует и запускает весь стек проекта
- Наличие Unit тестов приветствуется

