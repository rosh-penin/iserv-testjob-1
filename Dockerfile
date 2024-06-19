FROM python:3.12.4-alpine3.20
WORKDIR /app

RUN apk add --no-cache py3-pip
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "test_run.py"]