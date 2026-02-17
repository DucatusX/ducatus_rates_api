FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code


RUN apt-get update && apt-get install -y netcat-traditional
RUN pip install --upgrade pip
COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt


EXPOSE 8000

COPY . /code/

COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
