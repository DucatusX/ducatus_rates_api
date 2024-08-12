FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code


RUN apt-get update && apt-get install -y netcat-traditional
RUN pip install --upgrade pip

ENV PATH="/code/.venv/bin:$PATH"
RUN pip install uv==0.1.42
RUN uv venv
RUN uv pip install setuptools 
COPY requirements.txt /code/requirements.txt
RUN uv pip install -r requirements.txt


EXPOSE 8000

COPY . /code/

COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]]
