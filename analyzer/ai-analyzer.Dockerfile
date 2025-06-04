FROM python:3.13.3-slim
LABEL authors="dadadaniil"

RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

COPY analyzer/api/requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

RUN apt-get install curl -y

COPY analyzer/. .

ENV PYTHONPATH "${PYTHONPATH}:/api"

CMD ["python", "api/main.py"]