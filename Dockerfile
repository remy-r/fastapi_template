FROM python:3.9-slim

WORKDIR /code/app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

SHELL ["/bin/bash", "-c"]
COPY ./app /code/app

CMD ["uvicorn", "main:app", "--reload","--host", "0.0.0.0", "--port", "80"]
