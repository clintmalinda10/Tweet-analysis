FROM python:3.7

FROM ubuntu

WORKDIR /usr/src/app

EXPOSE 81/tcp

RUN mkdir /myvol

VOLUME /myvol

RUN apt-get update && apt-get install -y \
	sqlite3 \
	python3-pip*

COPY Twits4.py .
#COPY Stats.py .
COPY requirements.txt .
COPY cred.py .
COPY tweets.db .

RUN pip3 install --no-cache-dir -r requirements.txt

#CMD ["python3","./Stats.py"]

CMD ["python3","./Twits4.py"]
