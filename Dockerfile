FROM python:3-alpine

WORKDIR /apps/gpt_bot/
COPY . .
RUN ["pip", "install", "-r", "requirements.txt"]
VOLUME /apps/gpt_bot/data
CMD ["python", "gpt_telegram_bot.py"]