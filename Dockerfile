FROM python:3.6.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /GetIn
WORKDIR /GetIn
COPY requirements.txt /GetIn/
RUN pip install -r requirements.txt
COPY . /GetIn/