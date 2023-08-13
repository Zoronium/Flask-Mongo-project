FROM python:3.11-alpine

WORKDIR /app

ADD ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt --no-cache 


ENV PORT 5000
ENV FLASK_APP=app
ENV FLASK_DEBUG=0

ADD . /app

EXPOSE 5000

CMD [ "flask"," run"," --host"," 0.0.0.0"," --port ","5000" ]
