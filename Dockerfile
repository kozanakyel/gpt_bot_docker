FROM python:3.8-alpine

WORKDIR /app
COPY . .
RUN ["pip", "install", "-r", "requirements.txt"]

CMD ["python", "gpt_telegram_bot.py"]