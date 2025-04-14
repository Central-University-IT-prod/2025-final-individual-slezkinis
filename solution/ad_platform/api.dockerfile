FROM python:3.12-alpine3.21

WORKDIR /usr/src/app

COPY ad_platform/ .
RUN pip install -r requirements.txt

CMD sleep 0.8; python3 manage.py migrate ; python3 manage.py initialize_buckets; python3 manage.py bot & python3 manage.py runserver REDACTED:8080 
