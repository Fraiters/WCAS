FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "telegram_bot.py"]
