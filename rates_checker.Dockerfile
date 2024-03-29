FROM python:3.7

WORKDIR /code

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY . /code
CMD ["python", "rates_checker.py"]
