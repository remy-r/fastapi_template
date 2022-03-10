# fastapi_template

## Docker commands

Start container
```
docker-compose up -d
```

Stop container
```
docker-compose down --rmi all -v
```

## Database properties

Table ```notes``` :

|  id   | text | completed | text2 |
| :---: | ---- | :-------: | ----- |

Table ```users``` :

|  id   | name  |        email        | password      |
| :---: | ----- | :-----------------: | ------------- |
|   4   | admin | exemple@exemple.com | test (hashed) |


## Alembic commands

```
alembic revision -m "create account table"
alembic upgrade head
```

## URL test

[http://127.0.0.1/docs](http://127.0.0.1/docs)