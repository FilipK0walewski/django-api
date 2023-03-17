# Django Rest Framework image api

## Description

Simple api made with django rast framework.

## Installation

```
git clone https://github.com/FilipK0walewski/django-api.git
cd django-api
docker compose up -d --build
docker compose exec web python manage.py makemigrations images
docker compose exec web python manage.py migrate
docker compose exec web python manage.py create_tiers
docker compose exec web python manage.py collectstatic
```

Now you api should work fine at http://127.0.0.1:7999. To create superuser run

```
docker compose exec web python manage.py createsuperuser
```

## Tests

To run tests 

```
docker compose exec web python manage.py test
```