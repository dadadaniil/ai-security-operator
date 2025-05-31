FROM python:3.13.3-slim
LABEL authors="dadadaniil"

RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

COPY analyzer/api/requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

RUN apt-get install curl -y

COPY analyzer/. .
RUN rm api/.env

ENV PYTHONPATH "${PYTHONPATH}:/api"

# todo env variable or smth
#CMD pysmee forward https://smee.io/MQFI8eHvKVJBzDD8 http://localhost:8000/hook/github & python api/main.py
CMD ["python", "api/main.py"]