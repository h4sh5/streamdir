FROM python:3.10-alpine

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY app.py /

CMD flask run -h "0.0.0.0"
