FROM python:3-slim

ENV TZ="Europe/Oslo"
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .


CMD ["python", "./main.py"]