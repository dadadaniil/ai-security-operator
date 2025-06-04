FROM python:3.9-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/bot.py ./

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "3000"]