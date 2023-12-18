# Yatube
## Описание проекта:
Онлайн-сервис в формате социальной сети с функционалом создания постов (текст + изображения), возможности подписки на авторов и комментирования постов.

## Технологии:
Python, Django, Django ORM, Unittest, SQLite, HTML

## Запуск проекта:
* Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/silifonov/yatube.git

cd yatube_social
```
* Создать и активировать виртуальное окружение:
```
python -m venv venv 

source venv/bin/activate (Mac, Linux)
source venv/scripts/activate (Windows)
```
* Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip 

pip install -r requirements.txt
```
* Перейти в рабочую папку и выполнить миграции:
```
cd yatube

python manage.py migrate
```
* Запустить сервер (локально):
```
python manage.py runserver
```
