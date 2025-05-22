FROM python:3.13.3-slim
LABEL authors="dadadaniil"

RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

COPY analyzer/api/requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

COPY analyzer/. .
RUN rm api/.env

ENV PYTHONPATH "${PYTHONPATH}:/api"

CMD ["fastapi", "run", "api/main.py", "--port", "8000"]