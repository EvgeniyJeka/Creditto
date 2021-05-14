FROM python

WORKDIR var/www/html

COPY . .

RUN pip install -r requirements.txt


CMD ["python", "consumer_to_matcher.py"]