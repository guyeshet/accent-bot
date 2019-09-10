FROM python:3-alpine

WORKDIR /app

# musl-dev provides libc, alpine-sdk provides make
RUN apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev alpine-sdk libressl-dev musl-dev libffi-dev

ADD requirements.txt /app

RUN pip install -r requirements.txt
RUN apk del .build-deps

COPY . /app

#EXPOSE 8006
#CMD ["python", "json_head.py"]