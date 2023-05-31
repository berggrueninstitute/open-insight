# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY pdfparser.py pdfparser.py
COPY sampledata/SantaMonica/Minutes/ sampledata/SantaMonica/Minutes/

CMD ["python3", "pdfparser.py"]