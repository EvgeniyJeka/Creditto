FROM python:3.11.2-alpine3.16

WORKDIR var/www/html

COPY . .

RUN pip install -r requirements.txt


CMD ["python", "consumer_to_sql.py"]